"""VABS output mapper.

This module maps application-layer IR objects into raw payloads suitable for
the VABS writer layer.
"""

from __future__ import annotations

from typing import Any

import sgio.model as smdl
from sgio.core.sg import StructureGene

from ..common import build_material_id_map


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

        material_id_map = build_material_id_map(sg.materials)
        material_combos = _build_material_combo_records(sg, material_id_map)
        curve_flag, initial_curvatures = _build_curvature_payload(sg)
        oblique_flag = int((sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0))

        return {
            "mode": "homogenization",
            "version": version,
            "sg_fmt": sg_fmt,
            "mesh": sg.mesh,
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
                "nnode": sg.nnodes,
                "nelem": sg.nelems,
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
        records.append(
            {
                "combo_id": int(combo_id),
                "material_id": int(material_id_map[material_name]),
                "angle": float(angle),
            }
        )
    return records
