"""Tests for merging section files by layout."""

from __future__ import annotations

from pathlib import Path

import meshio
import numpy as np
import pytest
from meshio import CellBlock

import sgio
from sgio import (
    merge_sections,
    merge_sections_from_csv,
    read_section_layout_csv,
    write_merged_sections,
)
from sgio.core.mesh import SGMesh


def _write_triangle_mesh(
    file_path: Path,
    physical_tag: int,
    geometrical_tag: int,
    field_name: str,
) -> None:
    """Create a simple one-element Gmsh mesh fixture."""
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    cells = [CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))]
    cell_data = {
        "gmsh:physical": [np.array([physical_tag], dtype=int)],
        "gmsh:geometrical": [np.array([geometrical_tag], dtype=int)],
    }
    field_data = {field_name: np.array([physical_tag, 2], dtype=int)}
    mesh = SGMesh(points=points, cells=cells, cell_data=cell_data, field_data=field_data)
    meshio.write(file_path, mesh, file_format="gmsh22")


@pytest.mark.io
@pytest.mark.gmsh
def test_merge_section_meshes_from_csv_writes_output(temp_dir):
    """Merge two section meshes and write the merged result."""
    mesh_dir = temp_dir / "cs"
    mesh_dir.mkdir()
    _write_triangle_mesh(mesh_dir / "section_a.msh", 11, 7, "skin")
    _write_triangle_mesh(mesh_dir / "section_b.msh", 22, 7, "web")

    csv_file = temp_dir / "blade.csv"
    csv_file.write_text("location,cs\n0.0,section_a\n2.5,section_b\n", encoding="utf-8")

    output_file = temp_dir / "blade_merged.msh"
    merged = merge_sections_from_csv(
        csv_file=csv_file,
        section_dir=mesh_dir,
        input_format="gmsh",
        output_file=output_file,
        output_format="gmsh22",
    )

    assert output_file.exists()
    assert len(merged.points) == 6
    assert len(merged.cells) == 2

    np.testing.assert_allclose(merged.points[:3, 0], np.array([0.0, 1.0, 0.0]))
    np.testing.assert_allclose(merged.points[3:, 0], np.array([2.5, 3.5, 2.5]))
    np.testing.assert_array_equal(merged.cells[1].data, np.array([[3, 4, 5]]))

    np.testing.assert_array_equal(merged.cell_data["gmsh:physical"][0], np.array([11]))
    np.testing.assert_array_equal(merged.cell_data["gmsh:physical"][1], np.array([22]))
    np.testing.assert_array_equal(merged.cell_data["property_id"][0], np.array([11]))
    np.testing.assert_array_equal(merged.cell_data["property_id"][1], np.array([22]))

    assert int(merged.cell_data["gmsh:geometrical"][0][0]) == 7
    assert int(merged.cell_data["gmsh:geometrical"][1][0]) == 8

    np.testing.assert_array_equal(merged.field_data["skin"], np.array([11, 2]))
    np.testing.assert_array_equal(merged.field_data["web"], np.array([22, 2]))


@pytest.mark.io
@pytest.mark.gmsh
def test_read_layout_and_resolve_unique_prefix_match(temp_dir):
    """Resolve a section name by unique prefix when the exact filename is absent."""
    mesh_dir = temp_dir / "cs"
    mesh_dir.mkdir()
    _write_triangle_mesh(mesh_dir / "sta-01-0000-refined.msh", 3, 1, "layer")

    csv_file = temp_dir / "blade.csv"
    csv_file.write_text("location,cs\n1.25,sta-01-0000\n", encoding="utf-8")

    layout = read_section_layout_csv(csv_file)
    assert layout == [(1.25, "sta-01-0000")]

    merged = merge_sections(layout, section_dir=mesh_dir, input_format="gmsh")

    assert len(merged.points) == 3
    np.testing.assert_allclose(merged.points[:, 0], np.array([1.25, 2.25, 1.25]))


@pytest.mark.io
@pytest.mark.gmsh
@pytest.mark.vabs
def test_merge_sections_accepts_vabs_input_by_default(test_data_dir):
    """Merge VABS section files by reading SG input directly."""
    mesh_dir = test_data_dir / "vabs" / "version_4_0"
    source_file = mesh_dir / "sg21eb_tri3_vabs40.sg"

    source_sg = sgio.read(str(source_file), "vabs")
    source_prop_ids = source_sg.mesh.cell_data["property_id"][0]

    merged = merge_sections(
        [(0.0, "sg21eb_tri3_vabs40"), (3.0, "sg21eb_tri3_vabs40")],
        section_dir=mesh_dir,
    )

    assert len(merged.points) == len(source_sg.mesh.points) * 2
    assert len(merged.cells) == 2
    np.testing.assert_array_equal(merged.cell_data["gmsh:physical"][0], source_prop_ids)
    np.testing.assert_array_equal(merged.cell_data["property_id"][1], source_prop_ids)
    assert "layer_1" in merged.field_data
    assert "layer_7" in merged.field_data


@pytest.mark.io
@pytest.mark.gmsh
@pytest.mark.swiftcomp
def test_merge_sections_accepts_swiftcomp_input(test_data_dir):
    """Merge SwiftComp section files by reading SG input directly."""
    mesh_dir = test_data_dir / "swiftcomp"
    source_file = mesh_dir / "sg21eb_tri6_sc21.sg"

    source_sg = sgio.read(str(source_file), "swiftcomp", model_type="bm1")

    merged = merge_sections(
        [(0.0, "sg21eb_tri6_sc21"), (1.0, "sg21eb_tri6_sc21")],
        section_dir=mesh_dir,
        input_format="swiftcomp",
        model_type="bm1",
    )

    assert len(merged.points) == len(source_sg.mesh.points) * 2
    assert len(merged.cells) == 2
    np.testing.assert_array_equal(
        merged.cell_data["gmsh:physical"][0],
        source_sg.mesh.cell_data["property_id"][0],
    )
    assert "layer_1" in merged.field_data


@pytest.mark.io
def test_write_merged_sections_supports_mesh_output_formats(test_data_dir, temp_dir):
    """Write a merged visualization mesh to a non-Gmsh mesh format."""
    merged = merge_sections(
        [(0.0, "sg21eb_tri3_vabs40"), (3.0, "sg21eb_tri3_vabs40")],
        section_dir=test_data_dir / "vabs" / "version_4_0",
    )

    output_file = temp_dir / "merged_sections.inp"
    write_merged_sections(merged, output_file, output_format="abaqus")

    assert output_file.exists()
    assert output_file.stat().st_size > 0


@pytest.mark.io
@pytest.mark.gmsh
def test_write_merged_sections_writes_ascii_element_data_scalars(temp_dir):
    """Write ASCII Gmsh ElementData without NumPy scalar repr strings."""
    mesh = SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))],
        cell_data={
            "gmsh:physical": [np.array([1], dtype=np.int32)],
            "gmsh:geometrical": [np.array([1], dtype=np.int32)],
            "property_id": [np.array([1], dtype=np.int32)],
            "element_id": [np.array([1], dtype=np.int32)],
        },
    )

    output_file = temp_dir / "element_data_ascii.msh"
    write_merged_sections(mesh, output_file, output_format="gmsh22")

    text = output_file.read_text(encoding="utf-8")
    assert "$MeshFormat\n2.2 0 8" in text
    assert '"element_id"' in text
    assert "1 np.int32(1)" not in text
    assert "1 1.0" not in text
    assert "1 1\n" in text


@pytest.mark.io
@pytest.mark.vabs
def test_write_merged_sections_supports_vabs_output(test_data_dir, temp_dir):
    """Write a merged section mesh to VABS format."""
    merged = merge_sections(
        [(0.0, "sg21eb_tri3_vabs40"), (3.0, "sg21eb_tri3_vabs40")],
        section_dir=test_data_dir / "vabs" / "version_4_0",
    )

    output_file = temp_dir / "merged_sections.sg"
    write_merged_sections(merged, output_file, output_format="vabs")

    assert output_file.exists()
    assert output_file.stat().st_size > 0
