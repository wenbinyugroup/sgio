"""Tests for writing SwiftComp (.sc) input files."""
from __future__ import annotations

import re
from io import StringIO
from pathlib import Path

import numpy as np
import pytest

import sgio


def _parse_sc_numbers(text: str) -> list[list[float]]:
    """Parse all numeric tokens from sc file lines, ignoring comments.

    Parameters
    ----------
    text : str
        Content of a .sc file.

    Returns
    -------
    list[list[float]]
        Non-empty rows of numeric values (comments stripped).
    """
    rows = []
    for line in text.splitlines():
        # Strip inline comments
        line = line.split('#')[0].split('!')[0].strip()
        if not line:
            continue
        tokens = re.split(r'\s+', line)
        try:
            nums = [float(t) for t in tokens]
            rows.append(nums)
        except ValueError:
            pass  # skip non-numeric lines (e.g. blank or partial)
    return rows


@pytest.mark.io
@pytest.mark.swiftcomp
def test_write_sc_pl1_from_abaqus(test_data_dir, expected_data_dir, temp_dir):
    """Converting an Abaqus 2D mesh to SwiftComp PL1 format writes correct output.

    Verifies that model header, curvatures, mesh, orientations, material
    combos, material properties, and omega are all written correctly.
    """
    fn_in = test_data_dir / 'abaqus' / 'sg2_min.inp'
    fn_expected = expected_data_dir / 'sg2_min.sc'

    if not fn_in.exists():
        pytest.skip(f'Input file not found: {fn_in}')
    if not fn_expected.exists():
        pytest.skip(f'Expected file not found: {fn_expected}')

    # Read Abaqus model
    sg = sgio.read(str(fn_in), file_format='abaqus', sgdim=2)

    # Configure plate-specific parameters
    sg.initial_curvature = [1, 2]
    sg.omega = 10

    # Write to SwiftComp format
    fn_out = str(temp_dir / 'sg2_min.sc')
    sgio.write(sg, filename=fn_out, file_format='sc', model_type='pl1', model_space='xy')

    # Load both outputs for comparison
    actual = Path(fn_out).read_text()
    expected = fn_expected.read_text()

    actual_rows = _parse_sc_numbers(actual)
    expected_rows = _parse_sc_numbers(expected)

    assert len(actual_rows) == len(expected_rows), (
        f'Row count mismatch: got {len(actual_rows)}, expected {len(expected_rows)}'
    )

    for i, (act_row, exp_row) in enumerate(zip(actual_rows, expected_rows)):
        assert len(act_row) == len(exp_row), (
            f'Row {i}: token count mismatch: got {act_row}, expected {exp_row}'
        )
        np.testing.assert_allclose(
            act_row, exp_row, rtol=1e-9,
            err_msg=f'Row {i} values differ: got {act_row}, expected {exp_row}'
        )
