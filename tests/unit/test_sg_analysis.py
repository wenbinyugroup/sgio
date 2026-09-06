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
def test_structure_gene_config_lives_only_on_analysis_config():
    """Analysis config is owned solely by ``analysis_config`` (0.9 removal)."""
    sg = sgio.StructureGene()

    assert isinstance(sg.analysis_config, SGAnalysisConfig)
    assert sgio.SGAnalysisConfig is SGAnalysisConfig

    sg.analysis_config = SGAnalysisConfig(analysis=5, physics=6, model=7, do_damping=8)

    assert sg.analysis_config.analysis == 5
    assert sg.analysis_config.physics == 6
    assert sg.analysis_config.model == 7
    assert sg.analysis_config.do_damping == 8


@pytest.mark.unit
@pytest.mark.parametrize(
    "name",
    [
        "analysis", "physics", "model", "geo_correct",
        "do_damping", "is_temp_nonuniform", "force_flag", "steer_flag",
    ],
)
def test_legacy_structure_gene_config_proxies_are_removed(name):
    """The 0.8 legacy proxies were removed in 0.9; reading one must fail loudly."""
    sg = sgio.StructureGene()

    with pytest.raises(AttributeError):
        getattr(sg, name)
