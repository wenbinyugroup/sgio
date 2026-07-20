"""Unit tests for the ``read_fe_model`` public entry point (Phase 10A).

Verifies the explicit generic-FE read entry returns an :class:`FEModel` whose
core fields match ``read(...).fe_model`` for the Abaqus path.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import sgio
from sgio.core import FEModel


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "abaqus"
ABAQUS_INP = FIXTURES_DIR / "sg2_airfoil.inp"


@pytest.mark.unit
@pytest.mark.abaqus
class TestReadFeModel:
    def test_returns_fe_model(self):
        if not ABAQUS_INP.exists():
            pytest.skip(f"Test fixture not found: {ABAQUS_INP}")

        fe = sgio.read_fe_model(str(ABAQUS_INP), "abaqus", model_type="PL1", sgdim=2)
        assert isinstance(fe, FEModel)
        assert fe.mesh is not None
        assert len(fe.materials) > 0
        assert len(fe.sections) > 0

    def test_matches_read_fe_model_field(self):
        if not ABAQUS_INP.exists():
            pytest.skip(f"Test fixture not found: {ABAQUS_INP}")

        fe = sgio.read_fe_model(str(ABAQUS_INP), "abaqus", model_type="PL1", sgdim=2)
        sg = sgio.read(str(ABAQUS_INP), "abaqus", model_type="PL1", sgdim=2)

        # read_fe_model is the FE core of what read() returns.
        assert set(fe.materials) == set(sg.materials)
        assert set(fe.sections) == set(sg.sections)
        assert fe.mesh.points.shape == sg.mesh.points.shape

    def test_exported_at_top_level(self):
        assert hasattr(sgio, "read_fe_model")
        assert "read_fe_model" in sgio.__all__
