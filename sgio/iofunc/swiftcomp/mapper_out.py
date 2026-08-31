"""SwiftComp output mapper."""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

import sgio.model as smdl
from sgio.core.mesh import SGMesh
from sgio.core.property_ref_csys import project_property_ref_csys
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
    sg_for_write._fe = copy.copy(sg.fe_model)
    sg_for_write.smdim = resolve_model_dimension(model)

    if analysis == "h":
        sg_for_write.mesh = _build_swiftcomp_export_mesh(sg.mesh, sg.sgdim, model_space)
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


def _build_swiftcomp_export_mesh(
    mesh: SGMesh | None,
    sgdim: int | None,
    model_space: str,
) -> SGMesh:
    """Create the private mesh consumed by the mutating SwiftComp writer."""
    if mesh is None:
        raise ValueError("StructureGene.mesh is required for SwiftComp export.")

    point_data = {
        name: np.asarray(values).copy() for name, values in mesh.point_data.items()
    }
    cell_data = {
        name: [np.asarray(block).copy() for block in blocks]
        for name, blocks in mesh.cell_data.items()
    }
    if sgdim == 2 and "property_ref_csys" in cell_data:
        cell_data["property_ref_csys"] = [
            np.asarray(
                [project_property_ref_csys(csys, model_space) for csys in block],
                dtype=float,
            )
            for block in cell_data["property_ref_csys"]
        ]

    return SGMesh(
        points=mesh.points,
        cells=mesh.cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=mesh.field_data.copy(),
        point_sets=mesh.point_sets.copy(),
        cell_sets=mesh.cell_sets.copy(),
        gmsh_periodic=mesh.gmsh_periodic,
        info=mesh.info,
        cell_point_data={
            name: [np.asarray(block).copy() for block in blocks]
            for name, blocks in mesh.cell_point_data.items()
        },
    )


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
