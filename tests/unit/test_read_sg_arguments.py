"""Tests for the SG arguments of ``sgio.read`` without an SG manifest."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import sgio
from sgio._exceptions import IncompleteModelDataError

FIXTURE_DIR = Path(__file__).parents[1] / 'fixtures'
ABAQUS_2D = FIXTURE_DIR / 'abaqus' / 'sg2_min.inp'
LAM_DIR = FIXTURE_DIR / 'abaqus'
VABS_2D = FIXTURE_DIR / 'vabs' / 'version_4_1' / 'isorect.sg'


@pytest.mark.unit
class TestRequiredArguments:
    """No SG argument falls back to a default."""

    @pytest.mark.parametrize(
        ('arguments', 'missing'),
        [
            ({'model_type': 'PL1', 'model_space': 'xy'}, 'sgdim'),
            ({'sgdim': 2, 'model_type': 'PL1'}, 'model_space'),
        ],
    )
    def test_abaqus_requires_sg_arguments(self, arguments, missing):
        with pytest.raises(IncompleteModelDataError, match=missing):
            sgio.read(str(ABAQUS_2D), 'abaqus', **arguments)

    def test_abaqus_model_type_deferred_to_write(self, tmp_path):
        """An Abaqus SG read without model_type needs it at write time."""
        sg = sgio.read(str(ABAQUS_2D), 'abaqus', sgdim=2, model_space='xy')
        assert sg.smdim is None

        with pytest.raises(IncompleteModelDataError, match='smdim'):
            sgio.write(sg, str(tmp_path / 'no_model.sc'), 'sc')

        sc_file = tmp_path / 'pl2.sc'
        sgio.write(sg, str(sc_file), 'sc', model_type='PL2')
        assert sc_file.read_text().split()[0] == '1'

    def test_swiftcomp_requires_model_type(self, tmp_path):
        sc_file = tmp_path / 'isorect.sc'
        sg = sgio.read(str(VABS_2D), 'vabs', format_version='4.1')
        sgio.write(sg, str(sc_file), 'sc', model_type='BM1')

        with pytest.raises(IncompleteModelDataError, match='model_type'):
            sgio.read(str(sc_file), 'sc')


@pytest.mark.unit
class TestFormatDefinedModelSpace:
    """VABS and SwiftComp inputs define the model space themselves."""

    def test_vabs_read_sets_yz(self):
        sg = sgio.read(str(VABS_2D), 'vabs', format_version='4.1')

        assert sg.model_space == 'yz'

    def test_model_space_argument_rejected_for_vabs(self):
        with pytest.raises(ValueError, match='do not pass model_space'):
            sgio.read(str(VABS_2D), 'vabs', format_version='4.1', model_space='yz')

    def test_vabs_to_vabs_keeps_coordinates(self, tmp_path):
        out = tmp_path / 'isorect.sg'

        source = sgio.convert(str(VABS_2D), str(out), 'vabs', 'vabs', file_version_in='4.1')
        result = sgio.read(str(out), 'vabs', format_version='4.1')

        np.testing.assert_allclose(result.mesh.points, source.mesh.points)


@pytest.mark.unit
def test_arguments_and_manifest_write_the_same_swiftcomp_input(tmp_path):
    from_manifest = tmp_path / 'manifest.sc'
    from_arguments = tmp_path / 'arguments.sc'

    sgio.convert(str(LAM_DIR / 'sg2d-user-lam.sg.json'), str(from_manifest), 'sg_manifest', 'sc')
    sg = sgio.read(
        str(LAM_DIR / 'sg2d-user-lam.inp'), 'abaqus',
        sgdim=2, model_type='BM1', model_space='yz',
    )
    sgio.write(sg, str(from_arguments), 'sc', model_type='BM1')

    assert from_arguments.read_text() == from_manifest.read_text()
