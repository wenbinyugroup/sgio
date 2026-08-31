"""Integration tests for VTK/VTU mesh-only export."""

from __future__ import annotations

import numpy as np
import pytest

import sgio
from sgio.core.mesh import SGMesh
from sgio.core.sg import StructureGene


def _sample_structure_gene() -> StructureGene:
    """Build a structure gene with mesh-bound data for VTK output."""
    local_csys = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    mesh = SGMesh(
        points=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]]
        ),
        cells=[
            ("triangle", np.array([[0, 1, 2]], dtype=int)),
            ("triangle", np.array([[1, 3, 2]], dtype=int)),
        ],
        point_data={"node_id": np.array([10, 20, 30, 40], dtype=int)},
        cell_data={
            "element_id": [np.array([101], dtype=int), np.array([102], dtype=int)],
            "property_id": [np.array([1], dtype=int), np.array([2], dtype=int)],
            "element_local_csys": [np.array([local_csys]), np.array([local_csys])],
        },
    )
    sg = StructureGene(name="vtk_export", sgdim=2)
    sg.mesh = mesh
    return sg


@pytest.mark.integration
@pytest.mark.parametrize("file_format", ["vtk", "vtu"])
def test_public_write_exports_mesh_data_for_external_vtk_consumers(tmp_path, file_format):
    """Public export must produce files meshio can consume without sgio reading them."""
    import meshio

    sg = _sample_structure_gene()
    output_path = tmp_path / f"mesh.{file_format}"

    result = sgio.write(sg, str(output_path), file_format=file_format)
    exported = meshio.read(output_path, file_format=file_format)

    assert result == str(output_path)
    assert output_path.is_file()
    np.testing.assert_allclose(exported.points, sg.mesh.points)
    # VTK combines adjacent blocks with the same cell type. Its one triangle
    # block must still carry the original connectivity and aligned cell arrays.
    assert [block.type for block in exported.cells] == ["triangle"]
    np.testing.assert_array_equal(
        exported.cells[0].data,
        np.vstack([block.data for block in sg.mesh.cells]),
    )
    np.testing.assert_array_equal(exported.point_data["node_id"], sg.mesh.point_data["node_id"])
    for field_name in ("element_id", "property_id", "element_local_csys"):
        np.testing.assert_allclose(
            exported.cell_data[field_name][0],
            np.concatenate(sg.mesh.cell_data[field_name]),
        )


@pytest.mark.integration
def test_public_read_reports_that_vtu_is_write_only(tmp_path):
    """VTU input remains deliberately outside this implementation phase."""
    with pytest.raises(ValueError, match="supports writing only"):
        sgio.read(str(tmp_path / "input.vtu"), file_format="vtu")
