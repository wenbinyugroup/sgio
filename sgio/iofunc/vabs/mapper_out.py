"""VABS output mapper.

This module maps application-layer IR objects into raw payloads suitable for
the VABS writer layer.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import sgio.model as smdl
from sgio.core.mesh import CellBlock, SGMesh
from sgio.core.sg import StructureGene

from ..common import build_material_id_map


VABS_SUPPORTED_CELL_TYPES = frozenset(
    {"triangle", "triangle6", "quad", "quad8", "quad9"}
)


def map_structure_gene_to_write_payload(
    sg: StructureGene | None,
    analysis: str = "h",
    sg_fmt: int = 1,
    model: int = 0,
    model_space: str = "",
    prop_ref_y: str = "x",
    macro_responses: list[smdl.StateCase] | None = None,
    sfi: str = "8d",
    sff: str = "20.12e",
    version: str | None = None,
) -> dict[str, Any]:
    """Map a ``StructureGene`` into a raw VABS writer payload."""
    macro_responses = [] if macro_responses is None else macro_responses
    analysis_flags = _derive_analysis_flags(sg, model)

    if analysis == "h":
        if sg is None:
            raise ValueError("StructureGene is required for VABS homogenization input.")

        export_mesh = _build_vabs_export_mesh(sg.mesh)
        material_id_map = build_material_id_map(sg.materials)
        material_combos = _build_material_combo_records(sg, material_id_map)
        curve_flag, initial_curvatures = _build_curvature_payload(sg)
        oblique_flag = int((sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0))

        return {
            "mode": "homogenization",
            "version": version,
            "sg_fmt": sg_fmt,
            "mesh": export_mesh,
            "materials": sg.materials,
            "material_combos": material_combos,
            "material_id_map": material_id_map,
            "model_space": model_space,
            "prop_ref_y": prop_ref_y,
            "sfi": sfi,
            "sff": sff,
            "header": {
                "format_flag": sg_fmt,
                "nlayer": len(material_combos),
                "timoshenko_flag": analysis_flags["timoshenko_flag"],
                "damping_flag": sg.analysis_config.do_damping,
                "thermal_flag": analysis_flags["thermal_flag"],
                "curve_flag": curve_flag,
                "oblique_flag": oblique_flag,
                "trapeze_flag": analysis_flags["trapeze_flag"],
                "vlasov_flag": analysis_flags["vlasov_flag"],
                "initial_curvatures": initial_curvatures,
                "obliqueness": sg.oblique,
                "nnode": len(export_mesh.points),
                "nelem": sum(
                    len(cell_block.data) for cell_block in export_mesh.cells
                ),
                "nmate": sg.nmates,
            },
        }

    materials = {} if sg is None else sg.materials
    return {
        "mode": "global",
        "analysis": analysis,
        "model": analysis_flags["timoshenko_flag"],
        "macro_responses": macro_responses,
        "materials": materials,
        "sfi": sfi,
        "sff": sff,
    }


def _derive_analysis_flags(sg: StructureGene | None, model: int) -> dict[str, int]:
    """Derive VABS analysis flags from SG analysis config."""
    if sg is None:
        return {
            "timoshenko_flag": model,
            "trapeze_flag": 0,
            "vlasov_flag": 0,
            "thermal_flag": 0,
        }

    timoshenko_flag = 0
    trapeze_flag = 0
    vlasov_flag = 0
    if sg.analysis_config.model == 1:
        timoshenko_flag = 1
    elif sg.analysis_config.model == 2:
        timoshenko_flag = 1
        vlasov_flag = 1
    elif sg.analysis_config.model == 3:
        trapeze_flag = 1

    thermal_flag = 3 if sg.analysis_config.physics == 1 else 0
    return {
        "timoshenko_flag": timoshenko_flag,
        "trapeze_flag": trapeze_flag,
        "vlasov_flag": vlasov_flag,
        "thermal_flag": thermal_flag,
    }


def _build_curvature_payload(sg: StructureGene) -> tuple[int, list[float]]:
    """Build VABS curvature payload from SG geometry fields."""
    initial_curvatures = [sg.initial_twist] + sg.initial_curvature
    curve_flag = int(any(value != 0.0 for value in initial_curvatures))
    return curve_flag, initial_curvatures


def _build_material_combo_records(
    sg: StructureGene,
    material_id_map: dict[str, int],
) -> list[dict[str, float | int]]:
    """Convert SG material-orientation combinations to raw writer records."""
    records: list[dict[str, float | int]] = []
    for combo_id, (material_name, angle) in sg.mocombos.items():
        resolved_material_name = _resolve_combo_material_name(
            sg,
            combo_id=int(combo_id),
            material_name=material_name,
            material_id_map=material_id_map,
        )
        records.append(
            {
                "combo_id": int(combo_id),
                "material_id": int(material_id_map[resolved_material_name]),
                "angle": float(angle),
            }
        )
    return records


def _resolve_combo_material_name(
    sg: StructureGene,
    combo_id: int,
    material_name: str,
    material_id_map: dict[str, int],
) -> str:
    """Resolve one combo material name against the current material table.

    Parameters
    ----------
    sg : StructureGene
        Structure gene being written.
    combo_id : int
        Property/combo identifier.
    material_name : str
        Material name stored in ``sg.mocombos``.
    material_id_map : dict[str, int]
        Export material-ID mapping built from ``sg.materials``.

    Returns
    -------
    str
        Material name that exists in ``material_id_map``.

    Raises
    ------
    KeyError
        If the combo material cannot be resolved against current materials.
    """
    if material_name in material_id_map:
        return material_name

    fallback_name = _resolve_material_name_from_mesh_field_data(sg, combo_id)
    if fallback_name is not None and fallback_name in material_id_map:
        return fallback_name

    raise KeyError(
        f"Material combo {combo_id} references unknown material {material_name!r}. "
        f"Available materials: {sorted(material_id_map)}."
    )


def _resolve_material_name_from_mesh_field_data(
    sg: StructureGene,
    combo_id: int,
) -> str | None:
    """Resolve a combo material name from mesh ``field_data``.

    Parameters
    ----------
    sg : StructureGene
        Structure gene being written.
    combo_id : int
        Property/combo identifier.

    Returns
    -------
    str or None
        Material/physical-group name if a matching field-data entry exists.
    """
    mesh = sg.mesh
    if mesh is None or not getattr(mesh, "field_data", None):
        return None

    fallback_name: str | None = None
    for name, values in mesh.field_data.items():
        array = np.asarray(values, dtype=int).reshape(-1)
        if array.size < 2:
            continue
        physical_id, dimension = int(array[0]), int(array[1])
        if physical_id != combo_id:
            continue
        if sg.sgdim is None or dimension == int(sg.sgdim):
            return name
        if fallback_name is None:
            fallback_name = name

    return fallback_name


def _build_vabs_export_mesh(mesh: SGMesh | None) -> SGMesh:
    """Create a VABS-compatible mesh containing only supported section cells."""
    if mesh is None:
        raise ValueError("StructureGene.mesh is required for VABS export.")

    supported_indices = [
        index for index, cell_block in enumerate(mesh.cells)
        if cell_block.type in VABS_SUPPORTED_CELL_TYPES
    ]
    if not supported_indices:
        raise ValueError(
            "VABS export requires supported section cells "
            f"{sorted(VABS_SUPPORTED_CELL_TYPES)}."
        )

    used_point_ids = np.unique(
        np.concatenate(
            [
                np.asarray(mesh.cells[index].data, dtype=int).reshape(-1)
                for index in supported_indices
            ]
        )
    )
    old_to_new = np.full(len(mesh.points), -1, dtype=int)
    old_to_new[used_point_ids] = np.arange(len(used_point_ids), dtype=int)

    cells = [
        CellBlock(
            mesh.cells[index].type,
            old_to_new[np.asarray(mesh.cells[index].data, dtype=int)],
        )
        for index in supported_indices
    ]
    point_data = {
        name: np.asarray(values)[used_point_ids].copy()
        for name, values in mesh.point_data.items()
    }
    cell_data = {
        name: [np.asarray(values[index]).copy() for index in supported_indices]
        for name, values in mesh.cell_data.items()
    }
    field_data = {
        name: np.asarray(values).copy()
        for name, values in mesh.field_data.items()
    }
    cell_point_data = {
        name: [np.asarray(values[index]).copy() for index in supported_indices]
        for name, values in getattr(mesh, "cell_point_data", {}).items()
    }

    return SGMesh(
        points=np.asarray(mesh.points, dtype=float)[used_point_ids].copy(),
        cells=cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        cell_point_data=cell_point_data,
    )
