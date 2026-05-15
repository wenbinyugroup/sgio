"""Unit tests for the Gmsh parser layer."""

from __future__ import annotations

import pytest

from sgio.iofunc.gmsh.parser import parse_input_buffer


@pytest.mark.unit
def test_parse_input_buffer_reads_gmsh41_fixture(gmsh_test_files):
    """Parser should return raw header metadata and the parsed mesh."""
    fixture = gmsh_test_files["root"] / "sg33_cube_tetra4_min_gmsh41.msh"

    with open(fixture, "rb") as file:
        payload = parse_input_buffer(file, format_version="4.1")

    assert payload["requested_format_version"] == "4.1"
    assert payload["format_version"] == "4.1"
    assert payload["data_size"] == 8
    assert payload["is_ascii"] is True
    assert len(payload["mesh"].points) > 0
    assert "property_id" in payload["mesh"].cell_data
