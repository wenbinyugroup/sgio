"""Tests for SGAnalysisConfig and StructureGene analysis proxies."""

import pytest

import sgio
from sgio.core import SGAnalysisConfig


@pytest.mark.unit
def test_sg_analysis_config_is_independently_usable():
    """SGAnalysisConfig should work as a standalone pure config object."""
    config = SGAnalysisConfig(
        analysis=1,
        physics=2,
        model=3,
        geo_correct=True,
        do_damping=1,
        is_temp_nonuniform=1,
        force_flag=4,
        steer_flag=5,
    )

    assert config.analysis == 1
    assert config.physics == 2
    assert config.model == 3
    assert config.geo_correct is True
    assert config.do_damping == 1
    assert config.is_temp_nonuniform == 1
    assert config.force_flag == 4
    assert config.steer_flag == 5


@pytest.mark.unit
def test_structure_gene_analysis_proxies_forward_to_analysis_config():
    """Legacy StructureGene config fields should proxy to analysis_config."""
    sg = sgio.StructureGene()

    sg.analysis = 2
    sg.physics = 1
    sg.model = 3
    sg.geo_correct = True
    sg.do_damping = 7
    sg.is_temp_nonuniform = 8
    sg.force_flag = 9
    sg.steer_flag = 10

    assert isinstance(sg.analysis_config, SGAnalysisConfig)
    assert sgio.SGAnalysisConfig is SGAnalysisConfig
    assert sg.analysis_config.analysis == 2
    assert sg.analysis_config.physics == 1
    assert sg.analysis_config.model == 3
    assert sg.analysis_config.geo_correct is True
    assert sg.analysis_config.do_damping == 7
    assert sg.analysis_config.is_temp_nonuniform == 8
    assert sg.analysis_config.force_flag == 9
    assert sg.analysis_config.steer_flag == 10

    sg.analysis_config = SGAnalysisConfig(analysis=5, physics=6, model=7, do_damping=8)

    assert sg.analysis == 5
    assert sg.physics == 6
    assert sg.model == 7
    assert sg.do_damping == 8
