"""Gmsh output mapper."""

from __future__ import annotations

from typing import Any

from sgio.core.sg import StructureGene

from ..common import build_material_id_map
from ..utils.section_files import infer_section_dimension


def map_model_to_write_payload(
    model_obj: Any,
    format_version: str = "4.1",
    float_fmt: str = ".16e",
    sgdim: int | None = None,
    mesh_only: bool = True,
    binary: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """Map a mesh or ``StructureGene`` into a raw Gmsh writer payload."""
    payload: dict[str, Any] = {
        "format_version": format_version,
        "float_fmt": float_fmt,
        "mesh_only": mesh_only,
        "binary": binary,
        **kwargs,
    }

    if not isinstance(model_obj, StructureGene):
        payload.setdefault("sgdim", sgdim if sgdim is not None else 2)
        payload["mesh"] = model_obj
        return payload

    sg = model_obj
    resolved_sgdim = sgdim if sgdim is not None else infer_section_dimension(sg)
    material_id_map = build_material_id_map(sg.materials) if sg.mocombos else {}
    sg_configs = {"sgdim": resolved_sgdim}
    if sg.smdim is not None:
        sg_configs["model"] = sg.analysis_config.model
    sg_configs["do_damping"] = sg.analysis_config.do_damping
    sg_configs["thermal"] = sg.analysis_config.physics

    payload.setdefault("sgdim", resolved_sgdim)
    payload.setdefault("mocombos", sg.mocombos if sg.mocombos else None)
    payload.setdefault("material_id_map", material_id_map)
    payload.setdefault("sg_configs", sg_configs)
    payload["mesh"] = sg.mesh
    return payload
