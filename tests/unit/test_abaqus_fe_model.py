"""Unit tests for the Abaqus FEModel mapping path (Phase 10B).

Covers :func:`map_input_to_fe_model` (named orientations, structural-block
fallback into ``extras``) and its equivalence with the delegating SG path.
"""
from __future__ import annotations

import pytest

from sgio.core import FEModel, Orientation
from sgio.iofunc.abaqus.mapper_in import (
    map_input_to_fe_model,
    map_input_to_structure_gene,
)
from sgio.iofunc.abaqus.parser import parse_input_file


@pytest.mark.unit
@pytest.mark.abaqus
class TestAbaqusFeModelMapping:
    def test_returns_fe_model_with_core_fields(self, abaqus_test_files):
        fixture = abaqus_test_files["root"] / "sg2_min.inp"
        parsed = parse_input_file(str(fixture), sgdim=2, model="PL1")
        fe = map_input_to_fe_model(parsed)

        assert isinstance(fe, FEModel)
        assert fe.mesh is not None and len(fe.mesh.points) > 0
        assert fe.materials
        assert fe.sections
        assert "property_id" in fe.mesh.cell_data

    def test_promotes_named_orientations(self, abaqus_test_files):
        fixture = abaqus_test_files["root"] / "sg31_rec_ori_discrete.inp"
        parsed = parse_input_file(str(fixture), sgdim=3, model="SD1")
        fe = map_input_to_fe_model(parsed)

        assert "Ori-1" in fe.orientations
        orient = fe.orientations["Ori-1"]
        assert isinstance(orient, Orientation)
        assert orient.extras["source"] == "abaqus"
        # Distribution reference is preserved, not silently dropped.
        assert orient.extras["distribution"]

    def test_routes_structural_blocks_to_extras(self, abaqus_test_files):
        fixture = abaqus_test_files["root"] / "sg31_rec_ori_discrete.inp"
        parsed = parse_input_file(str(fixture), sgdim=3, model="SD1")
        fe = map_input_to_fe_model(parsed)

        assert "abaqus_steps" in fe.extras
        assert len(fe.extras["abaqus_steps"]) > 0
        block = fe.extras["abaqus_steps"][0]
        # Serialized as a plain, deep-copyable dict.
        assert set(block) == {"keyword", "parameters", "data"}
        assert isinstance(block["parameters"], dict)


@pytest.mark.unit
@pytest.mark.abaqus
class TestSgPathDelegatesToFeModel:
    @pytest.mark.parametrize(
        "fixture_name, sgdim, model",
        [
            ("sg2_min.inp", 2, "PL1"),
            ("sg31_rec_ori_discrete.inp", 3, "SD1"),
        ],
    )
    def test_sg_matches_fe_model_core(
        self, abaqus_test_files, fixture_name, sgdim, model
    ):
        fixture = abaqus_test_files["root"] / fixture_name
        parsed = parse_input_file(str(fixture), sgdim=sgdim, model=model)

        fe = map_input_to_fe_model(parsed)
        sg = map_input_to_structure_gene(parsed)

        # Delegate guard: SG core fields equal the FEModel path.
        assert set(sg.materials) == set(fe.materials)
        assert set(sg.sections) == set(fe.sections)
        assert set(sg.orientations) == set(fe.orientations)
        assert sg.mesh.points.shape == fe.mesh.points.shape
        assert sg.sgdim == sgdim

    def test_extras_survive_sg_wrapping(self, abaqus_test_files):
        """Structural extras must survive the from_fe deep copy on the SG path."""
        fixture = abaqus_test_files["root"] / "sg31_rec_ori_discrete.inp"
        parsed = parse_input_file(str(fixture), sgdim=3, model="SD1")
        sg = map_input_to_structure_gene(parsed)

        assert "abaqus_steps" in sg.fe_model.extras
