"""Unit tests for the Abaqus input mapper layer."""

from __future__ import annotations

import pytest

from sgio.core.property_ref_csys import property_ref_value_to_vabs_theta
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


@pytest.mark.unit
def test_map_input_to_structure_gene_maps_2d_discrete_orientations_to_vabs_angles(
    abaqus_test_files,
):
    """2D Abaqus discrete orientations should preserve sectional in-plane angles."""
    fixture = abaqus_test_files["root"] / "sg2_i_simple_eo1.inp"

    parsed = parse_input_file(str(fixture), sgdim=2, model="BM2")
    sg = map_input_to_structure_gene(parsed)

    element_to_expected_theta = {
        41: 180.0,
        46: 90.0,
        86: -90.0,
        70: 0.0,
    }

    # The Abaqus mapper stores property_ref_csys in the source (Abaqus xy)
    # frame; ``model_space='xy'`` resolves it to the VABS theta_1.
    theta_by_element_id: dict[int, float] = {}
    for block_index, element_ids in enumerate(sg.mesh.cell_data["element_id"]):
        for element_index, element_id in enumerate(element_ids):
            theta_by_element_id[int(element_id)] = property_ref_value_to_vabs_theta(
                sg.mesh.cell_data["property_ref_csys"][block_index][element_index],
                model_space="xy",
            )

    for element_id, expected_theta in element_to_expected_theta.items():
        assert element_id in theta_by_element_id
        assert theta_by_element_id[element_id] == pytest.approx(expected_theta)
