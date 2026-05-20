"""Tests for VABS <-> Gmsh format conversion."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from sgio import convert, configure_logging, logger

configure_logging(cout_level='info')

_YML = 'test_convert_vabs_gmsh.yml'


def _load_test_cases(test_data_dir: Path) -> list[dict]:
    path = test_data_dir / 'yaml' / _YML
    if not path.exists():
        path = test_data_dir / _YML
    if not path.exists():
        legacy = Path(__file__).parent.parent / 'files' / _YML
        if legacy.exists():
            path = legacy
        else:
            pytest.skip(f'Test case file not found: {_YML}')
    with open(path) as f:
        return yaml.safe_load(f)


def _resolve_input(fn_rel: str, test_data_dir: Path) -> str:
    fn = str(test_data_dir / fn_rel)
    if not Path(fn).exists():
        fn = str(Path(__file__).parent.parent / 'files' / fn_rel)
    return fn


@pytest.mark.conversion
@pytest.mark.gmsh
def test_vabs_gmsh_conversion(test_data_dir, capsys):
    """Test VABS <-> Gmsh file format conversion."""
    with capsys.disabled():
        test_cases = _load_test_cases(test_data_dir)
        output_dir = Path(__file__).parent.parent / '_temp'
        os.makedirs(output_dir, exist_ok=True)

        for _case in test_cases:
            fn_in = _resolve_input(_case['fn_in'], test_data_dir)
            fn_out = str(output_dir / _case['fn_out'])

            logger.info(f'Converting {fn_in} to {fn_out}...')
            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f'Output file was not created: {fn_out}'
            assert os.path.getsize(fn_out) > 0, f'Output file is empty: {fn_out}'

            if _case.get('solver'):
                pytest.skip('Solver execution skipped (requires external tool)')


@pytest.mark.conversion
@pytest.mark.gmsh
def test_convert_to_gmsh(test_data_dir, capsys):
    """Test conversion to Gmsh format."""
    with capsys.disabled():
        test_cases = _load_test_cases(test_data_dir)
        gmsh_cases = [c for c in test_cases if c.get('ff_out') == 'gmsh']

        if not gmsh_cases:
            pytest.skip('No Gmsh output test cases found')

        output_dir = Path(__file__).parent.parent / '_temp'
        os.makedirs(output_dir, exist_ok=True)

        for _case in gmsh_cases:
            fn_in = _resolve_input(_case['fn_in'], test_data_dir)
            fn_out = str(output_dir / _case['fn_out'])

            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f'Output file was not created: {fn_out}'
            assert os.path.getsize(fn_out) > 0, f'Output file is empty: {fn_out}'
