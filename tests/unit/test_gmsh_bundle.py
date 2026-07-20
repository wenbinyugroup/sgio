from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from sgio.core import SGAnalysisConfig
from sgio.iofunc.gmsh.bundle import (
    read_config_from_json,
    read_sections_from_json,
    read_sg_from_gmsh_bundle,
    section_model_to_record,
    write_config_to_json,
    write_sections_to_json,
)
from sgio.model import CauchyContinuumModel, EulerBernoulliBeamModel


@pytest.mark.unit
def test_config_sidecar_roundtrip(tmp_path: Path):
    """Config sidecar should round-trip through SGAnalysisConfig serialization."""
    config = SGAnalysisConfig(
        analysis=1,
        physics=2,
        model=3,
        geo_correct=True,
        do_damping=1,
        is_temp_nonuniform=1,
        force_flag=7,
        steer_flag=8,
    )
    file_path = tmp_path / "config.json"

    write_config_to_json(config, file_path)
    raw_data = json.loads(file_path.read_text(encoding="utf-8"))
    restored = read_config_from_json(file_path)

    assert raw_data["analysis"] == 1
    assert "config" not in raw_data
    assert asdict(restored) == asdict(config)


@pytest.mark.unit
def test_read_config_from_json_accepts_legacy_wrapped_object(tmp_path: Path):
    """Config reader should remain compatible with the legacy wrapped schema."""
    file_path = tmp_path / "config.json"
    file_path.write_text(
        json.dumps(
            {
                "config": {
                    "analysis": 2,
                    "physics": 3,
                    "model": 4,
                    "geo_correct": True,
                    "do_damping": 1,
                    "is_temp_nonuniform": 0,
                    "force_flag": 5,
                    "steer_flag": 6,
                }
            }
        ),
        encoding="utf-8",
    )

    restored = read_config_from_json(file_path)

    assert restored.analysis == 2
    assert restored.physics == 3
    assert restored.model == 4


@pytest.mark.unit
def test_sections_sidecar_roundtrip_for_material_and_beam(tmp_path: Path):
    """Sections sidecar should reuse model serialization for supported payloads."""
    material = CauchyContinuumModel(name="frp", id=11, isotropy=0, e=20.0e9, nu=0.3)
    beam = EulerBernoulliBeamModel(name="beam_section", id=22, ea=12.5, gj=3.5)
    file_path = tmp_path / "sections.json"

    write_sections_to_json([material, beam], file_path)
    raw_data = json.loads(file_path.read_text(encoding="utf-8"))
    records = read_sections_from_json(file_path)

    assert len(records) == 2
    assert raw_data["sections"][0]["payload"]["model"] == "sd1"
    assert raw_data["sections"][0]["payload"]["elastic"]["e1"] == pytest.approx(20.0e9)
    assert raw_data["sections"][0]["payload"]["label"] == "11"
    assert records[0].kind == "material"
    assert records[0].theory == "cauchy_continuum"
    assert isinstance(records[0].payload, CauchyContinuumModel)
    assert records[0].payload.name == "frp"
    assert records[1].kind == "beam"
    assert records[1].theory == "euler_bernoulli_beam"
    assert isinstance(records[1].payload, EulerBernoulliBeamModel)
    assert records[1].payload.ea == pytest.approx(12.5)


@pytest.mark.unit
def test_read_sg_from_gmsh_bundle_prefers_name_match(tmp_path: Path, gmsh_test_files):
    """Bundle assembly should prefer physical-name matching over id fallback."""
    sections_path = tmp_path / "sections.json"
    config_path = tmp_path / "config.json"
    gmsh_path = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"

    matched_material = section_model_to_record(
        CauchyContinuumModel(name="frp", id=99, isotropy=0, e=30.0e9, nu=0.25)
    )
    wrong_id_material = section_model_to_record(
        CauchyContinuumModel(name="wrong_id_match", id=1, isotropy=0, e=1.0e9, nu=0.2)
    )
    write_sections_to_json([matched_material, wrong_id_material], sections_path)
    write_config_to_json(SGAnalysisConfig(model=1, physics=4), config_path)

    sg = read_sg_from_gmsh_bundle(gmsh_path, sections_path, config_path)

    section = next(iter(sg.sections.values()))
    assert section.material == "frp"
    assert section.extras["bundle_match_source"] == "name"
    assert "frp" in sg.materials
    assert sg.analysis_config.model == 1
    assert sg.analysis_config.physics == 4


@pytest.mark.unit
def test_read_sg_from_gmsh_bundle_falls_back_to_id(tmp_path: Path, gmsh_test_files):
    """Bundle assembly should fall back to id when no usable name match exists."""
    sections_path = tmp_path / "sections.json"
    gmsh_path = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"

    record = section_model_to_record(
        CauchyContinuumModel(name="", id=1, isotropy=0, e=18.0e9, nu=0.33),
        name=None,
        id=1,
    )
    write_sections_to_json([record], sections_path)

    sg = read_sg_from_gmsh_bundle(gmsh_path, sections_path, None)

    section = next(iter(sg.sections.values()))
    assert section.extras["bundle_match_source"] == "id"


@pytest.mark.unit
def test_read_sg_from_gmsh_bundle_accepts_top_level_material_list(
    tmp_path: Path,
    gmsh_test_files,
):
    """Bundle assembly should accept the standard top-level material record list."""
    sections_path = tmp_path / "sections.json"
    gmsh_path = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"
    payload = [
        {
            "name": "matrix",
            "model": "sd1",
            "label": "1",
            "isotropy": 0,
            "density": 1000.0,
            "temperature": 0.0,
            "elastic": {
                "e1": 1.0e9,
                "nu12": 0.3,
            },
        }
    ]
    sections_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    sg = read_sg_from_gmsh_bundle(gmsh_path, sections_path, None)

    section = next(iter(sg.sections.values()))
    assert section.material == "matrix"
    assert sg.materials["matrix"].e1 == pytest.approx(1.0e9)


@pytest.mark.unit
def test_read_sg_from_gmsh_bundle_rejects_duplicate_sidecar_ids(
    tmp_path: Path,
    gmsh_test_files,
):
    """Duplicate sidecar ids should raise instead of assembling ambiguously."""
    sections_path = tmp_path / "sections.json"
    gmsh_path = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"
    payload = {
        "sections": [
            {
                "kind": "material",
                "theory": "cauchy_continuum",
                "id": 1,
                "name": "mat_a",
                "payload": {"name": "mat_a", "id": 1, "isotropy": 0, "e1": 1.0, "nu12": 0.3},
            },
            {
                "kind": "material",
                "theory": "cauchy_continuum",
                "id": 1,
                "name": "mat_b",
                "payload": {"name": "mat_b", "id": 2, "isotropy": 0, "e1": 2.0, "nu12": 0.25},
            },
        ]
    }
    sections_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate section sidecar id"):
        read_sg_from_gmsh_bundle(gmsh_path, sections_path, None)


@pytest.mark.unit
def test_read_sg_from_gmsh_bundle_rejects_duplicate_sidecar_names(
    tmp_path: Path,
    gmsh_test_files,
):
    """Duplicate sidecar names should raise instead of assembling ambiguously."""
    sections_path = tmp_path / "sections.json"
    gmsh_path = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"
    payload = {
        "sections": [
            {
                "kind": "material",
                "theory": "cauchy_continuum",
                "id": 1,
                "name": "dup",
                "payload": {"name": "dup", "id": 1, "isotropy": 0, "e1": 1.0, "nu12": 0.3},
            },
            {
                "kind": "material",
                "theory": "cauchy_continuum",
                "id": 2,
                "name": "dup",
                "payload": {"name": "dup", "id": 2, "isotropy": 0, "e1": 2.0, "nu12": 0.25},
            },
        ]
    }
    sections_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate section sidecar name"):
        read_sg_from_gmsh_bundle(gmsh_path, sections_path, None)
