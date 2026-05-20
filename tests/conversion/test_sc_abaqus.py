"""Tests for SwiftComp <-> Abaqus format conversion."""
from __future__ import annotations

import os
from io import StringIO
from pathlib import Path

import numpy as np
import pytest
import yaml

from sgio import convert, configure_logging, logger
from sgio.core.mesh import SGMesh
from sgio.iofunc.swiftcomp._mesh import write_buffer as sc_write_buffer

configure_logging(cout_level='info')

_YML = 'test_convert_sc_abaqus.yml'


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


def _mesh_with_nonconsecutive_ids() -> SGMesh:
    """Triangle mesh with non-consecutive node IDs (require renumbering for SwiftComp)."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([10, 20, 30])}
    cell_data = {'property_id': [np.array([1])]}
    return SGMesh(points, cells, point_data=point_data, cell_data=cell_data)


@pytest.mark.conversion
@pytest.mark.swiftcomp
def test_sc_abaqus_conversion(test_data_dir, capsys):
    """Test SwiftComp <-> Abaqus file format conversion."""
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
@pytest.mark.swiftcomp
def test_convert_to_swiftcomp(test_data_dir, capsys):
    """Test conversion to SwiftComp format."""
    with capsys.disabled():
        test_cases = _load_test_cases(test_data_dir)
        sc_cases = [c for c in test_cases if c.get('ff_out') in ('sc', 'swiftcomp')]

        if not sc_cases:
            pytest.skip('No SwiftComp output test cases found')

        output_dir = Path(__file__).parent.parent / '_temp'
        os.makedirs(output_dir, exist_ok=True)

        for _case in sc_cases:
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
@pytest.mark.swiftcomp
def test_swiftcomp_auto_renumbers_nonconsecutive_ids():
    """SwiftComp output must have consecutive node IDs; non-consecutive ones are renumbered."""
    mesh = _mesh_with_nonconsecutive_ids()
    f = StringIO()
    sc_write_buffer(f, mesh, sgdim=2, model_space='xy')
    assert list(mesh.point_data['node_id']) == [1, 2, 3]  # type: ignore[arg-type]


@pytest.mark.conversion
@pytest.mark.swiftcomp
def test_swiftcomp_emits_warning_on_renumber():
    """SwiftComp write emits UserWarning when renumbering non-consecutive node IDs."""
    mesh = _mesh_with_nonconsecutive_ids()
    f = StringIO()
    with pytest.warns(UserWarning, match='[Nn]ode'):
        sc_write_buffer(f, mesh, sgdim=2, model_space='xy')
