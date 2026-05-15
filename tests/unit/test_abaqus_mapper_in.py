"""Unit tests for the Abaqus input mapper layer."""

from __future__ import annotations

import pytest

from sgio.iofunc.abaqus.mapper_in import map_input_to_structure_gene
from sgio.iofunc.abaqus.parser import parse_input_file


@pytest.mark.unit
def test_map_input_to_structure_gene_builds_structure_gene(abaqus_test_files):
    """Mapper should convert parsed Abaqus payload into a populated SG."""
    fixture = abaqus_test_files["root"] / "sg2_min.inp"

    parsed = parse_input_file(str(fixture), sgdim=2, model="PL1")
    sg = map_input_to_structure_gene(parsed)

    assert sg.sgdim == 2
    assert sg.smdim == 2
    assert sg.analysis_config.model == 0
    assert sg.mesh is not None
    assert len(sg.mesh.points) > 0
    assert "node_id" in sg.mesh.point_data
    assert "property_id" in sg.mesh.cell_data
    assert sg.materials
    assert sg.mocombos
