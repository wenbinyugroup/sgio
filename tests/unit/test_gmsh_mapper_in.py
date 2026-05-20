"""Unit tests for the Gmsh input mapper layer."""

from __future__ import annotations

import pytest

from sgio.iofunc.gmsh.mapper_in import map_input_to_mesh
from sgio.iofunc.gmsh.parser import parse_input_buffer


@pytest.mark.unit
def test_map_input_to_mesh_returns_parser_mesh(gmsh_test_files):
    """Gmsh mapper-in should keep the mesh IR unchanged."""
    fixture = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"

    with open(fixture, "rb") as file:
        parsed = parse_input_buffer(file, format_version="4.1")

    mesh = map_input_to_mesh(parsed)

    assert mesh is parsed["mesh"]
    assert len(mesh.cells) > 0
