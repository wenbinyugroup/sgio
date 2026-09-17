"""End-to-end conversion of a TexGen Abaqus deck to SwiftComp.

A TexGen deck exercises four things at once that nothing else in the suite
covers together: per-element orientations pulled from an external
``*Distribution, Input=`` file, ``*Expansion`` thermal data, ordinary
``*Solid Section`` thickness data lines, and an omega that must be derived
from the SG bounding box rather than left at 1.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import sgio
from sgio.core.omega import compute_omega


TEXGEN_DIR = Path(__file__).parent.parent / 'fixtures' / 'texgen' / 'plain_weave_3d'
INPUT_FILE = TEXGEN_DIR / 'plain_weave_3d.inp'


def _sc_numbers(line: str) -> list[float]:
    """Parse one SwiftComp data line into floats, dropping any comment."""
    return [float(token) for token in line.split('#')[0].split()]


@pytest.fixture
def texgen_sg():
    """Read the TexGen fixture as a 3D SG for a 3D macro model."""
    return sgio.read(
        str(INPUT_FILE), 'abaqus', sgdim=3, model_type='sd1'
    )


@pytest.mark.integration
@pytest.mark.io
def test_texgen_read_maps_materials_and_orientations(texgen_sg):
    """Both materials keep their CTE and every yarn keeps its own frame."""
    assert texgen_sg.materials['Mat0'].cte == pytest.approx(
        [6.5e-06, 6.5e-06, 6.5e-06, 0.0, 0.0, 0.0]
    )
    assert texgen_sg.materials['Mat1'].cte == pytest.approx(
        [-2e-07, 3e-06, 3e-06, 0.0, 0.0, 0.0]
    )

    # The orientations live in plain_weave_3d.ori, reachable only through the
    # '*Distribution, Input=' include.
    csys = np.asarray(texgen_sg.mesh.cell_data['property_ref_csys'][0], dtype=float)
    assert len(np.unique(np.round(csys, 6), axis=0)) > 1


@pytest.mark.integration
@pytest.mark.io
@pytest.mark.parametrize("model_type, smdim", [('sd1', 3), ('pl1', 2)])
def test_texgen_writes_thermoelastic_swiftcomp(tmp_path, model_type, smdim):
    """The deck converts to a thermoelastic SwiftComp input for both models.

    Asserts the two values that were silently wrong before: the physics flag
    in the header and omega on the last line, which depends on how many
    dimensions the SG shares with the macro model.
    """
    fn_out = tmp_path / f'plain_weave_{model_type}.sc'

    sg = sgio.convert(
        file_name_in=str(INPUT_FILE), file_name_out=str(fn_out),
        file_format_in='abaqus', file_format_out='sc',
        sgdim=3, model_type=model_type, physics='thermoelastic',
    )

    lines = [line for line in fn_out.read_text().splitlines() if line.strip()]

    # The plate model header carries two extra leading lines (model flag and
    # initial curvatures) ahead of the physics record.
    header = _sc_numbers(lines[2 if smdim == 2 else 0])
    assert header[0] == 1  # analysis = thermoelastic

    expected_omega = compute_omega(sg.mesh.points, 3, smdim)
    assert _sc_numbers(lines[-1])[0] == pytest.approx(expected_omega)
    assert _sc_numbers(lines[-1])[0] != pytest.approx(1.0)
