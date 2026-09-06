"""Abaqus input mapper."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Mapping

import numpy as np
import sgio.model as smdl
from meshio.abaqus._abaqus import abaqus_to_meshio_type

from sgio._vendors.inprw.inpRW import inpRW
from sgio.core.fe_model import FEModel
from sgio.core.mesh import CellBlock, SGMesh
from sgio.core.property_ref_csys import (
    axes_to_property_ref_csys,
    property_ref_csys_to_axes,
)
from sgio.core.section import Orientation, Section
from sgio.core.sg import StructureGene
from .._mesh_convert import parse_model_type

logger = logging.getLogger(__name__)

# Route unmapped Abaqus structural keywords (captured by the parser) to their
# ``FEModel.extras`` fallback keys.
_STRUCTURAL_EXTRAS_KEYS = {
    "boundary": "abaqus_boundary",
    "cload": "abaqus_loads",
    "dload": "abaqus_loads",
    "step": "abaqus_steps",
}

abaqus_to_meshio_type.update({
    "CPE3": "triangle",
    "CPS6M": "triangle6",
    "CPE4": "quad",
    "CPS8": "quad8",
    "CPS8R": "quad8",
    "WARP2D4": "quad",
    "WARPF2D4": "quad",
    "WARPF2D8": "quad8",
    "WARP2D3": "triangle",
    "WARPF2D3": "triangle",
    "WARPF2D6": "triangle6",
})

INPRW_PRINT = logger.getEffectiveLevel() <= logging.DEBUG


@dataclass(frozen=True)
class _AbaqusOrientationDefinition:
    """Normalized Abaqus ``*Orientation`` definition for mapper use."""

    name: str
    coordinates: tuple[float, ...] | None
    distribution: str | None
    rotation_axis: int
    rotation_angle: float


def map_input_to_fe_model(parsed: Mapping[str, Any]) -> FEModel:
    """Map parsed Abaqus payload into a generic ``FEModel``.

    Single source of the Abaqus input semantics: mesh, materials, sections and
    named orientations become first-class ``FEModel`` fields; unmapped
    structural blocks (boundary conditions, loads, steps) are stashed in
    ``FEModel.extras`` as a non-lossy fallback. See the boundary table in
    ``architecture/io.md``.
    """
    sgdim = int(parsed["sgdim"])
    mesh, materials, mocombos, orientations = process_mesh(
        parsed["inprw"], sgdim=sgdim
    )

    fe = FEModel(name="")
    fe.mesh = mesh
    fe.materials = _build_material_models(materials)
    fe.sections = _build_sections(mocombos)
    fe.orientations = _build_orientations(orientations)
    _route_structural_blocks(fe, parsed.get("structural_blocks", {}))
    return fe


def map_input_to_structure_gene(parsed: Mapping[str, Any]) -> StructureGene:
    """Map parsed Abaqus payload into a ``StructureGene``.

    Delegates the FE-level semantics to :func:`map_input_to_fe_model` and wraps
    the result with SG-specific dimensions/analysis config.
    """
    fe = map_input_to_fe_model(parsed)
    sg = StructureGene.from_fe(fe, sgdim=int(parsed["sgdim"]))
    sg.smdim, sg.analysis_config.model = parse_model_type(parsed["model"])
    return sg


def process_mesh(
    inprw: inpRW,
    sgdim: int,
) -> tuple[
    SGMesh,
    dict[str, dict[str, Any]],
    dict[int, tuple[str, float]],
    dict[str, _AbaqusOrientationDefinition],
]:
    """Build SG mesh, raw materials, material combos, and named orientations."""
    points = []
    node_ids = []
    nid2pid = {}
    for node_id, node in inprw.nd.items():
        points.append(list(map(float, node.data[1:])))
        node_ids.append(node_id)
        nid2pid[node_id] = len(points) - 1
    points = np.asarray(points)

    point_data = {"node_id": node_ids}

    cells: list[list[Any]] = []
    cell_types: list[str] = []
    cell_elem_ids: dict[str, list[int]] = {}
    eid2cid: dict[int, tuple[int, int]] = {}
    cell_sets: dict[str, list[int]] = {}
    for elem_block in inprw.findKeyword("element", printOutput=INPRW_PRINT):
        params = elem_block.parameter
        abq_type = params["type"]
        meshio_type = abaqus_to_meshio_type[abq_type]
        try:
            cell_block_index = cell_types.index(meshio_type)
        except ValueError:
            cells.append([meshio_type, []])
            cell_types.append(meshio_type)
            cell_elem_ids[meshio_type] = []
            cell_block_index = len(cell_types) - 1

        set_name = params.get("elset")
        if set_name is not None and set_name not in cell_sets:
            cell_sets[set_name] = []

        for elem_id, elem in elem_block.data.items():
            original_node_ids = list(map(int, elem.data[1:]))
            node_indices = [nid2pid[nid] for nid in original_node_ids]
            cells[cell_block_index][1].append(node_indices)
            cell_elem_ids[meshio_type].append(elem_id)
            eid2cid[elem_id] = (cell_block_index, len(cells[cell_block_index][1]) - 1)
            if set_name is not None:
                cell_sets[set_name].append(elem_id)

    for set_block in inprw.findKeyword("elset", printOutput=INPRW_PRINT):
        params = set_block.parameter
        set_name = params["elset"]._value
        generate = params.get("generate")
        if set_name not in cell_sets:
            cell_sets[set_name] = []

        if generate is not None:
            elem_start, elem_end, elem_increment = set_block.data[0]
            for elem_id in range(elem_start, elem_end + 1, elem_increment):
                cell_sets[set_name].append(elem_id)
        else:
            for row in set_block.data:
                cell_sets[set_name].extend(row)

    distributions: dict[str, dict[int, list[float]]] = {}
    distribution_defaults: dict[str, list[float]] = {}
    for distr_block in inprw.findKeyword("distribution", printOutput=INPRW_PRINT):
        distr_name = str(
            getattr(distr_block.parameter["name"], "_value", distr_block.parameter["name"])
        )
        distributions.setdefault(distr_name, {})
        for row in distr_block.data:
            row_key = row[0]
            coordinates = list(map(float, row[1:]))
            if isinstance(row_key, str) and getattr(row_key, "_value", row_key) == "":
                distribution_defaults[distr_name] = coordinates
            else:
                distributions[distr_name][int(row_key)] = coordinates

    orientations: dict[str, _AbaqusOrientationDefinition] = {}
    for orient_block in inprw.findKeyword("orientation", printOutput=INPRW_PRINT):
        orient_name = str(
            getattr(orient_block.parameter["name"], "_value", orient_block.parameter["name"])
        )
        orientations[orient_name] = _parse_orientation_definition(orient_block, orient_name)

    materials: dict[str, dict[str, Any]] = {}
    for material_block in inprw.findKeyword("material", printOutput=INPRW_PRINT):
        _process_material(material_block, inprw, materials)

    cell_prop_ids: dict[int, list[int]] = {}
    used_materials: list[str] = []
    mocombos: dict[int, tuple[str, float]] = {}
    orientation_element_ids: dict[str, set[int]] = {}

    for section_block in inprw.findKeyword("solid section", printOutput=INPRW_PRINT):
        _process_section(
            section_block,
            materials,
            mocombos,
            cell_sets,
            cell_prop_ids,
            used_materials,
            orientation_element_ids,
        )
    for section_block in inprw.findKeyword("shell section", printOutput=INPRW_PRINT):
        _process_section(
            section_block,
            materials,
            mocombos,
            cell_sets,
            cell_prop_ids,
            used_materials,
            orientation_element_ids,
        )

    cells_tuple = [CellBlock(cell_type, np.asarray(cell_rows, dtype=int)) for cell_type, cell_rows in cells]
    cell_data = {
        "element_id": [cell_elem_ids[cell_type] for cell_type in cell_types],
        "property_id": _init_cell_data_list(cells_tuple, None),
        "property_ref_csys": _init_cell_data_list(cells_tuple, _default_property_ref_csys(sgdim)),
    }

    for prop_id, elem_ids in cell_prop_ids.items():
        for elem_id in elem_ids:
            cell_block_index, cell_index = eid2cid[elem_id]
            cell_data["property_id"][cell_block_index][cell_index] = prop_id

    for orient_name, elem_ids in orientation_element_ids.items():
        if orient_name not in orientations:
            raise ValueError(
                f"Abaqus section references unknown orientation {orient_name!r}."
            )
        orientation = orientations[orient_name]
        if orientation.coordinates is not None:
            coordinates_by_element = {elem_id: orientation.coordinates for elem_id in elem_ids}
        else:
            distribution_name = orientation.distribution
            if distribution_name not in distributions:
                raise ValueError(
                    f"Abaqus orientation {orient_name!r} references unknown distribution "
                    f"{distribution_name!r}."
                )
            coordinates_by_element = {}
            for elem_id in elem_ids:
                coordinates = distributions[distribution_name].get(
                    elem_id,
                    distribution_defaults.get(distribution_name),
                )
                if coordinates is None:
                    raise ValueError(
                        f"Abaqus orientation {orient_name!r} has no coordinates for "
                        f"element {elem_id}."
                    )
                coordinates_by_element[elem_id] = coordinates

        for elem_id, coords in coordinates_by_element.items():
            cell_block_index, cell_index = eid2cid[elem_id]
            cell_data["property_ref_csys"][cell_block_index][cell_index] = (
                _map_orientation_coords_to_property_ref_csys(
                    coords,
                    sgdim,
                    orientation.rotation_axis,
                    orientation.rotation_angle,
                )
            )

    mesh = SGMesh(
        points=points,
        cells=cells_tuple,
        point_data=point_data,
        cell_sets=cell_sets,
        cell_data=cell_data,
    )
    return mesh, materials, mocombos, orientations


def _build_material_models(materials: Mapping[str, Mapping[str, Any]]) -> dict[str, smdl.CauchyContinuumModel]:
    """Convert raw Abaqus material records into SG material models."""
    mapped_materials: dict[str, smdl.CauchyContinuumModel] = {}
    for material_name, material_data in materials.items():
        material_id = material_data["id"]
        if material_id == 0:
            continue

        model = smdl.CauchyContinuumModel(material_name)
        model.temperature = material_data.get("temperature", 0)
        model.density = material_data.get("density", 0)

        material_type = material_data["type"]
        elastic = material_data["elastic"]
        if material_type == "isotropic":
            model.set_isotropy(0)
            model.set_elastic(elastic)
        elif material_type == "engineering constants":
            model.set_isotropy(1)
            e1, e2, e3 = elastic[:3]
            g12, g13, g23 = elastic[6:9]
            nu12, nu13, nu23 = elastic[3:6]
            model.set_elastic(
                [e1, e2, e3, g12, g13, g23, nu12, nu13, nu23],
                input_type="engineering",
            )
        elif material_type == "lamina":
            model.set_isotropy(1)
            e1, e2, e3 = [elastic[0], elastic[1], elastic[1]]
            g12, g13, g23 = [elastic[3], elastic[4], elastic[5]]
            nu12, nu13 = [elastic[2], elastic[2]]
            nu23 = e3 / (2 * g23) - 1
            model.set_elastic(
                [e1, e2, e3, g12, g13, g23, nu12, nu13, nu23],
                input_type="engineering",
            )
        elif material_type == "anisotropic":
            stiffness = [
                [elastic[0], elastic[1], elastic[3], elastic[6], elastic[10], elastic[15]],
                [elastic[1], elastic[2], elastic[4], elastic[7], elastic[11], elastic[16]],
                [elastic[3], elastic[4], elastic[5], elastic[8], elastic[12], elastic[17]],
                [elastic[6], elastic[7], elastic[8], elastic[9], elastic[13], elastic[18]],
                [elastic[10], elastic[11], elastic[12], elastic[13], elastic[14], elastic[19]],
                [elastic[15], elastic[16], elastic[17], elastic[18], elastic[19], elastic[20]],
            ]
            model.set_isotropy(2)
            model.set_elastic(stiffness, input_type="stiffness")

        mapped_materials[material_name] = model
    return mapped_materials


def _build_sections(mocombos: Mapping[int, tuple[str, float]]) -> dict[str, Section]:
    """Convert ``{property_id: (material, angle)}`` combos into named sections.

    Mirrors the ``StructureGene.mocombos`` setter so the FEModel path and the
    legacy SG path produce identical sections.
    """
    return {
        f"section_{int(property_id)}": Section(
            name=f"section_{int(property_id)}",
            material=material,
            orientation=float(angle),
            property_id=int(property_id),
        )
        for property_id, (material, angle) in sorted(mocombos.items())
    }


def _build_orientations(
    orientations: Mapping[str, _AbaqusOrientationDefinition],
) -> dict[str, Orientation]:
    """Promote Abaqus named orientations to first-class ``Orientation`` objects.

    Abaqus orientations are discrete coordinate distributions rather than a
    single angle; the per-element frame is already carried in
    ``cell_data['property_ref_csys']``. Here we preserve the *named* entity and
    its distribution reference so it is not silently lost.
    """
    return {
        name: Orientation(
            name=name,
            angle=definition.rotation_angle,
            extras={
                "source": "abaqus",
                "definition": (
                    "coordinates" if definition.coordinates is not None else "distribution"
                ),
                "axis": definition.rotation_axis,
                **(
                    {"coordinates": list(definition.coordinates)}
                    if definition.coordinates is not None
                    else {"distribution": definition.distribution}
                ),
            },
        )
        for name, definition in orientations.items()
    }


def _route_structural_blocks(
    fe: FEModel,
    structural_blocks: Mapping[str, list[dict[str, Any]]],
) -> None:
    """Stash unmapped structural keyword blocks into ``FEModel.extras``."""
    for keyword, blocks in structural_blocks.items():
        extras_key = _STRUCTURAL_EXTRAS_KEYS.get(keyword)
        if extras_key is None:
            continue
        fe.extras.setdefault(extras_key, []).extend(blocks)


def _init_cell_data_list(cells: list[CellBlock], default_value: Any = None) -> list[list[Any]]:
    """Initialize one cell-data list per cell block."""
    return [[default_value] * len(cell_block.data) for cell_block in cells]


def _default_property_ref_csys(sgdim: int) -> list[float]:
    """Return the Abaqus-frame default property reference coordinate system."""
    if sgdim == 2:
        return [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    return [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]


def _parse_orientation_definition(
    orientation_block: Any,
    orientation_name: str,
) -> _AbaqusOrientationDefinition:
    """Normalize a direct or distributed Abaqus orientation definition."""
    parameters = orientation_block.parameter
    definition = _orientation_parameter_value(parameters, "definition", "COORDINATES")
    system = _orientation_parameter_value(parameters, "system", "RECTANGULAR")
    if definition != "COORDINATES" or system != "RECTANGULAR":
        raise ValueError(
            f"Abaqus orientation {orientation_name!r} supports only "
            f"DEFINITION=COORDINATES with SYSTEM=RECTANGULAR "
            f"(got definition={definition!r}, system={system!r})."
        )
    if "local directions" in parameters or "dispersion" in parameters:
        raise ValueError(
            f"Abaqus orientation {orientation_name!r} with LOCAL DIRECTIONS or DISPERSION "
            "is not supported."
        )

    first_row = orientation_block.data[0]
    first_value = first_row[0]
    rotation_axis = 1
    rotation_angle = 0.0
    if len(orientation_block.data) > 1:
        rotation_axis = int(orientation_block.data[1][0])
        rotation_angle = float(orientation_block.data[1][1])

    if isinstance(first_value, str):
        return _AbaqusOrientationDefinition(
            name=orientation_name,
            coordinates=None,
            distribution=str(getattr(first_value, "_value", first_value)),
            rotation_axis=rotation_axis,
            rotation_angle=rotation_angle,
        )

    coordinates = tuple(float(value) for value in first_row)
    if len(coordinates) not in (6, 9):
        raise ValueError(
            f"Abaqus orientation {orientation_name!r} must contain 6 or 9 direct "
            f"coordinates (got {len(coordinates)})."
        )
    return _AbaqusOrientationDefinition(
        name=orientation_name,
        coordinates=coordinates,
        distribution=None,
        rotation_axis=rotation_axis,
        rotation_angle=rotation_angle,
    )


def _orientation_parameter_value(parameters: Mapping[str, Any], name: str, default: str) -> str:
    """Return one normalized Abaqus orientation keyword parameter."""
    value = parameters.get(name)
    if value is None:
        return default
    return str(getattr(value, "_value", value)).strip().upper()


def _map_orientation_coords_to_property_ref_csys(
    coords: list[float] | tuple[float, ...],
    sgdim: int,
    rotation_axis: int,
    rotation_angle: float,
) -> list[float]:
    """Map one Abaqus orientation record into ``property_ref_csys``.

    Parameters
    ----------
    coords : list of float or tuple of float
        Abaqus ``coord3D, coord3D`` payload, with optional origin ``c``.
    sgdim : int
        Structure-gene dimension.
    rotation_axis : int
        Abaqus local axis for the additional rotation.
    rotation_angle : float
        Abaqus additional rotation in degrees.

    Returns
    -------
    list of float
        Internal 9-value ``(a, b, c)`` representation in the source (Abaqus)
        frame.
    """
    if len(coords) not in (6, 9):
        raise ValueError(
            "Abaqus orientation must contain 6 or 9 values "
            f"(got {len(coords)})."
        )

    point_c = (
        np.zeros(3, dtype=float)
        if len(coords) == 6
        else np.asarray(coords[6:9], dtype=float)
    )
    raw_csys = np.concatenate((np.asarray(coords[:6], dtype=float), point_c))
    axis_y1, axis_y2, axis_y3 = property_ref_csys_to_axes(raw_csys)
    axis_y1, axis_y2, axis_y3 = _rotate_orientation_axes(
        axis_y1,
        axis_y2,
        axis_y3,
        rotation_axis,
        rotation_angle,
    )

    if sgdim == 2:
        if rotation_axis == 1 and rotation_angle != 0.0:
            raise ValueError(
                "Abaqus 2D orientation rotation about local axis 1 is unsupported "
                "because it tilts the section normal."
            )
        if rotation_axis == 2 and rotation_angle != 0.0:
            raise ValueError(
                "Abaqus 2D orientation rotation about local axis 2 requires "
                "section/material combo assignment and is not supported."
            )
        property_csys = axes_to_property_ref_csys(axis_y3, axis_y1, axis_y2)
    else:
        property_csys = axes_to_property_ref_csys(axis_y1, axis_y2, axis_y3)

    return list(_translate_property_ref_csys(property_csys, point_c))


def _rotate_orientation_axes(
    axis_y1: np.ndarray,
    axis_y2: np.ndarray,
    axis_y3: np.ndarray,
    rotation_axis: int,
    rotation_angle: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rotate one right-handed Abaqus local basis about one local axis."""
    if rotation_axis not in (1, 2, 3):
        raise ValueError(
            f"Abaqus orientation rotation axis must be 1, 2, or 3 (got {rotation_axis})."
        )
    if rotation_angle == 0.0:
        return axis_y1, axis_y2, axis_y3

    axes = (axis_y1, axis_y2, axis_y3)
    rotation_vector = axes[rotation_axis - 1]
    angle_rad = np.deg2rad(rotation_angle)
    cross_matrix = np.array(
        [
            [0.0, -rotation_vector[2], rotation_vector[1]],
            [rotation_vector[2], 0.0, -rotation_vector[0]],
            [-rotation_vector[1], rotation_vector[0], 0.0],
        ]
    )
    rotation_matrix = (
        np.eye(3)
        + np.sin(angle_rad) * cross_matrix
        + (1.0 - np.cos(angle_rad)) * (cross_matrix @ cross_matrix)
    )
    return (
        rotation_matrix @ axis_y1,
        rotation_matrix @ axis_y2,
        rotation_matrix @ axis_y3,
    )


def _translate_property_ref_csys(csys: np.ndarray, point_c: np.ndarray) -> np.ndarray:
    """Translate a canonical origin-zero coordinate system to ``point_c``."""
    return (np.asarray(csys, dtype=float).reshape(3, 3) + point_c).reshape(-1)


def _process_material(material_block: Any, inprw: inpRW, materials: dict[str, dict[str, Any]]) -> None:
    """Extract one Abaqus ``*Material`` block into a raw material record."""
    name = material_block.parameter["name"]._value
    density = inprw.findKeyword("density", parentBlock=material_block, printOutput=INPRW_PRINT)
    density_value = float(density[0].data[0][0]) if density else 0.0

    elastic = inprw.findKeyword("elastic", parentBlock=material_block, printOutput=INPRW_PRINT)
    try:
        elastic_type = elastic[0].parameter["type"]._value.lower()
    except KeyError:
        elastic_type = "isotropic"

    elastic_constants = []
    for row in elastic[0].data:
        for value in row:
            if str(value).strip() == "":
                # Abaqus data lines are comma-terminated; the trailing comma
                # on the last populated line produces one blank cell.
                continue
            try:
                elastic_constants.append(float(value))
            except ValueError as exc:
                raise ValueError(
                    f"Invalid elastic constant {value!r} for material {name!r} "
                    f"in '*Elastic' data."
                ) from exc

    materials[name] = {
        "id": 0,
        "density": density_value,
        "type": elastic_type,
        "elastic": list(map(float, elastic_constants)),
    }


def _process_section(
    section_block: Any,
    materials: dict[str, dict[str, Any]],
    mocombos: dict[int, tuple[str, float]],
    cell_sets: Mapping[str, list[int]],
    cell_prop_ids: dict[int, list[int]],
    used_materials: list[str],
    orientation_element_ids: dict[str, set[int]],
) -> None:
    """Extract one Abaqus section block into property/material assignments."""
    params = section_block.parameter
    elset_name = params.get("elset")

    material_name = params.get("material")
    if material_name is None and "composite" in params:
        material_name = section_block.data[0][2]
    material_name = material_name._value

    orient_name = params.get("orientation")
    if orient_name is not None:
        orientation_name = str(getattr(orient_name, "_value", orient_name))
        orientation_element_ids.setdefault(orientation_name, set()).update(cell_sets[elset_name])

    angle = 0.0
    try:
        if "composite" in params:
            angle_token = section_block.data[0][-2]
        else:
            angle_token = section_block.data[-2]
    except IndexError:
        # No angle column/row present at all: an ordinary section without a
        # layup angle. 0 degrees is Abaqus's own implicit default.
        angle_token = None
    if angle_token is not None:
        try:
            angle = float(angle_token)
        except ValueError as exc:
            raise ValueError(
                f"Invalid section orientation angle {angle_token!r} for "
                f"elset {elset_name!r} in '*Solid Section'/'*Shell Section' data."
            ) from exc

    if material_name not in used_materials:
        used_materials.append(material_name)
        materials[material_name]["id"] = len(used_materials)

    prop_id = 0
    for existing_prop_id, combo in mocombos.items():
        if combo[0] == material_name and combo[1] == angle:
            prop_id = existing_prop_id
            break

    if prop_id == 0:
        prop_id = len(mocombos) + 1
        mocombos[prop_id] = (material_name, angle)
        cell_prop_ids[prop_id] = []

    cell_prop_ids[prop_id].extend(cell_sets[elset_name])
