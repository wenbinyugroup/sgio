"""Unit tests for the Abaqus parser layer."""

from __future__ import annotations

import pytest

from sgio.iofunc.abaqus.parser import parse_input_file


@pytest.mark.unit
def test_parse_input_file_returns_inprw_payload(abaqus_test_files):
    """Parser should wrap ``inpRW`` and preserve caller context."""
    fixture = abaqus_test_files["root"] / "sg2_min.inp"

    payload = parse_input_file(str(fixture), sgdim=2, model="PL1")

    assert payload["filename"] == str(fixture)
    assert payload["sgdim"] == 2
    assert payload["model"] == "PL1"
    assert hasattr(payload["inprw"], "nd")
    assert len(payload["inprw"].nd) > 0
