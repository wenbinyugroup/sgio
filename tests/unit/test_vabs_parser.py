"""Tests for the VABS parser layer."""

from sgio.iofunc.vabs.parser import parse_input_buffer

import pytest


@pytest.mark.unit
def test_parse_input_buffer_returns_raw_payload(test_data_dir):
    """VABS parser should return raw intermediate data without SG mapping."""
    fixture = test_data_dir / "vabs" / "version_4_1" / "3cells.sg"

    with open(fixture, "r", encoding="utf-8") as file:
        parsed = parse_input_buffer(file, format_version="4.1")

    assert parsed["format_version"] == "4.1"
    assert parsed["configs"]["sgdim"] == 2
    assert parsed["configs"]["num_nodes"] == 862
    assert parsed["configs"]["num_elements"] == 218
    assert parsed["configs"]["num_materials"] == 1
    assert parsed["mesh"].points.shape[0] == 862
    assert sum(len(block.data) for block in parsed["mesh"].cells) == 218
    assert len(parsed["materials"]) == 1
    assert len(parsed["material_id_pairs"]) == 1
