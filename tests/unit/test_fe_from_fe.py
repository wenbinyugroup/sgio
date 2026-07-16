"""Unit tests for the ``from_fe`` wrapping workflow (Phase 10A).

Covers :meth:`StructureGene.from_fe` (new) and its symmetry with the existing
:meth:`StructuralModel.from_fe`.
"""
from __future__ import annotations

import numpy as np
import pytest

from sgio.core import FEModel, Section, StructuralModel, StructureGene
from sgio.core.mesh import CellBlock, SGMesh


def _make_fe_model() -> FEModel:
    """Build a minimal FEModel with mesh, one material, one section, extras."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    cells = [CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))]
    mesh = SGMesh(points=points, cells=cells)
    return FEModel(
        name="macro",
        mesh=mesh,
        materials={"steel": object()},
        sections={"sec-1": Section(name="sec-1", material="steel", property_id=1)},
        extras={"abaqus_steps": [{"keyword": "step"}]},
    )


@pytest.mark.unit
class TestStructureGeneFromFe:
    def test_wraps_and_proxies_fe_fields(self):
        fe = _make_fe_model()
        sg = StructureGene.from_fe(fe, sgdim=2, smdim=1)

        assert sg.name == "macro"
        assert sg.sgdim == 2
        assert sg.smdim == 1
        assert sg.spdim == 2  # defaults to sgdim
        assert "steel" in sg.materials
        assert "sec-1" in sg.sections
        assert sg.extras["abaqus_steps"] == [{"keyword": "step"}]

    def test_deep_copies_source_fe(self):
        fe = _make_fe_model()
        sg = StructureGene.from_fe(fe, sgdim=2, smdim=1)

        # Mutating the SG must not touch the source FEModel.
        sg.materials["new"] = object()
        sg.mesh.points[0, 0] = 99.0
        assert "new" not in fe.materials
        assert fe.mesh.points[0, 0] == 0.0

    def test_analysis_config_keeps_defaults(self):
        fe = _make_fe_model()
        sg = StructureGene.from_fe(fe, sgdim=2, smdim=1)
        assert sg.analysis_config.analysis == 0
        assert sg.analysis_config.physics == 0
        assert sg.analysis_config.model == 0


@pytest.mark.unit
class TestFromFeSymmetry:
    def test_sg_and_structural_share_fe_contract(self):
        fe = _make_fe_model()
        sg = StructureGene.from_fe(fe, sgdim=2)
        sm = StructuralModel.from_fe(fe)

        # Both expose the same FE core fields via proxies.
        assert set(sg.materials) == set(sm.materials)
        assert set(sg.sections) == set(sm.sections)
        # Both deep-copied: independent from the source and from each other.
        assert sg.fe_model is not fe
        assert sm.fe_model is not fe
        assert sg.fe_model is not sm.fe_model
