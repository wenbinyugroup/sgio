"""Unit tests for the Gmsh parser layer."""

from __future__ import annotations

import pytest

import sgio
from sgio.iofunc.gmsh.parser import _resolve_reader, parse_input_buffer


@pytest.mark.unit
def test_parse_input_buffer_reads_gmsh41_fixture(gmsh_test_files):
    """Parser should return raw header metadata and the parsed mesh."""
    fixture = gmsh_test_files["root"] / "sg21_box_quad4_min_gmsh41.msh"

    with open(fixture, "rb") as file:
        payload = parse_input_buffer(file, format_version="4.1")

    assert payload["requested_format_version"] == "4.1"
    assert payload["format_version"] == "4.1"
    assert payload["data_size"] == 8
    assert payload["is_ascii"] is True
    assert len(payload["mesh"].points) > 0
    assert "property_id" in payload["mesh"].cell_data
    assert "element_local_csys" in payload["mesh"].cell_data
    assert "property_ref_csys" in payload["mesh"].cell_data


@pytest.mark.unit
@pytest.mark.parametrize(
    "format_version, expected_module",
    [
        ("2", "_gmsh22"),
        ("2.2", "_gmsh22"),
        ("4", "_gmsh40"),
        ("4.0", "_gmsh40"),
        ("4.1", "_gmsh41"),
    ],
)
def test_resolve_reader_dispatches_on_exact_version(format_version, expected_module):
    """MSH 4.0 declares itself as "4" and must not reach the 4.1 reader."""
    reader = _resolve_reader(format_version)

    assert reader.__name__.rsplit(".", 1)[-1] == expected_module


@pytest.mark.unit
def test_resolve_reader_falls_back_to_newest_minor_version():
    """An unknown minor version resolves to the newest reader of that major."""
    assert _resolve_reader("4.2").__name__.rsplit(".", 1)[-1] == "_gmsh41"


@pytest.mark.unit
def test_resolve_reader_rejects_unknown_major_version():
    """An unsupported major version is reported rather than mis-parsed."""
    with pytest.raises(ValueError, match="Need mesh format"):
        _resolve_reader("3.0")


@pytest.mark.unit
def test_parse_input_buffer_reads_gmsh40_fixture(gmsh_test_files):
    """A MSH 4.0 file parses to the same counts native Gmsh reports.

    Regression for the ``$Entities`` parse failure: MSH 4.0 point entities
    carry a 6-double bounding box where 4.1 carries 3 coordinates, so parsing
    a 4.0 file with the 4.1 reader desynchronises on the first point entity.
    """
    fixture = gmsh_test_files["root"] / "sg33_tpms_entities_parse_bug.msh"

    with open(fixture, "rb") as file:
        payload = parse_input_buffer(file, format_version="4.1")

    mesh = payload["mesh"]

    assert payload["format_version"] == "4"
    # Counts cross-checked against the native Gmsh Python API for this file.
    assert len(mesh.points) == 10841
    assert sum(len(cell_block.data) for cell_block in mesh.cells) == 35288
    assert {cell_block.type for cell_block in mesh.cells} == {"tetra"}
    assert mesh.field_data["Mat0"].tolist() == [1, 3]
    # SG post-processing must run for 4.0 exactly as it does for 4.1.
    assert "property_id" in mesh.cell_data


@pytest.mark.unit
def test_read_gmsh40_mesh_into_structure_gene(gmsh_test_files):
    """The full read path yields a SG with the expected node/element counts."""
    fixture = gmsh_test_files["root"] / "sg33_tpms_entities_parse_bug.msh"
    sections = gmsh_test_files["root"] / "sections_sg33_tpms.json"

    sg = sgio.read_sg_from_gmsh_bundle(fixture, sections, model_type="SD1")

    assert sg.nnodes == 10841
    assert sg.nelems == 35288
    assert list(sg.materials.keys()) == ["Mat0"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "fixture_name, format_version",
    [
        ("sg33_cube_tetra4_min_gmsh41.msh", "4.1"),
        ("sg33_cube_tetra4_min_gmsh40.msh", "4.0"),
        ("sg33_cube_tetra4_min_gmsh22.msh", "2.2"),
    ],
)
def test_gmsh_versions_read_into_the_same_mesh_ir(
    gmsh_test_files, fixture_name, format_version, tmp_path
):
    """The same cube mesh must read identically regardless of $MeshFormat.

    Regression for the 2.2 read path returning a raw ``meshio.Mesh`` instead
    of the ``SGMesh`` every other version yields, which crashed the
    SwiftComp writer on the missing ``cell_point_data`` attribute.
    """
    from sgio.core.mesh import SGMesh

    fixture = gmsh_test_files["root"] / fixture_name

    sg = sgio.read_sg_from_gmsh_bundle(
        fixture,
        gmsh_test_files["root"] / "sections_sg33_cube_tetra4.json",
        model_type="SD1",
        format_version=format_version,
    )

    assert type(sg.mesh) is SGMesh
    assert sg.nnodes == 8
    assert sg.nelems == 6
    assert list(sg.materials.keys()) == ["matrix"]

    # Must be writable, not just readable -- this is where 2.2 used to crash.
    sgio.write(
        sg=sg, filename=str(tmp_path / f"{fixture_name}.sc"), file_format="sc",
        format_version="2.1", model_type="SD1",
    )
