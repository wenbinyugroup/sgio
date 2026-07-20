"""Smoke test for the multiscale beam example (Phase 10D).

Runs ``examples/multiscale_beam/run.py`` end to end to guard the generic-FE
workflow against regressions.
"""
from __future__ import annotations

import runpy
from pathlib import Path

import pytest

EXAMPLE = (
    Path(__file__).parent.parent.parent
    / "examples"
    / "multiscale_beam"
    / "run.py"
)


@pytest.mark.integration
def test_multiscale_beam_example_runs(capsys):
    if not EXAMPLE.exists():
        pytest.skip(f"Example not found: {EXAMPLE}")

    runpy.run_path(str(EXAMPLE), run_name="__main__")

    out = capsys.readouterr().out
    assert "effective Euler-Bernoulli beam section" in out
    assert "beam mesh:" in out
    assert "blade_section" in out
    assert "abaqus_boundary" in out
    assert "Multiscale handoff complete" in out
