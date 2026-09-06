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
from ._common import normalize_additional_rotation_fields
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
    mesh.cell_data["gmsh:geometrical"] = [
        np.ones(len(cell_block), dtype=int) for cell_block in mesh.cells
    ]

    _normalize_local_coordinate_fields(mesh)
    normalize_additional_rotation_fields(mesh.cell_data, mesh.cells)


def _normalize_local_coordinate_fields(mesh: Any) -> None:
    """Normalize canonical and legacy local-csys fields before Gmsh writing."""
    cell_csys = resolve_element_local_csys(mesh.cell_data, mesh.cells)
    if cell_csys is None:
        return

    mesh.cell_data["element_local_csys"] = cell_csys
    mesh.cell_data["property_ref_csys"] = [
        np.asarray(block, dtype=float).copy() for block in mesh.cell_data["element_local_csys"]
    ]

    axis_data = build_property_ref_axis_cell_data(mesh.cell_data["element_local_csys"])
    mesh.cell_data.update(axis_data)
