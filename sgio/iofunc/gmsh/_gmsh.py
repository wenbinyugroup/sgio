"""Backward-compatible Gmsh I/O entry points."""

from __future__ import annotations

from .mapper_in import map_input_to_mesh
from .parser import parse_input_buffer
from .writer import write_input_payload


def read_buffer(file, format_version: str = "4.1", **kwargs):
    """Read a Gmsh input buffer into a mesh object."""
    parsed = parse_input_buffer(file, format_version=format_version)
    return map_input_to_mesh(parsed)


def write_buffer(
    file,
    mesh,
    format_version,
    float_fmt,
    sgdim,
    mesh_only,
    binary,
    mocombos=None,
    material_id_map=None,
    sg_configs=None,
    **kwargs,
):
    """Write a mesh object to a Gmsh input buffer."""
    payload = {
        "mesh": mesh,
        "format_version": format_version,
        "float_fmt": float_fmt,
        "sgdim": sgdim,
        "mesh_only": mesh_only,
        "binary": binary,
        "mocombos": mocombos,
        "material_id_map": material_id_map,
        "sg_configs": sg_configs,
        **kwargs,
    }
    write_input_payload(file, payload)
