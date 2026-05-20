"""Tests for the VABS output mapper."""

from __future__ import annotations

import numpy as np
import pytest

import sgio
from sgio.core.mesh import CellBlock, SGMesh
from sgio.iofunc.vabs.mapper_out import map_structure_gene_to_write_payload


@pytest.mark.unit
def test_map_structure_gene_to_write_payload_resolves_stale_combo_name_from_field_data():
    """VABS export should recover combo material names from mesh field data."""
    sg = sgio.StructureGene()
    sg.sgdim = 2
    sg.smdim = 1
    sg.analysis_config.model = 0
    sg.mesh = SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))],
        cell_data={"property_id": [np.array([1], dtype=int)]},
        field_data={"matrix": np.array([1, 2], dtype=int)},
    )
    sg.materials = {
        "matrix": sgio.CauchyContinuumModel(name="matrix"),
    }
    sg.mocombos[1] = ("Material_1", 0.0)

    payload = map_structure_gene_to_write_payload(sg)

    assert payload["material_id_map"] == {"matrix": 1}
    assert payload["material_combos"] == [
        {
            "combo_id": 1,
            "material_id": 1,
            "angle": pytest.approx(0.0),
        }
    ]


@pytest.mark.unit
def test_map_structure_gene_to_write_payload_falls_back_when_field_dim_differs():
    """VABS export should still use field-data names when SG dim metadata is stale."""
    sg = sgio.StructureGene()
    sg.sgdim = 3
    sg.smdim = 1
    sg.analysis_config.model = 0
    sg.mesh = SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))],
        cell_data={"property_id": [np.array([1], dtype=int)]},
        field_data={"matrix": np.array([1, 2], dtype=int)},
    )
    sg.materials = {
        "matrix": sgio.CauchyContinuumModel(name="matrix"),
    }
    sg.mocombos[1] = ("Material_1", 0.0)

    payload = map_structure_gene_to_write_payload(sg)

    assert payload["material_combos"][0]["material_id"] == 1
