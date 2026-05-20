"""Unit tests for the Gmsh output mapper layer."""

from __future__ import annotations

import numpy as np
import pytest

import sgio
from sgio.core.mesh import CellBlock, SGMesh
from sgio.iofunc.gmsh.mapper_out import map_model_to_write_payload


def _build_triangle_mesh() -> SGMesh:
    """Build a minimal triangle mesh for writer-payload tests."""
    return SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))],
        cell_data={"property_id": [np.array([3], dtype=int)]},
    )


@pytest.mark.unit
def test_map_model_to_write_payload_supports_bare_mesh():
    """Bare mesh inputs should be forwarded with default Gmsh kwargs."""
    mesh = _build_triangle_mesh()

    payload = map_model_to_write_payload(mesh, format_version="2.2", binary=False)

    assert payload["mesh"] is mesh
    assert payload["format_version"] == "2.2"
    assert payload["binary"] is False
    assert payload["sgdim"] == 2


@pytest.mark.unit
def test_map_model_to_write_payload_extracts_structure_gene_metadata():
    """StructureGene inputs should export material combos and SG config."""
    sg = sgio.StructureGene()
    sg.sgdim = 2
    sg.smdim = 1
    sg.analysis_config.model = 0
    sg.analysis_config.do_damping = 1
    sg.analysis_config.physics = 1
    sg.mesh = _build_triangle_mesh()
    sg.materials["matrix"] = sgio.CauchyContinuumModel(name="matrix")
    sg.mocombos[3] = ("matrix", 45.0)

    payload = map_model_to_write_payload(sg, format_version="4.1", mesh_only=False)

    assert payload["mesh"] is sg.mesh
    assert payload["sgdim"] == 2
    assert payload["mesh_only"] is False
    assert payload["mocombos"] == {3: ("matrix", 45.0)}
    assert payload["material_id_map"] == {"matrix": 1}
    assert payload["sg_configs"] == {
        "sgdim": 2,
        "model": 0,
        "do_damping": 1,
        "thermal": 1,
    }
