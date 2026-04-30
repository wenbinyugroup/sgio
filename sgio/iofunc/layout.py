"""Utilities for merging section data by spanwise layout."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any, Iterable

import meshio
import numpy as np
from meshio import CellBlock, Mesh

from sgio.core import StructureGene
from sgio.core.mesh import SGMesh, get_cell_data_arrays, merge_field_data
from sgio.iofunc.gmsh._common import build_geometrical_tags
from sgio.iofunc.utils import infer_section_dimension, resolve_section_path

SectionLayout = list[tuple[float, str]]
SGIO_INPUT_FORMATS = {"abaqus", "gmsh", "sc", "swiftcomp", "vabs"}
SG_ANALYSIS_FORMATS = {"sc", "swiftcomp", "vabs"}

logger = logging.getLogger(__name__)


def read_section_layout_csv(
    csv_file: str | Path,
    location_column: str = "location",
    section_column: str = "cs",
    encoding: str = "utf-8-sig",
) -> SectionLayout:
    """Read a cross-section layout CSV file."""
    layout: SectionLayout = []
    csv_path = Path(csv_file)
    logger.info("Reading section layout CSV: %s", csv_path)

    with csv_path.open("r", newline="", encoding=encoding) as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []

        if location_column not in fieldnames:
            raise ValueError(
                f"Column '{location_column}' not found in layout CSV: {csv_path}"
            )
        if section_column not in fieldnames:
            raise ValueError(
                f"Column '{section_column}' not found in layout CSV: {csv_path}"
            )

        for row in reader:
            layout.append((float(row[location_column]), row[section_column].strip()))

    logger.info("Loaded %d layout rows from %s", len(layout), csv_path)
    return layout


def merge_sections(
    layout: Iterable[tuple[float, str]],
    section_dir: str | Path,
    file_extension: str | None = None,
    axis: int = 0,
    input_format: str = "vabs",
    **read_kwargs: Any,
) -> SGMesh:
    """Merge multiple section files according to a blade layout."""
    from .main import read

    layout = list(layout)
    root = Path(section_dir)
    input_format = input_format.lower()
    logger.info(
        "Merging %d sections from %s with input_format=%s axis=%d",
        len(layout),
        root,
        input_format,
        axis,
    )
    merged_points: list[np.ndarray] = []
    merged_cells: list[CellBlock] = []
    merged_field_data: dict[str, np.ndarray] = {}
    merged_physical: list[np.ndarray] = []
    merged_geometrical: list[np.ndarray] = []
    used_geometrical_tags: set[int] = set()
    point_offset = 0

    for index, (location, section_name) in enumerate(layout, start=1):
        section_path = resolve_section_path(
            section_name=section_name,
            section_dir=root,
            file_extension=file_extension,
            input_format=input_format,
        )
        logger.info(
            "Reading section %d/%d: %s from %s at location=%s",
            index,
            len(layout),
            section_name,
            section_path,
            location,
        )

        if input_format in SGIO_INPUT_FORMATS:
            sg = read(str(section_path), file_format=input_format, **read_kwargs)
            mesh = _convert_mesh_to_visualization_mesh(sg.mesh)
            if input_format != "gmsh":
                mesh.field_data = _build_field_data_from_structure_gene(sg)
        else:
            mesh = _convert_mesh_to_visualization_mesh(
                meshio.read(section_path, file_format=input_format)
            )

        logger.info(
            "Merged section %d/%d: points=%d cell_blocks=%d",
            index,
            len(layout),
            len(mesh.points),
            len(mesh.cells),
        )

        shifted_points = np.asarray(mesh.points, dtype=float).copy()
        shifted_points[:, axis] += float(location)
        merged_points.append(shifted_points)

        for cell_block in mesh.cells:
            merged_cells.append(
                CellBlock(cell_block.type, np.asarray(cell_block.data, dtype=int) + point_offset)
            )

        physical_data = get_cell_data_arrays(mesh, "gmsh:physical", 0)
        geometrical_data = get_cell_data_arrays(mesh, "gmsh:geometrical", 0)
        merged_physical.extend(physical_data)
        merged_geometrical.extend(_remap_geometrical_tags(geometrical_data, used_geometrical_tags))
        merge_field_data(merged_field_data, mesh.field_data)
        point_offset += len(mesh.points)

    points = (
        np.concatenate(merged_points, axis=0)
        if merged_points
        else np.empty((0, 3), dtype=float)
    )

    merged_mesh = SGMesh(
        points=points,
        cells=merged_cells,
        cell_data={
            "gmsh:physical": merged_physical,
            "gmsh:geometrical": merged_geometrical,
            "property_id": [array.copy() for array in merged_physical],
        },
        field_data=merged_field_data,
    )
    logger.info(
        "Completed merge: total_points=%d total_cell_blocks=%d",
        len(merged_mesh.points),
        len(merged_mesh.cells),
    )
    return merged_mesh


def merge_sections_from_csv(
    csv_file: str | Path,
    section_dir: str | Path,
    output_file: str | Path | None = None,
    output_format: str = "gmsh22",
    file_extension: str | None = None,
    axis: int = 0,
    input_format: str = "vabs",
    location_column: str = "location",
    section_column: str = "cs",
    encoding: str = "utf-8-sig",
    **read_kwargs: Any,
) -> SGMesh:
    """Merge section files using a layout CSV file."""
    logger.info("Starting merge from layout file: %s", csv_file)
    merged_mesh = merge_sections(
        layout=read_section_layout_csv(
            csv_file=csv_file,
            location_column=location_column,
            section_column=section_column,
            encoding=encoding,
        ),
        section_dir=section_dir,
        file_extension=file_extension,
        axis=axis,
        input_format=input_format,
        **read_kwargs,
    )

    if output_file is not None:
        write_merged_sections(
            merged_mesh=merged_mesh,
            output_file=output_file,
            output_format=output_format,
        )

    logger.info("Finished merge from layout file: %s", csv_file)
    return merged_mesh


def write_merged_sections(
    merged_mesh: Mesh,
    output_file: str | Path,
    output_format: str = "gmsh22",
    **write_kwargs: Any,
) -> str:
    """Write a merged section mesh."""
    from .main import _mesh_to_sg, write

    output_path = str(output_file)
    logger.info("Writing merged sections to %s with output_format=%s", output_path, output_format)
    normalized_output_format = output_format.lower()

    if normalized_output_format.startswith("gmsh"):
        sgdim = write_kwargs.pop("sgdim", None)
        if sgdim is None:
            sgdim = merged_mesh.cells[0].dim if merged_mesh.cells else 2

        format_version = write_kwargs.pop("format_version", "")
        if normalized_output_format == "gmsh22":
            format_version = "2.2"
        elif normalized_output_format == "gmsh41":
            format_version = "4.1"

        binary = write_kwargs.pop("binary", False)
        sg = _mesh_to_sg(merged_mesh, sgdim=sgdim, model_type=write_kwargs.get("model_type", "SD1"))
        written = write(
            sg=sg,
            filename=output_path,
            file_format="gmsh",
            format_version=format_version,
            binary=binary,
            **write_kwargs,
        )
        logger.info("Wrote merged sections to %s", written)
        return written

    if normalized_output_format in SG_ANALYSIS_FORMATS:
        model_type = write_kwargs.get("model_type", "SD1")
        sgdim = write_kwargs.pop("sgdim", None)
        if sgdim is None:
            sgdim = merged_mesh.cells[0].dim if merged_mesh.cells else 2
        if "model_space" not in write_kwargs:
            if sgdim == 1:
                write_kwargs["model_space"] = "x"
            elif sgdim == 2:
                write_kwargs["model_space"] = "xy"
        sg = _mesh_to_sg(merged_mesh, sgdim=sgdim, model_type=model_type)
        written = write(sg=sg, filename=output_path, file_format=output_format, **write_kwargs)
        logger.info("Wrote merged sections to %s", written)
        return written

    meshio.write(output_file, merged_mesh, file_format=output_format, **write_kwargs)
    logger.info("Wrote merged sections to %s", output_path)
    return output_path


def _convert_mesh_to_visualization_mesh(mesh: Mesh | None) -> SGMesh:
    """Normalize a generic mesh to visualization conventions."""
    if mesh is None:
        raise ValueError("Section mesh is None")

    property_id = get_cell_data_arrays(mesh, "property_id", 0)
    if "gmsh:physical" in mesh.cell_data:
        gmsh_physical = get_cell_data_arrays(mesh, "gmsh:physical", 0)
        property_id = [array.copy() for array in gmsh_physical]
    else:
        gmsh_physical = [array.copy() for array in property_id]

    if "gmsh:geometrical" in mesh.cell_data:
        gmsh_geometrical = get_cell_data_arrays(mesh, "gmsh:geometrical", 0)
    else:
        gmsh_geometrical = build_geometrical_tags(mesh, property_id)

    return SGMesh(
        points=np.asarray(mesh.points, dtype=float).copy(),
        cells=[
            CellBlock(cell_block.type, np.asarray(cell_block.data, dtype=int).copy())
            for cell_block in mesh.cells
        ],
        point_data={
            name: np.asarray(values).copy()
            for name, values in getattr(mesh, "point_data", {}).items()
        },
        cell_data={
            **dict(mesh.cell_data),
            "gmsh:physical": gmsh_physical,
            "gmsh:geometrical": gmsh_geometrical,
            "property_id": [array.copy() for array in property_id],
        },
        field_data={
            name: np.asarray(values).copy()
            for name, values in getattr(mesh, "field_data", {}).items()
        },
        cell_point_data=getattr(mesh, "cell_point_data", None),
    )


def _build_field_data_from_structure_gene(sg: StructureGene) -> dict[str, np.ndarray]:
    """Build field-data metadata from SG layer definitions."""
    field_data: dict[str, np.ndarray] = {}
    sgdim = infer_section_dimension(sg)

    if sg.mocombos:
        for property_id in sorted(sg.mocombos):
            field_data[f"layer_{property_id}"] = np.array([property_id, sgdim], dtype=int)
        return field_data

    if sg.mesh is None:
        return field_data

    for prop_id in sorted(
        {
            int(value)
            for array in get_cell_data_arrays(sg.mesh, "property_id", 0)
            for value in np.asarray(array, dtype=np.int32).ravel()
            if int(value) != 0
        }
    ):
        field_data[f"layer_{prop_id}"] = np.array([prop_id, sgdim], dtype=int)

    return field_data


def _remap_geometrical_tags(
    geometrical_data: list[np.ndarray],
    used_tags: set[int],
) -> list[np.ndarray]:
    """Remap geometrical tags to avoid collisions."""
    unique_tags = sorted(
        {
            int(tag)
            for array in geometrical_data
            for tag in np.asarray(array, dtype=np.int32).ravel()
            if int(tag) != 0
        }
    )

    tag_map: dict[int, int] = {}
    next_tag = max(used_tags, default=0) + 1
    for tag in unique_tags:
        if tag not in used_tags:
            tag_map[tag] = tag
            used_tags.add(tag)
            next_tag = max(next_tag, tag + 1)
        else:
            while next_tag in used_tags:
                next_tag += 1
            tag_map[tag] = next_tag
            used_tags.add(next_tag)
            next_tag += 1

    remapped_arrays = []
    for array in geometrical_data:
        remapped = np.asarray(array, dtype=np.int32).copy()
        if np.any(remapped != 0):
            remapped[remapped != 0] = np.array(
                [tag_map[int(tag)] for tag in remapped[remapped != 0]],
                dtype=np.int32,
            )
        remapped_arrays.append(remapped)

    return remapped_arrays
