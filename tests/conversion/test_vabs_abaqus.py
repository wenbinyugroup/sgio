"""Tests for VABS <-> Abaqus format conversion."""
from __future__ import annotations

import os
import tempfile
import warnings
from io import StringIO
from pathlib import Path

import numpy as np
import pytest
import yaml

from sgio import convert, configure_logging, logger, read
from sgio.core.mesh import SGMesh
from sgio.core.numbering import auto_renumber_for_format
from sgio.core.property_ref_csys import property_ref_value_to_vabs_theta
from sgio.iofunc.vabs._mesh import write_buffer as vabs_write_buffer

configure_logging(cout_level='info')

_YML = 'test_convert_vabs_abaqus.yml'


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
    """Triangle mesh with non-consecutive node IDs (require renumbering for vabs)."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([10, 20, 30])}
    cell_data = {'property_id': [np.array([1])]}
    return SGMesh(points, cells, point_data=point_data, cell_data=cell_data)


@pytest.mark.conversion
@pytest.mark.vabs
def test_vabs_abaqus_conversion(test_data_dir, capsys):
    """Test VABS <-> Abaqus file format conversion."""
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
                pytest.skip(f"Solver execution skipped (requires external tool)")


@pytest.mark.conversion
@pytest.mark.vabs
def test_convert_to_vabs_v41(test_data_dir, capsys):
    """Test conversion to VABS v4.1 format."""
    with capsys.disabled():
        test_cases = _load_test_cases(test_data_dir)
        vabs41_cases = [c for c in test_cases if c.get('version_out') == '4.1']
        assert len(vabs41_cases) > 0, 'No VABS v4.1 test cases found'

        output_dir = Path(__file__).parent.parent / '_temp'
        os.makedirs(output_dir, exist_ok=True)

        for _case in vabs41_cases:
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
@pytest.mark.vabs
def test_convert_to_vabs_v40(test_data_dir, capsys):
    """Test conversion to VABS v4.0 format."""
    with capsys.disabled():
        test_cases = _load_test_cases(test_data_dir)
        vabs40_cases = [c for c in test_cases if c.get('version_out') == '4.0']

        if not vabs40_cases:
            pytest.skip('No VABS v4.0 test cases found')

        output_dir = Path(__file__).parent.parent / '_temp'
        os.makedirs(output_dir, exist_ok=True)

        for _case in vabs40_cases:
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
@pytest.mark.vabs
def test_abaqus_2d_discrete_orientation_survives_vabs_conversion(test_data_dir):
    """Abaqus 2D discrete orientations should survive Abaqus -> VABS conversion."""
    src = test_data_dir / "abaqus" / "sg2_i_simple_eo1.inp"
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".sg",
        dir=Path.cwd(),
        delete=False,
    ) as temp_file:
        dst = Path(temp_file.name)

    try:
        convert(
            str(src),
            str(dst),
            "abaqus",
            "vabs",
            model_type="BM2",
            sgdim=2,
        )

        roundtrip = read(
            str(dst),
            "vabs",
            model_type="BM2",
            format_version="4.1",
        )
    finally:
        dst.unlink(missing_ok=True)

    theta_by_element_id: dict[int, float] = {}
    for block_index, element_ids in enumerate(roundtrip.mesh.cell_data["element_id"]):
        for element_index, element_id in enumerate(element_ids):
            theta_by_element_id[int(element_id)] = property_ref_value_to_vabs_theta(
                roundtrip.mesh.cell_data["property_ref_csys"][block_index][element_index]
            )

    assert theta_by_element_id[41] == pytest.approx(180.0)
    assert theta_by_element_id[46] == pytest.approx(90.0)
    assert theta_by_element_id[86] == pytest.approx(-90.0)
    assert theta_by_element_id[70] == pytest.approx(0.0)


@pytest.mark.conversion
@pytest.mark.vabs
def test_vabs_auto_renumbers_nonconsecutive_ids():
    """VABS output must have consecutive node IDs; non-consecutive ones are renumbered."""
    mesh = _mesh_with_nonconsecutive_ids()
    f = StringIO()
    vabs_write_buffer(f, mesh, sgdim=2, model_space='xy')
    assert list(mesh.point_data['node_id']) == [1, 2, 3]  # type: ignore[arg-type]


@pytest.mark.conversion
@pytest.mark.vabs
def test_vabs_emits_warning_on_renumber():
    """VABS write emits UserWarning when renumbering non-consecutive node IDs."""
    mesh = _mesh_with_nonconsecutive_ids()
    f = StringIO()
    with pytest.warns(UserWarning, match='[Nn]ode'):
        vabs_write_buffer(f, mesh, sgdim=2, model_space='xy')


@pytest.mark.conversion
@pytest.mark.vabs
def test_auto_renumber_preserves_compliant_ids():
    """auto_renumber_for_format is a no-op when IDs already satisfy the VABS format."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    mesh = SGMesh(
        points, cells,
        point_data={'node_id': np.array([1, 2, 3])},
        cell_data={'property_id': [np.array([1])], 'element_id': [np.array([1])]},
    )
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        nodes_renumbered, elems_renumbered = auto_renumber_for_format(mesh, format='vabs')
    assert not nodes_renumbered
    assert not elems_renumbered
