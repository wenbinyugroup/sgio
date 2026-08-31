"""Gmsh input writer."""

from __future__ import annotations

from typing import Any, TextIO

import numpy as np

from sgio.core.property_ref_csys import (
    build_property_ref_axis_cell_data,
    resolve_element_local_csys,
)

from . import _gmsh22
from . import _gmsh41
from .keywords import DEFAULT_FORMAT_VERSION


def write_input_payload(file: TextIO, payload: dict[str, Any]) -> None:
    """Write a raw Gmsh payload to a file-like object."""
    format_version = payload.get("format_version") or DEFAULT_FORMAT_VERSION
    mesh = payload["mesh"]
    float_fmt = payload.get("float_fmt", ".16e")
    mesh_only = payload.get("mesh_only", True)
    binary = payload.get("binary", True)

    if format_version == "2.2":
        _gmsh22.write_buffer(file, mesh, float_fmt=float_fmt, binary=binary)
        return

    if format_version == "4.1":
        sgdim = int(payload.get("sgdim", 2))
        _prepare_gmsh41_mesh(mesh, sgdim)
        _gmsh41.write_buffer(
            file,
            mesh,
            float_fmt,
            mesh_only,
            binary,
            mocombos=payload.get("mocombos"),
            material_id_map=payload.get("material_id_map"),
            sg_configs=payload.get("sg_configs"),
            sgdim=sgdim,
        )
        return

    raise ValueError(f"Unsupported Gmsh write version: {format_version}")


def _prepare_gmsh41_mesh(mesh: Any, sgdim: int) -> None:
    """Populate the minimal metadata required by the local Gmsh 4.1 writer."""
    mesh.point_data["gmsh:dim_tags"] = np.array(
        [[sgdim, 1] for _ in range(len(mesh.points))],
        dtype=int,
    )
    mesh.cell_data["gmsh:geometrical"] = [[1]] * len(mesh.cells)

    _normalize_local_coordinate_fields(mesh)
    _normalize_additional_rotation_fields(mesh)


def _normalize_local_coordinate_fields(mesh: Any) -> None:
    """Normalize canonical and legacy local-csys fields before Gmsh writing."""
    cell_csys = resolve_element_local_csys(mesh.cell_data, mesh.cells)
    if cell_csys is None:
        return

    mesh.cell_data["element_local_csys"] = cell_csys
    mesh.cell_data["property_ref_csys"] = [
        np.asarray(block, dtype=float).copy() for block in mesh.cell_data["element_local_csys"]
    ]

    try:
        axis_data = build_property_ref_axis_cell_data(mesh.cell_data["element_local_csys"])
    except (TypeError, ValueError):
        return

    mesh.cell_data.update(axis_data)


def _normalize_additional_rotation_fields(mesh: Any) -> None:
    """Normalize legacy and canonical additional-rotation fields before writing."""
    rotation_1 = mesh.cell_data.get("additional_rotation_1")
    rotation_2 = mesh.cell_data.get("additional_rotation_2")
    rotation_3 = mesh.cell_data.get("additional_rotation_3")
    legacy_rotation = mesh.cell_data.get("additional_rotation")

    if rotation_1 is None and legacy_rotation is not None:
        rotation_1 = [np.asarray(block, dtype=float) for block in legacy_rotation]

    if rotation_1 is None and rotation_2 is None and rotation_3 is None:
        return

    reference_blocks = rotation_1 or rotation_2 or rotation_3
    assert reference_blocks is not None

    def _zeros_like_reference() -> list[np.ndarray]:
        return [np.zeros(len(np.asarray(block)), dtype=float) for block in reference_blocks]

    mesh.cell_data["additional_rotation_1"] = (
        [np.asarray(block, dtype=float) for block in rotation_1]
        if rotation_1 is not None
        else _zeros_like_reference()
    )
    mesh.cell_data["additional_rotation_2"] = (
        [np.asarray(block, dtype=float) for block in rotation_2]
        if rotation_2 is not None
        else _zeros_like_reference()
    )
    mesh.cell_data["additional_rotation_3"] = (
        [np.asarray(block, dtype=float) for block in rotation_3]
        if rotation_3 is not None
        else _zeros_like_reference()
    )
