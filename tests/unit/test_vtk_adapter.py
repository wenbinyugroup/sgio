"""Unit tests for the write-only VTK/VTU format adapter."""

from __future__ import annotations

from io import BytesIO

import numpy as np
import pytest

from sgio.core.mesh import SGMesh
from sgio.iofunc.base import get_format_registry
from sgio.iofunc.vtk.adapter import VtkWriter
from sgio.iofunc.vtk.mapper_out import map_model_to_write_payload


def _sample_mesh() -> SGMesh:
    """Build a mesh with node, element, and local-coordinate data."""
    local_csys = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    return SGMesh(
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


@pytest.mark.unit
@pytest.mark.parametrize("file_format", ["vtk", "vtu"])
def test_vtk_writer_is_registered_without_a_reader(file_format):
    """VTK and VTU must be explicit write-only registry formats."""
    registry = get_format_registry()

    assert isinstance(registry.get_writer(file_format), VtkWriter)
    assert registry.get_reader(file_format) is None


@pytest.mark.unit
@pytest.mark.parametrize("field_name", ["cell_point_data", "point_sets", "cell_sets"])
def test_vtk_mapper_rejects_mesh_data_without_a_vtk_contract(field_name):
    """Set and element-nodal data must not be silently lost during export."""
    mesh = _sample_mesh()
    if field_name == "cell_point_data":
        mesh.cell_point_data = {"stress": [np.zeros((1, 3, 1)), np.zeros((1, 3, 1))]}
    elif field_name == "point_sets":
        mesh.point_sets = {"boundary": np.array([0, 1])}
    else:
        mesh.cell_sets = {"ALL_ELEMENTS": [101, 102]}

    with pytest.raises(ValueError, match=field_name):
        map_model_to_write_payload(mesh, file_format="vtu")


@pytest.mark.unit
def test_vtk_writer_rejects_an_unsupported_file_format():
    """The writer must only own the two registered VTK output formats."""
    with pytest.raises(ValueError, match="Unsupported VTK output format"):
        VtkWriter("ply")


@pytest.mark.unit
def test_vtu_writer_rejects_file_buffers_that_meshio_cannot_write():
    """VTU export must fail clearly instead of leaking meshio's path error."""
    destination = BytesIO()

    with pytest.raises(TypeError, match="filesystem path"):
        VtkWriter("vtu").write_input(destination, _sample_mesh())
