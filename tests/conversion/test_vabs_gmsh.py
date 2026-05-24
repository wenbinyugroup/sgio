"""Tests for VABS <-> Gmsh format conversion."""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest
import yaml

from sgio import convert, configure_logging, logger, read

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


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
def test_gmsh_xy_section_converts_to_vabs(test_data_dir, temp_dir):
    """A Gmsh section mesh in the ``xy`` plane should convert to VABS."""
    src = test_data_dir / 'gmsh' / 'laminate_closed_spline_3.msh'
    dst = temp_dir / 'laminate_closed_spline_3_xy.sg'

    source_sg = read(str(src), 'gmsh', format_version='4.1', sgdim=2, model_type='BM2')

    convert(
        str(src),
        str(dst),
        'gmsh',
        'vabs',
        file_version_in='4.1',
        file_version_out='4.1',
        sgdim=2,
        model_space='xy',
        model_type='BM2',
    )

    assert dst.exists(), f'Output file was not created: {dst}'
    assert dst.stat().st_size > 0, f'Output file is empty: {dst}'

    roundtrip = read(str(dst), 'vabs', format_version='4.1', model_type='BM2')
    np.testing.assert_allclose(roundtrip.mesh.points[:, 0], 0.0)
    np.testing.assert_allclose(roundtrip.mesh.points[:, 1], source_sg.mesh.points[:, 0])
    np.testing.assert_allclose(roundtrip.mesh.points[:, 2], source_sg.mesh.points[:, 1])


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
@pytest.mark.parametrize(
    ('model_space', 'expected_axes'),
    [('xy', (0, 1)), ('yz', (1, 2)), ('zx', (2, 0))],
)
def test_gmsh_to_vabs_respects_model_space_projection(
    test_data_dir,
    temp_dir,
    model_space,
    expected_axes,
):
    """Gmsh -> VABS conversion should project nodes onto the requested section plane."""
    src = test_data_dir / 'gmsh' / 'laminate_closed_spline_3.msh'
    dst = temp_dir / f'laminate_closed_spline_3_{model_space}.sg'

    source_sg = read(str(src), 'gmsh', format_version='4.1', sgdim=2, model_type='BM2')

    convert(
        str(src),
        str(dst),
        'gmsh',
        'vabs',
        file_version_in='4.1',
        file_version_out='4.1',
        sgdim=2,
        model_space=model_space,
        model_type='BM2',
    )

    roundtrip = read(str(dst), 'vabs', format_version='4.1', model_type='BM2')
    expected_points = source_sg.mesh.points[:, expected_axes]

    np.testing.assert_allclose(roundtrip.mesh.points[:, 0], 0.0)
    np.testing.assert_allclose(roundtrip.mesh.points[:, 1], expected_points[:, 0])
    np.testing.assert_allclose(roundtrip.mesh.points[:, 2], expected_points[:, 1])
