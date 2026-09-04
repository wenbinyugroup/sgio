"""Unit tests for property reference coordinate-system helpers."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
import tempfile

import numpy as np
import pytest

from sgio.core.mesh import CellBlock, SGMesh
from sgio.core.property_ref_csys import (
    build_property_ref_csys_from_axis_cell_data,
    build_property_ref_axis_cell_data,
    project_property_ref_csys,
    property_ref_csys_to_axes,
    property_ref_csys_to_vabs_theta,
    resolve_element_local_csys,
    vabs_theta_to_property_ref_csys,
)
from sgio.iofunc.gmsh import _gmsh
from sgio.iofunc.gmsh._common import _normalize_local_coordinate_fields
from sgio.iofunc.gmsh.writer import write_input_payload
from sgio.iofunc.vabs._mesh import (
    _read_property_id_ref_csys,
    _write_property_id_ref_csys,
)


@pytest.mark.unit
def test_vabs_theta_roundtrip_uses_internal_nine_value_representation():
    """VABS theta values should normalize to the internal 9-value representation."""
    cell_prop_id, cell_csys = _read_property_id_ref_csys(
        StringIO("1 7 90.0\n"),
        nelem=1,
        cells=[("quad", np.array([[0, 1, 2, 3]], dtype=int))],
        elem_id_to_cell_id={1: (0, 0)},
        format_flag=1,
    )

    np.testing.assert_array_equal(cell_prop_id[0], np.array([7]))
    np.testing.assert_allclose(
        cell_csys[0][0],
        np.array([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]),
        atol=1.0e-12,
    )
    assert property_ref_csys_to_vabs_theta(cell_csys[0][0]) == pytest.approx(90.0)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("model_space", "csys_points", "expected_theta"),
    [
        # Gmsh section in xy plane: section normal is +z, local y2 should be
        # measured from gmsh +x (which the writer maps to VABS x2).
        ("xy", [0, 0, 1,  1, 0, 0,  0, 0, 0], 0.0),
        ("xy", [0, 0, 1,  0.7071067811865476, 0.7071067811865476, 0,  0, 0, 0], 45.0),
        # Gmsh section in yz plane: section normal is +x, theta_1 measured from
        # gmsh +y (= VABS x2).
        ("yz", [1, 0, 0,  0, 1, 0,  0, 0, 0], 0.0),
        ("yz", [1, 0, 0,  0, 0.7071067811865476, 0.7071067811865476,  0, 0, 0], 45.0),
        # Gmsh section in zx plane: section normal is +y, theta_1 measured from
        # gmsh +z (= VABS x2).
        ("zx", [0, 1, 0,  0, 0, 1,  0, 0, 0], 0.0),
        ("zx", [0, 1, 0,  0.7071067811865476, 0, 0.7071067811865476,  0, 0, 0], 45.0),
        # VABS-native frame (default): local y1 = VABS x1, theta_1 measured
        # from VABS x2 toward VABS x3.
        ("",   [1, 0, 0,  0, 1, 0,  0, 0, 0], 0.0),
        ("",   [1, 0, 0,  0, 0, 1,  0, 0, 0], 90.0),
    ],
)
def test_property_ref_csys_to_vabs_theta_respects_model_space(
    model_space, csys_points, expected_theta
):
    """theta_1 should be measured in the plane indicated by model_space."""
    theta = property_ref_csys_to_vabs_theta(
        np.asarray(csys_points, dtype=float), model_space=model_space
    )
    assert theta == pytest.approx(expected_theta)


@pytest.mark.unit
def test_property_ref_csys_axes_follow_right_handed_definition():
    """The internal point-based definition should reconstruct local y1/y2/y3 axes."""
    csys = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0])

    axis_y1, axis_y2, axis_y3 = property_ref_csys_to_axes(csys)

    np.testing.assert_allclose(axis_y1, np.array([1.0, 0.0, 0.0]))
    np.testing.assert_allclose(axis_y2, np.array([0.0, 0.0, 1.0]))
    np.testing.assert_allclose(axis_y3, np.array([0.0, -1.0, 0.0]))


@pytest.mark.unit
@pytest.mark.parametrize(
    ("model_space", "expected"),
    [
        ("", [11.0, 20.0, 30.0, 10.0, 22.0, 30.0, 10.0, 20.0, 30.0]),
        ("xy", [30.0, 11.0, 20.0, 30.0, 10.0, 22.0, 30.0, 10.0, 20.0]),
        ("yz", [11.0, 20.0, 30.0, 10.0, 22.0, 30.0, 10.0, 20.0, 30.0]),
        ("zx", [20.0, 30.0, 11.0, 22.0, 30.0, 10.0, 20.0, 30.0, 10.0]),
    ],
)
def test_project_property_ref_csys_reorders_all_points_with_right_handed_axes(
    model_space,
    expected,
):
    """Projection must apply the same even coordinate permutation to ``a``, ``b``, and ``c``."""
    csys = [11.0, 20.0, 30.0, 10.0, 22.0, 30.0, 10.0, 20.0, 30.0]

    projected = project_property_ref_csys(csys, model_space)

    np.testing.assert_allclose(projected, expected)
    axis_y1, axis_y2, axis_y3 = property_ref_csys_to_axes(projected)
    np.testing.assert_allclose(np.cross(axis_y1, axis_y2), axis_y3)


@pytest.mark.unit
def test_project_property_ref_csys_rejects_unknown_model_space():
    """Projection must reject a model-space name that does not define a plane."""
    with pytest.raises(ValueError, match="Unsupported model_space 'bad'"):
        project_property_ref_csys(np.arange(9, dtype=float), "bad")


@pytest.mark.unit
def test_vabs_writer_converts_internal_property_ref_csys_back_to_theta():
    """VABS writing should emit theta_1 from the internal 9-value representation."""
    buffer = StringIO()

    _write_property_id_ref_csys(
        buffer,
        cell_prop_id=[np.array([3, 4], dtype=int)],
        cell_csys=[
            np.array(
                [
                    vabs_theta_to_property_ref_csys(0.0),
                    vabs_theta_to_property_ref_csys(45.0),
                ]
            )
        ],
        elem_ids=[np.array([11, 12], dtype=int)],
    )

    lines = [line.strip() for line in buffer.getvalue().splitlines() if line.strip()]
    assert lines[0].split() == ["11", "3", "0.000000000000e+00"]
    assert lines[1].split() == ["12", "4", "4.500000000000e+01"]


@pytest.mark.unit
def test_gmsh_writer_outputs_local_axis_element_data_blocks():
    """Gmsh writing should emit canonical local-csys and axis ElementData blocks."""
    mesh = SGMesh(
        points=np.array(
            [
                [0.0, -0.5, -0.5],
                [0.0, 0.5, -0.5],
                [0.0, 0.5, 0.5],
                [0.0, -0.5, 0.5],
            ]
        ),
        cells=[("quad", np.array([[0, 1, 2, 3]], dtype=int))],
        cell_data={
            "property_id": [np.array([1], dtype=int)],
            "property_ref_csys": [np.array([vabs_theta_to_property_ref_csys(30.0)])],
        },
    )
    payload = {
        "format_version": "4.1",
        "mesh": mesh,
        "float_fmt": ".6e",
        "mesh_only": True,
        "binary": False,
        "sgdim": 2,
    }
    workspace_dir = Path.cwd()
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".msh",
        dir=workspace_dir,
        delete=False,
    ) as buffer:
        output_file = Path(buffer.name)
        write_input_payload(buffer, payload)

    try:
        text = output_file.read_text(encoding="utf-8")
    finally:
        output_file.unlink(missing_ok=True)
    assert '"element_local_csys"' in text
    assert '"property_ref_axis_y1"' in text
    assert '"property_ref_axis_y2"' in text
    assert '"property_ref_axis_y3"' in text
    assert "1 1.0 0.0 0.0" in text
    assert "1 -0.0 0.8660254037844387 0.49999999999999994" in text


@pytest.mark.unit
def test_gmsh_writer_does_not_emit_legacy_sg_blocks():
    """Gmsh writing should stop emitting legacy SG custom blocks."""
    mesh = SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        ),
        cells=[("quad", np.array([[0, 1, 2, 3]], dtype=int))],
        cell_data={"property_id": [np.array([1], dtype=int)]},
    )
    payload = {
        "format_version": "4.1",
        "mesh": mesh,
        "float_fmt": ".6e",
        "mesh_only": True,
        "binary": False,
        "sgdim": 2,
        "mocombos": {1: ("mat", 15.0)},
        "sg_configs": {"sgdim": 2, "model": 1},
    }
    workspace_dir = Path.cwd()
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".msh",
        dir=workspace_dir,
        delete=False,
    ) as buffer:
        output_file = Path(buffer.name)
        write_input_payload(buffer, payload)

    try:
        text = output_file.read_text(encoding="utf-8")
    finally:
        output_file.unlink(missing_ok=True)

    assert "$SGLayerDef" not in text
    assert "$SGConfig" not in text


@pytest.mark.unit
def test_build_property_ref_axis_cell_data_returns_three_vector_fields():
    """Axis derivation should return three 3-component cell-data blocks."""
    axis_data = build_property_ref_axis_cell_data(
        [[vabs_theta_to_property_ref_csys(0.0), vabs_theta_to_property_ref_csys(90.0)]]
    )

    assert set(axis_data) == {
        "property_ref_axis_y1",
        "property_ref_axis_y2",
        "property_ref_axis_y3",
    }
    assert axis_data["property_ref_axis_y1"][0].shape == (2, 3)
    assert axis_data["property_ref_axis_y2"][0].shape == (2, 3)
    assert axis_data["property_ref_axis_y3"][0].shape == (2, 3)


@pytest.mark.unit
def test_build_property_ref_csys_from_axis_cell_data_roundtrips_axes():
    """Axis-vector compatibility fields should rebuild canonical local csys."""
    original_blocks = [[vabs_theta_to_property_ref_csys(30.0)]]
    axis_data = build_property_ref_axis_cell_data(original_blocks)

    rebuilt = build_property_ref_csys_from_axis_cell_data(
        axis_data["property_ref_axis_y1"],
        axis_data["property_ref_axis_y2"],
        axis_data["property_ref_axis_y3"],
    )

    np.testing.assert_allclose(rebuilt[0][0], original_blocks[0][0])


@pytest.mark.unit
def test_resolve_element_local_csys_prefers_canonical_data_without_mutation():
    """Canonical local-csys data must win without changing the source mapping."""
    canonical = vabs_theta_to_property_ref_csys(30.0)
    legacy = vabs_theta_to_property_ref_csys(75.0)
    cell_data = {
        "element_local_csys": [np.array([canonical])],
        "property_ref_csys": [np.array([legacy])],
    }
    cells = [CellBlock("quad", np.array([[0, 1, 2, 3]], dtype=int))]

    resolved = resolve_element_local_csys(cell_data, cells)

    assert resolved is not None
    np.testing.assert_allclose(resolved[0][0], canonical)
    np.testing.assert_allclose(cell_data["property_ref_csys"][0][0], legacy)


@pytest.mark.unit
def test_resolve_element_local_csys_rebuilds_axis_compatibility_data():
    """Axis compatibility fields must rebuild canonical 9-value cell data."""
    canonical = vabs_theta_to_property_ref_csys(30.0)
    cell_data = build_property_ref_axis_cell_data([[canonical]])
    cells = [CellBlock("quad", np.array([[0, 1, 2, 3]], dtype=int))]

    resolved = resolve_element_local_csys(cell_data, cells)

    assert resolved is not None
    np.testing.assert_allclose(resolved[0][0], canonical)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("cell_csys", "match"),
    [
        (np.array([[1.0, 2.0]]), "exactly 9 values"),
        (np.zeros((1, 9)), "points a and c must be distinct"),
    ],
)
def test_resolve_element_local_csys_rejects_invalid_canonical_values(cell_csys, match):
    """Resolved local coordinate systems must have valid 9-value geometry."""
    cells = [CellBlock("quad", np.array([[0, 1, 2, 3]], dtype=int))]

    with pytest.raises(ValueError, match=match):
        resolve_element_local_csys({"element_local_csys": [cell_csys]}, cells)


@pytest.mark.unit
def test_gmsh_reader_rebuilds_element_local_csys_from_axis_fields():
    """Reader should rebuild canonical local csys from compatibility axis fields."""
    mesh = SGMesh(
        points=np.array(
            [
                [0.0, -0.5, -0.5],
                [0.0, 0.5, -0.5],
                [0.0, 0.5, 0.5],
                [0.0, -0.5, 0.5],
            ]
        ),
        cells=[("quad", np.array([[0, 1, 2, 3]], dtype=int))],
        cell_data={
            "property_id": [np.array([1], dtype=int)],
            "property_ref_csys": [np.array([vabs_theta_to_property_ref_csys(30.0)])],
        },
    )
    payload = {
        "format_version": "4.1",
        "mesh": mesh,
        "float_fmt": ".6e",
        "mesh_only": True,
        "binary": False,
        "sgdim": 2,
    }
    workspace_dir = Path.cwd()
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".msh",
        dir=workspace_dir,
        delete=False,
    ) as buffer:
        output_file = Path(buffer.name)
        write_input_payload(buffer, payload)

    try:
        text = output_file.read_text(encoding="utf-8")
        text = text.replace('"element_local_csys"', '"legacy_removed_element_local_csys"')
        output_file.write_text(text, encoding="utf-8")
        with output_file.open("rb") as handle:
            parsed_mesh = _gmsh.read_buffer(handle, format_version="4.1")
    finally:
        output_file.unlink(missing_ok=True)

    assert "element_local_csys" in parsed_mesh.cell_data
    assert "property_ref_csys" in parsed_mesh.cell_data
    np.testing.assert_allclose(
        parsed_mesh.cell_data["element_local_csys"][0][0],
        vabs_theta_to_property_ref_csys(30.0),
        atol=1.0e-12,
    )


@pytest.mark.unit
def test_normalize_local_csys_prefers_element_local_csys_over_property_ref_csys():
    """When both fields are present with different values, the canonical one wins.

    Locks reader priority step 1 (element_local_csys) over step 2
    (property_ref_csys) from the SG-on-Gmsh spec.
    """
    canonical = vabs_theta_to_property_ref_csys(30.0)
    legacy = vabs_theta_to_property_ref_csys(75.0)
    cell_data = {
        "element_local_csys": [np.array([canonical])],
        "property_ref_csys": [np.array([legacy])],
    }
    cells = [CellBlock("quad", np.array([[0, 1, 2, 3]], dtype=int))]

    _normalize_local_coordinate_fields(cell_data, cells)

    # Canonical field is preserved.
    np.testing.assert_allclose(
        cell_data["element_local_csys"][0][0], canonical, atol=1.0e-12
    )
    # Compatibility field is overwritten to match the canonical field, not the
    # differing legacy value it originally held.
    np.testing.assert_allclose(
        cell_data["property_ref_csys"][0][0], canonical, atol=1.0e-12
    )
    assert not np.allclose(cell_data["property_ref_csys"][0][0], legacy)


@pytest.mark.unit
def test_gmsh_reader_expands_legacy_additional_rotation_field():
    """Reader should expand legacy single-field additional rotation into 1/2/3."""
    msh_text = """$MeshFormat
4.1 0 8
$EndMeshFormat
$Nodes
1 4 1 4
2 1 0 4
1
2
3
4
0 0 0
1 0 0
1 1 0
0 1 0
$EndNodes
$Elements
1 1 1 1
2 1 3 1
1 1 2 3 4
$EndElements
$ElementData
1
"additional_rotation"
1
0.0
3
0
1
1
1 45.0
$EndElementData
"""
    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".msh",
        dir=Path.cwd(),
        delete=False,
    ) as buffer:
        output_file = Path(buffer.name)
        buffer.write(msh_text.encode("utf-8"))

    try:
        with output_file.open("rb") as handle:
            parsed_mesh = _gmsh.read_buffer(handle, format_version="4.1")
    finally:
        output_file.unlink(missing_ok=True)

    np.testing.assert_allclose(parsed_mesh.cell_data["additional_rotation_1"][0], np.array([45.0]))
    np.testing.assert_allclose(parsed_mesh.cell_data["additional_rotation_2"][0], np.array([0.0]))
    np.testing.assert_allclose(parsed_mesh.cell_data["additional_rotation_3"][0], np.array([0.0]))
