"""Tests for reading structure genes from SG manifests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import sgio
from sgio._exceptions import IncompleteModelDataError

FIXTURE_DIR = Path(__file__).parents[1] / 'fixtures' / 'abaqus'
MANIFEST = FIXTURE_DIR / 'sg2d-user-lam.sg.json'


@pytest.fixture
def write_manifest(tmp_path):
    """Return a function writing a variant of the fixture manifest next to the model file."""
    shutil.copy(FIXTURE_DIR / 'sg2d-user-lam.inp', tmp_path / 'sg2d-user-lam.inp')

    def _write(**changes) -> Path:
        data = json.loads(MANIFEST.read_text(encoding='utf-8'))
        for key, value in changes.items():
            if value is None:
                data.pop(key, None)
            else:
                data[key] = value
        path = tmp_path / 'variant.sg.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    return _write


@pytest.mark.unit
class TestReadSGManifest:
    """Reading an Abaqus model file through its SG manifest."""

    def test_reads_sg_fields_from_manifest(self):
        sg = sgio.read(str(MANIFEST), 'sg_manifest')

        assert (sg.sgdim, sg.smdim, sg.analysis_config.model) == (2, 1, 0)
        assert sg.model_space == 'yz'
        assert (sg.nnodes, sg.nelems, sg.nmates) == (7066, 6753, 2)

    def test_agreeing_arguments_are_accepted(self):
        sg = sgio.read(
            str(MANIFEST), 'sg_manifest', sgdim=2, model_type='bm1', model_space='yz'
        )

        assert sg.model_space == 'yz'

    def test_applies_config_and_beam_geometry(self, write_manifest):
        path = write_manifest(config={'physics': 1}, initial_twist=0.5)

        sg = sgio.read(str(path), 'sg_manifest')

        assert sg.analysis_config.physics == 1
        assert sg.analysis_config.model == 0
        assert sg.initial_twist == 0.5


@pytest.mark.unit
class TestSGManifestErrors:
    """Invalid manifests and contradicting arguments fail loudly."""

    @pytest.mark.parametrize('field', ['sgdim', 'model_type', 'model_space'])
    def test_missing_required_field(self, write_manifest, field):
        path = write_manifest(**{field: None})

        with pytest.raises(IncompleteModelDataError, match=field):
            sgio.read(str(path), 'sg_manifest')

    def test_unknown_version(self, write_manifest):
        path = write_manifest(sg_manifest_version=2)

        with pytest.raises(ValueError, match='sg_manifest_version'):
            sgio.read(str(path), 'sg_manifest')

    def test_missing_model_file_format(self, write_manifest):
        path = write_manifest(model_file={'path': 'sg2d-user-lam.inp'})

        with pytest.raises(IncompleteModelDataError, match='model_file.format'):
            sgio.read(str(path), 'sg_manifest')

    def test_unknown_field(self, write_manifest):
        path = write_manifest(sg_dim=2)

        with pytest.raises(ValueError, match='sg_dim'):
            sgio.read(str(path), 'sg_manifest')

    def test_invalid_model_space(self, write_manifest):
        path = write_manifest(model_space='x')

        with pytest.raises(ValueError, match='model_space'):
            sgio.read(str(path), 'sg_manifest')

    def test_block_owned_by_model_file(self, write_manifest):
        path = write_manifest(sections=[])

        with pytest.raises(ValueError, match='owns'):
            sgio.read(str(path), 'sg_manifest')

    def test_config_must_not_repeat_submodel(self, write_manifest):
        path = write_manifest(config={'model': 1})

        with pytest.raises(ValueError, match='model_type'):
            sgio.read(str(path), 'sg_manifest')

    @pytest.mark.parametrize(
        'argument', [{'sgdim': 3}, {'model_type': 'BM2'}, {'model_space': 'xy'}]
    )
    def test_argument_disagreeing_with_manifest(self, argument):
        with pytest.raises(ValueError, match='disagrees'):
            sgio.read(str(MANIFEST), 'sg_manifest', **argument)


@pytest.fixture(scope='module')
def lam_sg():
    """Structure gene read from the Abaqus fixture manifest."""
    return sgio.read(str(MANIFEST), 'sg_manifest')


def _write_solver_manifest(sg, tmp_path, fmt, suffix):
    """Write an SG manifest with a solver model file and return the manifest path."""
    manifest = tmp_path / f'lam-{fmt}.sg.json'
    sgio.write(
        sg, str(manifest), 'sg_manifest',
        model_file=f'lam.{suffix}', model_file_format=fmt,
    )
    return manifest


def _edit_manifest(path, **changes):
    """Rewrite fields of a manifest file in place."""
    data = json.loads(path.read_text(encoding='utf-8'))
    data.update(changes)
    path.write_text(json.dumps(data), encoding='utf-8')


@pytest.mark.unit
class TestSolverManifestRoundTrip:
    """SwiftComp/VABS model files: write the manifest, read it back."""

    @pytest.mark.parametrize(('fmt', 'suffix'), [('swiftcomp', 'sc'), ('vabs', 'dat')])
    def test_round_trip_keeps_sg_fields(self, lam_sg, tmp_path, fmt, suffix):
        manifest = _write_solver_manifest(lam_sg, tmp_path, fmt, suffix)

        sg = sgio.read(str(manifest), 'sg_manifest')

        assert (sg.sgdim, sg.smdim, sg.analysis_config.model) == (2, 1, 0)
        assert sg.model_space == 'yz'
        assert (sg.nnodes, sg.nelems, sg.nmates) == (lam_sg.nnodes, lam_sg.nelems, lam_sg.nmates)

    def test_manifest_omits_blocks_owned_by_solver_file(self, lam_sg, tmp_path):
        manifest = _write_solver_manifest(lam_sg, tmp_path, 'swiftcomp', 'sc')

        data = json.loads(manifest.read_text(encoding='utf-8'))

        assert data == {
            'sg_manifest_version': 1,
            'model_file': {'path': 'lam.sc', 'format': 'swiftcomp', 'format_version': '2.1'},
            'sgdim': 2,
            'model_type': 'BM1',
        }

    @pytest.mark.parametrize(
        ('fmt', 'suffix', 'change', 'match'),
        [
            ('swiftcomp', 'sc', {'sgdim': 3}, 'sgdim'),
            ('swiftcomp', 'sc', {'model_type': 'BM2'}, 'model_type'),
            ('vabs', 'dat', {'model_type': 'BM2'}, 'model_type'),
        ],
    )
    def test_model_file_header_disagreeing_with_manifest(
        self, lam_sg, tmp_path, fmt, suffix, change, match
    ):
        manifest = _write_solver_manifest(lam_sg, tmp_path, fmt, suffix)
        _edit_manifest(manifest, **change)

        with pytest.raises(ValueError, match=f'model file {match}'):
            sgio.read(str(manifest), 'sg_manifest')

    def test_block_owned_by_solver_file(self, lam_sg, tmp_path):
        manifest = _write_solver_manifest(lam_sg, tmp_path, 'vabs', 'dat')
        _edit_manifest(manifest, model_space='yz')

        with pytest.raises(ValueError, match='owns'):
            sgio.read(str(manifest), 'sg_manifest')

    def test_solver_file_requires_format_version(self, lam_sg, tmp_path):
        manifest = _write_solver_manifest(lam_sg, tmp_path, 'vabs', 'dat')
        _edit_manifest(manifest, model_file={'path': 'lam.dat', 'format': 'vabs'})

        with pytest.raises(IncompleteModelDataError, match='format_version'):
            sgio.read(str(manifest), 'sg_manifest')


@pytest.mark.unit
class TestWriteSGManifestErrors:
    """Invalid manifest write requests fail before any file is written."""

    @pytest.mark.parametrize(
        ('arguments', 'match'),
        [
            ({'model_file_format': 'sc'}, 'model_file'),
            ({'model_file': 'lam.sc'}, 'model_file_format'),
            ({'model_file': 'lam.inp', 'model_file_format': 'abaqus'}, 'not supported'),
            ({'model_file': 'lam.sc', 'model_file_format': 'sc', 'model_type': 'PL1'},
             'disagrees'),
        ],
    )
    def test_invalid_request(self, lam_sg, tmp_path, arguments, match):
        manifest = tmp_path / 'lam.sg.json'

        with pytest.raises(ValueError, match=match):
            sgio.write(lam_sg, str(manifest), 'sg_manifest', **arguments)

        assert list(tmp_path.iterdir()) == []

    def test_absolute_model_file(self, lam_sg, tmp_path):
        with pytest.raises(ValueError, match='relative'):
            sgio.write(
                lam_sg, str(tmp_path / 'lam.sg.json'), 'sg_manifest',
                model_file=str(tmp_path / 'lam.sc'), model_file_format='sc',
            )
