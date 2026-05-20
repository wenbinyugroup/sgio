"""Gmsh input writer."""

from __future__ import annotations

from typing import Any, TextIO

import numpy as np

from sgio.core.property_ref_csys import build_property_ref_axis_cell_data

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

    for key in (
        "property_ref_axis_y1",
        "property_ref_axis_y2",
        "property_ref_axis_y3",
    ):
        mesh.cell_data.pop(key, None)

    cell_csys = mesh.cell_data.get("property_ref_csys")
    if cell_csys is None:
        return

    try:
        axis_data = build_property_ref_axis_cell_data(cell_csys)
    except (TypeError, ValueError):
        return

    mesh.cell_data.update(axis_data)
