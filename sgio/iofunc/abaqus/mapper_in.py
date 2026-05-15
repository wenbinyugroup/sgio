"""Abaqus input mapper."""

from __future__ import annotations

import logging
from typing import Any, Mapping

import numpy as np
import sgio.model as smdl
from meshio.abaqus._abaqus import abaqus_to_meshio_type

from sgio._vendors.inprw.inpRW import inpRW
from sgio.core.mesh import CellBlock, SGMesh
from sgio.core.sg import StructureGene
from .._mesh_convert import parse_model_type

logger = logging.getLogger(__name__)

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


def map_input_to_structure_gene(parsed: Mapping[str, Any]) -> StructureGene:
    """Map parsed Abaqus payload into a ``StructureGene``."""
    sg = StructureGene()
    sg.sgdim = int(parsed["sgdim"])
    sg.smdim, sg.analysis_config.model = parse_model_type(parsed["model"])

    mesh, materials, mocombos = process_mesh(parsed["inprw"])
    sg.mesh = mesh
    sg.materials = _build_material_models(materials)
    sg.mocombos = mocombos
    return sg


def process_mesh(inprw: inpRW) -> tuple[SGMesh, dict[str, dict[str, Any]], dict[int, tuple[str, float]]]:
    """Build SG mesh, raw materials, and material combos from ``inpRW`` data."""
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
    for distr_block in inprw.findKeyword("distribution", printOutput=INPRW_PRINT):
        distr_name = distr_block.parameter["name"]._value
        distributions.setdefault(distr_name, {})
        for row_index in range(1, len(distr_block.data)):
            elem_id = distr_block.data[row_index][0]
            distributions[distr_name][elem_id] = list(map(float, distr_block.data[row_index][1:]))

    orientations: dict[str, str] = {}
    for orient_block in inprw.findKeyword("orientation", printOutput=INPRW_PRINT):
        orient_name = orient_block.parameter["name"]._value
        orientations[orient_name] = orient_block.data[0][0]._value

    materials: dict[str, dict[str, Any]] = {}
    for material_block in inprw.findKeyword("material", printOutput=INPRW_PRINT):
        _process_material(material_block, inprw, materials)

    cell_prop_ids: dict[int, list[int]] = {}
    used_materials: list[str] = []
    mocombos: dict[int, tuple[str, float]] = {}
    used_orientations: list[str] = []

    for section_block in inprw.findKeyword("solid section", printOutput=INPRW_PRINT):
        _process_section(
            section_block,
            materials,
            mocombos,
            cell_sets,
            cell_prop_ids,
            used_materials,
            used_orientations,
        )
    for section_block in inprw.findKeyword("shell section", printOutput=INPRW_PRINT):
        _process_section(
            section_block,
            materials,
            mocombos,
            cell_sets,
            cell_prop_ids,
            used_materials,
            used_orientations,
        )

    cells_tuple = [CellBlock(cell_type, np.asarray(cell_rows, dtype=int)) for cell_type, cell_rows in cells]
    cell_data = {
        "element_id": [cell_elem_ids[cell_type] for cell_type in cell_types],
        "property_id": _init_cell_data_list(cells_tuple, None),
        "property_ref_csys": _init_cell_data_list(
            cells_tuple,
            [1, 0, 0, 0, 1, 0, 0, 0, 0],
        ),
    }

    for prop_id, elem_ids in cell_prop_ids.items():
        for elem_id in elem_ids:
            cell_block_index, cell_index = eid2cid[elem_id]
            cell_data["property_id"][cell_block_index][cell_index] = prop_id

    for orient_name in used_orientations:
        distribution_name = orientations[orient_name]
        for elem_id, coords in distributions[distribution_name].items():
            cell_block_index, cell_index = eid2cid[elem_id]
            cell_data["property_ref_csys"][cell_block_index][cell_index] = coords + [0, 0, 0]

    mesh = SGMesh(
        points=points,
        cells=cells_tuple,
        point_data=point_data,
        cell_sets=cell_sets,
        cell_data=cell_data,
    )
    return mesh, materials, mocombos


def _build_material_models(materials: Mapping[str, Mapping[str, Any]]) -> dict[str, smdl.CauchyContinuumModel]:
    """Convert raw Abaqus material records into SG material models."""
    mapped_materials: dict[str, smdl.CauchyContinuumModel] = {}
    for material_name, material_data in materials.items():
        material_id = material_data["id"]
        if material_id == 0:
            continue

        model = smdl.CauchyContinuumModel(material_name)
        model.temperature = material_data.get("temperature", 0)
        model.set("density", material_data.get("density", 0))

        material_type = material_data["type"]
        elastic = material_data["elastic"]
        if material_type == "isotropic":
            model.set("isotropy", 0)
            model.set("elastic", elastic)
        elif material_type == "engineering constants":
            model.set("isotropy", 1)
            e1, e2, e3 = elastic[:3]
            g12, g13, g23 = elastic[6:9]
            nu12, nu13, nu23 = elastic[3:6]
            model.set(
                "elastic",
                [e1, e2, e3, g12, g13, g23, nu12, nu13, nu23],
                input_type="engineering",
            )
        elif material_type == "lamina":
            model.set("isotropy", 1)
            e1, e2, e3 = [elastic[0], elastic[1], elastic[1]]
            g12, g13, g23 = [elastic[3], elastic[4], elastic[5]]
            nu12, nu13 = [elastic[2], elastic[2]]
            nu23 = e3 / (2 * g23) - 1
            model.set(
                "elastic",
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
            model.set("isotropy", 2)
            model.set("elastic", stiffness, input_type="stiffness")

        mapped_materials[material_name] = model
    return mapped_materials


def _init_cell_data_list(cells: list[CellBlock], default_value: Any = None) -> list[list[Any]]:
    """Initialize one cell-data list per cell block."""
    return [[default_value] * len(cell_block.data) for cell_block in cells]


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
            try:
                elastic_constants.append(float(value))
            except ValueError:
                continue

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
    used_orientations: list[str],
) -> None:
    """Extract one Abaqus section block into property/material assignments."""
    params = section_block.parameter
    elset_name = params.get("elset")

    material_name = params.get("material")
    if material_name is None and "composite" in params:
        material_name = section_block.data[0][2]
    material_name = material_name._value

    orient_name = params.get("orientation")
    if orient_name is not None and orient_name._value not in used_orientations:
        used_orientations.append(orient_name._value)

    angle = 0.0
    try:
        if "composite" in params:
            angle = float(section_block.data[0][-2])
        else:
            angle = float(section_block.data[-2])
    except (ValueError, IndexError):
        angle = 0.0

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
