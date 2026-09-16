"""End-to-end check: SG manifest -> SwiftComp input -> solver stiffness."""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest

import sgio

FIXTURE_DIR = Path(__file__).parents[1] / 'fixtures' / 'abaqus'


@pytest.mark.integration
@pytest.mark.requires_solver
@pytest.mark.skipif(shutil.which('SwiftComp') is None, reason='SwiftComp not installed')
def test_manifest_convert_matches_reference_stiffness(tmp_path):
    sc_file = str(tmp_path / 'sg2d-user-lam.sc')

    # Only the manifest describes the SG; no SG arguments are passed.
    sgio.convert(str(FIXTURE_DIR / 'sg2d-user-lam.sg.json'), sc_file, 'sg_manifest', 'sc')
    sgio.run('SwiftComp', sc_file, 'h', smdim=1)

    result = sgio.read_output_model(f'{sc_file}.k', 'sc', model_type='BM1')
    reference = sgio.read_output_model(
        str(FIXTURE_DIR / 'sg2d-user-lam.sc.k'), 'sc', model_type='BM1'
    )
    for name in ('ea', 'gj', 'ei22', 'ei33'):
        np.testing.assert_allclose(getattr(result, name), getattr(reference, name), rtol=1e-6)
