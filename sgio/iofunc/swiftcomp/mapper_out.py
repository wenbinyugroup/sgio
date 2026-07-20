"""SwiftComp output mapper."""

from __future__ import annotations

import copy
from typing import Any

import sgio.model as smdl
from sgio.core.sg import StructureGene

from ..common import build_material_id_map
from .keywords import resolve_model_dimension


def map_structure_gene_to_write_payload(
    sg: StructureGene,
    analysis: str = "h",
    model: int | str = "sd1",
    model_space: str = "xy",
    prop_ref_y: str = "x",
    macro_responses: list[smdl.StateCase] | None = None,
    load_type: int = 0,
    sfi: str = "8d",
    sff: str = "20.12e",
    version: str | None = None,
) -> dict[str, Any]:
    """Map a ``StructureGene`` into a raw SwiftComp writer payload."""
    macro_responses = [] if macro_responses is None else macro_responses
    sg_for_write = copy.copy(sg)
    sg_for_write.smdim = resolve_model_dimension(model)

    if analysis == "h":
        material_id_map = build_material_id_map(
            sg_for_write.materials, sg_for_write.fe_model.material_source_ids, "swiftcomp"
        )
        return {
            "mode": "homogenization",
            "sg": sg_for_write,
            "version": version,
            "physics": sg_for_write.analysis_config.physics,
            "model_space": model_space,
            "prop_ref_y": prop_ref_y,
            "material_id_map": material_id_map,
            "material_combos": _build_material_combo_records(sg_for_write, material_id_map),
            "materials": sg_for_write.materials,
            "omega": sg_for_write.omega,
            "sfi": sfi,
            "sff": sff,
        }

    return {
        "mode": "global",
        "analysis": analysis,
        "model": model,
        "physics": sg.analysis_config.physics,
        "load_type": load_type,
        "macro_responses": macro_responses,
        "materials": sg.materials if sg is not None else {},
        "sfi": sfi,
        "sff": sff,
    }


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
