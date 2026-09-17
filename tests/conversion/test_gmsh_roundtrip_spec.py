"""Regression tests for the SG-on-Gmsh serialization contract (SG manifest)."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np
import pytest

from sgio import SGAnalysisConfig, convert, read, write

GMSH_DIR = Path("tests/fixtures/gmsh")
ISORECT = Path("tests/fixtures/vabs/version_4_1/isorect.sg")


def _remove_block(text: str, block_name: str) -> str:
    start = text.index(f"${block_name}")
    end = text.index(f"$End{block_name}") + len(f"$End{block_name}\n")
    return text[:start] + text[end:]


def _write_gmsh_manifest(sg, tmp_path: Path, stem: str) -> Path:
    """Write ``sg`` as a Gmsh model file plus its SG manifest."""
    manifest = tmp_path / f"{stem}.sg.json"
    write(
        sg, str(manifest), "sg_manifest", format_version="4.1",
        model_file=f"{stem}.msh", model_file_format="gmsh",
    )
    return manifest


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
def test_vabs_gmsh_vabs_roundtrip_preserves_mesh_orientation_invariants(tmp_path: Path):
    """VABS -> Gmsh manifest -> VABS should preserve mesh and section invariants."""
    roundtrip_path = tmp_path / "isorect_back.sg"

    source_sg = read(str(ISORECT), "vabs", format_version="4.1")
    manifest = _write_gmsh_manifest(source_sg, tmp_path, "isorect")
    convert(str(manifest), str(roundtrip_path), "sg_manifest", "vabs", file_version_out="4.1")
    roundtrip_sg = read(str(roundtrip_path), "vabs", format_version="4.1")

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
def test_gmsh_manifest_roundtrip_preserves_material_payload_and_config(tmp_path: Path):
    """VABS -> Gmsh manifest should reconstruct equivalent material/config payloads."""
    source_sg = read(str(ISORECT), "vabs", format_version="4.1")
    source_sg.analysis_config = SGAnalysisConfig(
        analysis=1,
        physics=1,
        model=source_sg.analysis_config.model,
        do_damping=1,
        is_temp_nonuniform=1,
    )

    manifest = _write_gmsh_manifest(source_sg, tmp_path, "isorect")
    assembled_sg = read(str(manifest), "sg_manifest")

    assert asdict(assembled_sg.analysis_config) == asdict(source_sg.analysis_config)
    assert set(assembled_sg.materials) == set(source_sg.materials)
    for name, material in source_sg.materials.items():
        np.testing.assert_allclose(
            assembled_sg.materials[name].model_dump()["stff"],
            material.model_dump()["stff"],
        )


@pytest.mark.conversion
@pytest.mark.gmsh
def test_gmsh_manifest_keeps_shared_materials_once(tmp_path: Path):
    """Sections sharing a material at different angles reference one material record."""
    source_sg = read("tests/fixtures/vabs/version_4_1/uh60a.sg", "vabs", format_version="4.1")

    manifest = _write_gmsh_manifest(source_sg, tmp_path, "uh60a")
    sg = read(str(manifest), "sg_manifest")

    assert set(sg.materials) == set(source_sg.materials)
    assert {section.material for section in sg.sections.values()} <= set(sg.materials)
    assert dict(sg.mocombos) == dict(source_sg.mocombos)


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
def test_gmsh_enriched_to_vabs_to_gmsh_preserves_local_csys_fields(tmp_path: Path):
    """An enriched Gmsh mesh should keep canonical local-csys fields after re-export."""
    vabs_path = tmp_path / "roundtrip.sg"
    gmsh_path = tmp_path / "roundtrip.msh"

    convert(
        str(GMSH_DIR / "sg21_box_quad4_min_gmsh41.sg.json"),
        str(vabs_path),
        "sg_manifest",
        "vabs",
        file_version_out="4.1",
    )
    roundtrip_sg = read(str(vabs_path), "vabs", format_version="4.1")
    write(roundtrip_sg, str(gmsh_path), "gmsh", format_version="4.1", binary=False)

    gmsh_text = gmsh_path.read_text(encoding="utf-8")
    assert '"element_local_csys"' in gmsh_text
    assert '"property_ref_axis_y1"' in gmsh_text
    assert "$SGLayerDef" not in gmsh_text
    assert "$SGConfig" not in gmsh_text


@pytest.mark.conversion
@pytest.mark.gmsh
def test_external_gmsh_reexport_preserves_original_physical_name(tmp_path: Path):
    """External Gmsh physical names should not be polluted by extra layer aliases."""
    out_path = tmp_path / "out.msh"

    sg = read(str(GMSH_DIR / "sg21_box_quad4_min_gmsh41.sg.json"), "sg_manifest")
    write(sg, str(out_path), "gmsh", format_version="4.1", binary=False)

    text = out_path.read_text(encoding="utf-8")
    assert '2 1 "frp"' in text
    assert '2 1 "layer_1"' not in text


@pytest.mark.conversion
@pytest.mark.gmsh
def test_section_id_fallback_works_without_physical_names(tmp_path: Path, copy_manifest):
    """Sections match by id when `$PhysicalNames` are absent."""
    manifest = copy_manifest(
        GMSH_DIR / "sg21_box_quad4_min_gmsh41.sg.json",
        sections=[{"id": 1, "material": "frp"}],
    )
    msh = tmp_path / "sg21_box_quad4_min_gmsh41.msh"
    msh.write_text(_remove_block(msh.read_text(encoding="utf-8"), "PhysicalNames"),
                   encoding="utf-8")

    sg = read(str(manifest), "sg_manifest")

    section = next(iter(sg.sections.values()))
    assert section.material == "frp"
    assert section.extras["section_match_source"] == "id"
