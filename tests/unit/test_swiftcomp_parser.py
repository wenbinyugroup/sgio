"""Tests for the SwiftComp parser layer."""

import pytest

from sgio.iofunc.swiftcomp.parser import parse_input_buffer


@pytest.mark.unit
def test_parse_input_buffer_returns_raw_payload(test_data_dir):
    """SwiftComp parser should return raw intermediate data without SG mapping."""
    fixture = test_data_dir / "swiftcomp" / "sg21t_tri6_sc21.sg"

    with open(fixture, "r", encoding="utf-8") as file:
        parsed = parse_input_buffer(file, format_version="2.1", model="BM2")

    assert parsed["format_version"] == "2.1"
    assert parsed["smdim"] == 1
    assert parsed["configs"]["sgdim"] == 2
    assert parsed["configs"]["num_nodes"] == 4816
    assert parsed["configs"]["num_elements"] == 2122
    assert parsed["configs"]["num_materials"] == 1
    assert parsed["mesh"].points.shape[0] == 4816
    assert sum(len(block.data) for block in parsed["mesh"].cells) == 2122
    assert len(parsed["materials"]) == 1
    assert len(parsed["material_id_pairs"]) == 1
