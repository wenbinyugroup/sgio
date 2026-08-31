"""Unit tests for the SwiftComp output mapper."""

from __future__ import annotations

from io import StringIO

import numpy as np
import pytest

import sgio
from sgio.core.mesh import CellBlock, SGMesh
from sgio.iofunc.swiftcomp._swiftcomp import write_buffer
from sgio.iofunc.swiftcomp.mapper_out import map_structure_gene_to_write_payload


def _build_2d_structure_gene() -> sgio.StructureGene:
    """Build a minimal 2D SG whose mesh can be projected for SwiftComp export."""
    sg = sgio.StructureGene(sgdim=2)
    sg.mesh = SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        ),
        cells=[CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))],
        point_data={"node_id": np.array([4, 8, 12], dtype=int)},
        cell_data={
            "element_id": [np.array([9], dtype=int)],
            "property_id": [np.array([1], dtype=int)],
            "property_ref_csys": [
                np.array([[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
            ],
        },
    )
    sg.materials = {
        "matrix": sgio.CauchyContinuumModel(name="matrix", e1=1.0, nu12=0.3)
    }
    sg.mocombos[1] = ("matrix", 0.0)
    return sg


@pytest.mark.unit
def test_map_structure_gene_to_write_payload_owns_projected_export_mesh():
    """SwiftComp export must project a private mesh without changing the input SG."""
    sg = _build_2d_structure_gene()
    original_node_ids = sg.mesh.point_data["node_id"].copy()
    original_element_ids = sg.mesh.cell_data["element_id"][0].copy()
    original_csys = sg.mesh.cell_data["property_ref_csys"][0].copy()

    payload = map_structure_gene_to_write_payload(sg, model="pl1", model_space="xy")

    export_mesh = payload["sg"].mesh
    assert export_mesh is not sg.mesh
    assert export_mesh.points is sg.mesh.points
    assert export_mesh.cells[0] is sg.mesh.cells[0]
    assert not np.shares_memory(export_mesh.point_data["node_id"], sg.mesh.point_data["node_id"])
    assert not np.shares_memory(
        export_mesh.cell_data["element_id"][0],
        sg.mesh.cell_data["element_id"][0],
    )
    assert not np.shares_memory(
        export_mesh.cell_data["property_ref_csys"][0],
        sg.mesh.cell_data["property_ref_csys"][0],
    )
    np.testing.assert_allclose(
        export_mesh.cell_data["property_ref_csys"][0][0],
        [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
    )
    np.testing.assert_array_equal(sg.mesh.point_data["node_id"], original_node_ids)
    np.testing.assert_array_equal(sg.mesh.cell_data["element_id"][0], original_element_ids)
    np.testing.assert_allclose(sg.mesh.cell_data["property_ref_csys"][0], original_csys)


@pytest.mark.unit
def test_swiftcomp_write_does_not_renumber_or_project_input_mesh():
    """The mutating SwiftComp writer must receive only the private export mesh."""
    sg = _build_2d_structure_gene()
    original_node_ids = sg.mesh.point_data["node_id"].copy()
    original_element_ids = sg.mesh.cell_data["element_id"][0].copy()
    original_csys = sg.mesh.cell_data["property_ref_csys"][0].copy()

    write_buffer(sg, StringIO(), model="pl1", model_space="xy", version="2.1")

    np.testing.assert_array_equal(sg.mesh.point_data["node_id"], original_node_ids)
    np.testing.assert_array_equal(sg.mesh.cell_data["element_id"][0], original_element_ids)
    np.testing.assert_allclose(sg.mesh.cell_data["property_ref_csys"][0], original_csys)
