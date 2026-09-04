"""Phase 4 regression tests for the SG-on-Gmsh serialization contract."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np
import pytest

from sgio import (
    SGAnalysisConfig,
    convert,
    read,
    read_sg_from_gmsh_bundle,
    section_model_to_record,
    write,
    write_config_to_json,
    write_sections_to_json,
)
from sgio.model import CauchyContinuumModel


def _write_sections_sidecar(sg, path: Path) -> Path:
    """Write the bundle section sidecar carrying one structure gene's materials.

    A ``.msh`` holds mesh data only, so a VABS -> Gmsh -> VABS round trip has to
    carry the section payload alongside it; that sidecar is what makes the
    second leg readable.
    """
    write_sections_to_json(
        [
            section_model_to_record(
                sg.materials[section.material],
                name=section.material,
                id=section.property_id,
                orientation=section.orientation,
            )
            for section in sg.sections.values()
        ],
        path,
    )
    return path


def _remove_block(text: str, block_name: str) -> str:
    start = text.index(f"${block_name}")
    end = text.index(f"$End{block_name}") + len(f"$End{block_name}\n")
    return text[:start] + text[end:]


def _append_legacy_blocks(text: str) -> str:
    if not text.endswith("\n"):
        text += "\n"
    return (
        text
        + "$SGLayerDef\n"
        + "! nlayers\n"
        + "1\n"
        + "! layer_id material_id fiber_angle\n"
        + "1 1 45.0\n"
        + "$EndSGLayerDef\n"
        + "$SGConfig\n"
        + "! key value\n"
        + "sgdim 2\n"
        + "model 1\n"
        + "do_damping 1\n"
        + "thermal 1\n"
        + "$EndSGConfig\n"
    )


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
def test_vabs_gmsh_vabs_roundtrip_preserves_mesh_orientation_invariants(tmp_path: Path):
    """VABS -> Gmsh -> VABS should preserve the supported mesh/orientation invariants."""
    src = Path("tests/fixtures/vabs/version_4_1/isorect.sg")
    gmsh_path = tmp_path / "isorect.msh"
    roundtrip_path = tmp_path / "isorect_back.sg"

    source_sg = read(str(src), "vabs", format_version="4.1", model_type="BM2")
    convert(
        str(src),
        str(gmsh_path),
        "vabs",
        "gmsh",
        file_version_in="4.1",
        file_version_out="4.1",
        model_type="BM2",
    )
    sections_path = _write_sections_sidecar(source_sg, tmp_path / "isorect.sections.json")
    convert(
        str(gmsh_path),
        str(roundtrip_path),
        "gmsh",
        "vabs",
        file_version_in="4.1",
        file_version_out="4.1",
        model_type="BM2",
        sgdim=2,
        model_space="yz",
        sections_json=str(sections_path),
    )
    roundtrip_sg = read(str(roundtrip_path), "vabs", format_version="4.1", model_type="BM2")

    assert len(roundtrip_sg.mesh.cells) == len(source_sg.mesh.cells)
    assert [block.type for block in roundtrip_sg.mesh.cells] == [
        block.type for block in source_sg.mesh.cells
    ]
    np.testing.assert_allclose(roundtrip_sg.mesh.points, source_sg.mesh.points)
    np.testing.assert_array_equal(
        roundtrip_sg.mesh.cell_data["element_id"][0],
        source_sg.mesh.cell_data["element_id"][0],
    )
    np.testing.assert_array_equal(
        roundtrip_sg.mesh.cell_data["property_id"][0],
        source_sg.mesh.cell_data["property_id"][0],
    )
    np.testing.assert_allclose(
        roundtrip_sg.mesh.cell_data["property_ref_csys"][0],
        source_sg.mesh.cell_data["property_ref_csys"][0],
    )
    assert [
        (section.material, section.orientation, section.property_id)
        for section in roundtrip_sg.sections.values()
    ] == [
        (section.material, section.orientation, section.property_id)
        for section in source_sg.sections.values()
    ]


@pytest.mark.conversion
@pytest.mark.gmsh
def test_vabs_gmsh_bundle_roundtrip_preserves_material_payload_and_config(tmp_path: Path):
    """VABS -> Gmsh plus sidecars should reconstruct equivalent material/config payloads."""
    src = Path("tests/fixtures/vabs/version_4_1/isorect.sg")
    gmsh_path = tmp_path / "isorect.msh"
    sections_path = tmp_path / "sections.json"
    config_path = tmp_path / "config.json"

    source_sg = read(str(src), "vabs", format_version="4.1", model_type="BM2")
    source_sg.analysis_config = SGAnalysisConfig(
        analysis=1,
        physics=1,
        model=1,
        do_damping=1,
        is_temp_nonuniform=1,
    )
    write(source_sg, str(gmsh_path), "gmsh", format_version="4.1", model_type="BM2", binary=False)

    write_sections_to_json(
        [
            section_model_to_record(material, name=f"layer_{index}", id=index)
            for index, material in enumerate(source_sg.materials.values(), start=1)
        ],
        sections_path,
    )
    write_config_to_json(source_sg.analysis_config, config_path)

    assembled_sg = read_sg_from_gmsh_bundle(
        gmsh_path,
        sections_path,
        config_path,
        model_type="BM2",
    )

    assert asdict(assembled_sg.analysis_config) == asdict(source_sg.analysis_config)
    assert set(assembled_sg.materials) == {"layer_1"}
    np.testing.assert_allclose(
        assembled_sg.materials["layer_1"].model_dump()["stff"],
        next(iter(source_sg.materials.values())).model_dump()["stff"],
    )


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
def test_gmsh_enriched_to_vabs_to_gmsh_preserves_local_csys_fields(tmp_path: Path):
    """An enriched Gmsh mesh should keep canonical local-csys fields after re-export."""
    src = Path("tests/fixtures/gmsh/sg21_box_quad4_min_gmsh41.msh")
    sections = Path("tests/fixtures/gmsh/sections_sg21_box_quad4.json")
    vabs_path = tmp_path / "roundtrip.sg"
    gmsh_path = tmp_path / "roundtrip.msh"

    convert(
        str(src),
        str(vabs_path),
        "gmsh",
        "vabs",
        file_version_in="4.1",
        file_version_out="4.1",
        model_type="BM2",
        sgdim=2,
        model_space="xy",
        sections_json=str(sections),
    )
    roundtrip_sg = read(str(vabs_path), "vabs", format_version="4.1", model_type="BM2")
    write(roundtrip_sg, str(gmsh_path), "gmsh", format_version="4.1", model_type="BM2", binary=False)

    gmsh_text = gmsh_path.read_text(encoding="utf-8")
    assert '"element_local_csys"' in gmsh_text
    assert '"property_ref_axis_y1"' in gmsh_text
    assert "$SGLayerDef" not in gmsh_text
    assert "$SGConfig" not in gmsh_text


@pytest.mark.conversion
@pytest.mark.gmsh
def test_external_gmsh_bundle_reexport_preserves_original_physical_name(tmp_path: Path):
    """External Gmsh physical names should not be polluted by extra layer aliases."""
    src = Path("tests/fixtures/gmsh/sg21_box_quad4_min_gmsh41.msh")
    sections_path = tmp_path / "sections.json"
    config_path = tmp_path / "config.json"
    out_path = tmp_path / "out.msh"

    write_sections_to_json(
        [
            section_model_to_record(
                CauchyContinuumModel(name="frp", id=1, isotropy=0, e=1.0e9, nu=0.3)
            )
        ],
        sections_path,
    )
    write_config_to_json(SGAnalysisConfig(), config_path)

    sg = read_sg_from_gmsh_bundle(src, sections_path, config_path, model_type="BM2")
    write(sg, str(out_path), "gmsh", format_version="4.1", model_type="BM2", binary=False)

    text = out_path.read_text(encoding="utf-8")
    assert '2 1 "frp"' in text
    assert '2 1 "layer_1"' not in text


@pytest.mark.conversion
@pytest.mark.gmsh
def test_bundle_id_fallback_works_without_physical_names(tmp_path: Path, gmsh_test_files):
    """Bundle assembly should degrade to id matching when `$PhysicalNames` are absent."""
    src = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"
    stripped_path = tmp_path / "no_physical_names.msh"
    sections_path = tmp_path / "sections.json"

    stripped_path.write_text(
        _remove_block(src.read_text(encoding="utf-8"), "PhysicalNames"),
        encoding="utf-8",
    )
    write_sections_to_json(
        [
            section_model_to_record(
                CauchyContinuumModel(name="", id=1, isotropy=0, e=18.0e9, nu=0.33),
                id=1,
            )
        ],
        sections_path,
    )

    sg = read_sg_from_gmsh_bundle(stripped_path, sections_path, None, model_type="BM2")
    section = next(iter(sg.sections.values()))
    assert section.extras["bundle_match_source"] == "id"


@pytest.mark.conversion
@pytest.mark.gmsh
def test_legacy_sg_blocks_are_still_readable(tmp_path: Path, gmsh_test_files):
    """Legacy `$SGLayerDef` and `$SGConfig` blocks should still be accepted on read."""
    src = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"
    legacy_path = tmp_path / "legacy_blocks.msh"
    legacy_path.write_text(
        _append_legacy_blocks(src.read_text(encoding="utf-8")),
        encoding="utf-8",
    )

    sg = read_sg_from_gmsh_bundle(
        legacy_path,
        gmsh_test_files["root"] / "sections_sg21_box_quad4.json",
        None,
        model_type="BM2",
    )

    assert sg.analysis_config.model == 1
    assert sg.analysis_config.do_damping == 1
    assert sg.analysis_config.physics == 1
    assert sg.mocombos[1] == ("frp", 45.0)
