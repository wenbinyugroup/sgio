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


@pytest.mark.unit
def test_map_structure_gene_to_write_payload_filters_non_section_cells():
    """VABS export should drop vertex/line entities from a Gmsh section mesh."""
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
                [2.0, 0.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[
            CellBlock("vertex", np.array([[3]], dtype=int)),
            CellBlock("line", np.array([[0, 3]], dtype=int)),
            CellBlock("triangle", np.array([[0, 1, 2]], dtype=int)),
        ],
        point_data={"node_id": np.array([1, 2, 3, 4], dtype=int)},
        cell_data={
            "property_id": [
                np.array([9], dtype=int),
                np.array([8], dtype=int),
                np.array([1], dtype=int),
            ]
        },
        field_data={"matrix": np.array([1, 2], dtype=int)},
    )
    sg.materials = {"matrix": sgio.CauchyContinuumModel(name="matrix")}
    sg.mocombos[1] = ("matrix", 0.0)

    payload = map_structure_gene_to_write_payload(sg)
    export_mesh = payload["mesh"]

    assert [cell_block.type for cell_block in export_mesh.cells] == ["triangle"]
    assert payload["header"]["nnode"] == 3
    assert payload["header"]["nelem"] == 1
    np.testing.assert_array_equal(export_mesh.point_data["node_id"], np.array([1, 2, 3]))
    np.testing.assert_array_equal(export_mesh.cell_data["property_id"][0], np.array([1]))


def _build_two_layer_sg_with_rotation_fields(
    rotation_values: dict[str, list[float]],
) -> "sgio.StructureGene":
    """Build a 2-element SG with controllable additional_rotation_{1,2,3} fields."""
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
                [1.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[
            CellBlock(
                "triangle", np.array([[0, 1, 2], [1, 3, 2]], dtype=int)
            )
        ],
        cell_data={
            "property_id": [np.array([1, 2], dtype=int)],
            "additional_rotation_1": [
                np.asarray(rotation_values.get("additional_rotation_1", [0.0, 0.0]))
            ],
            "additional_rotation_2": [
                np.asarray(rotation_values.get("additional_rotation_2", [0.0, 0.0]))
            ],
            "additional_rotation_3": [
                np.asarray(rotation_values.get("additional_rotation_3", [0.0, 0.0]))
            ],
        },
    )
    sg.materials = {"mat": sgio.CauchyContinuumModel(name="mat")}
    sg.mocombos[1] = ("mat", 0.0)
    sg.mocombos[2] = ("mat", 0.0)
    return sg


@pytest.mark.unit
@pytest.mark.parametrize(
    ("model_space", "rotation_field"),
    [
        ("xy", "additional_rotation_2"),
        ("yz", "additional_rotation_3"),
        ("zx", "additional_rotation_1"),
    ],
)
def test_theta_3_is_picked_from_rotation_field_matching_model_space(
    model_space, rotation_field
):
    """The VABS layer angle should come from the rotation field tied to model_space."""
    sg = _build_two_layer_sg_with_rotation_fields({rotation_field: [30.0, -15.0]})

    payload = map_structure_gene_to_write_payload(sg, model_space=model_space)

    combos = {record["combo_id"]: record["angle"] for record in payload["material_combos"]}
    assert combos == {1: pytest.approx(30.0), 2: pytest.approx(-15.0)}


@pytest.mark.unit
def test_other_rotation_fields_do_not_leak_into_theta_3_for_xy_space():
    """Only the rotation field tied to ``model_space`` should drive ``theta_3``."""
    sg = _build_two_layer_sg_with_rotation_fields(
        {
            "additional_rotation_1": [11.0, 22.0],
            "additional_rotation_3": [33.0, 44.0],
        }
    )

    payload = map_structure_gene_to_write_payload(sg, model_space="xy")

    combos = {record["combo_id"]: record["angle"] for record in payload["material_combos"]}
    # additional_rotation_2 is all zeros, so theta_3 should be 0 for both layers.
    assert combos == {1: pytest.approx(0.0), 2: pytest.approx(0.0)}


@pytest.mark.unit
def test_theta_3_aggregation_rejects_mixed_values_in_one_property():
    """Each VABS layer requires a single ``theta_3`` per ``property_id``."""
    sg = sgio.StructureGene()
    sg.sgdim = 2
    sg.smdim = 1
    sg.mesh = SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [1.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[
            CellBlock(
                "triangle", np.array([[0, 1, 2], [1, 3, 2]], dtype=int)
            )
        ],
        cell_data={
            "property_id": [np.array([1, 1], dtype=int)],
            "additional_rotation_2": [np.array([30.0, 45.0])],
        },
    )
    sg.materials = {"mat": sgio.CauchyContinuumModel(name="mat")}
    sg.mocombos[1] = ("mat", 0.0)

    with pytest.raises(ValueError, match="multiple additional_rotation_2 values"):
        map_structure_gene_to_write_payload(sg, model_space="xy")
