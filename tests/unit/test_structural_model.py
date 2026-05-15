"""Tests for the StructuralModel application-layer container."""

from pathlib import Path

import numpy as np
import pytest

import sgio
from sgio.core import FEModel, Section, StructuralModel
from sgio.iofunc.base import get_format_registry


@pytest.mark.unit
def test_structural_model_is_independently_usable():
    """StructuralModel should work as a standalone structural container."""
    model = StructuralModel(name="frame")
    mesh = sgio.SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        cells=[("line", np.array([[0, 1]]))],
    )

    model.mesh = mesh
    model.materials["steel"] = {"elastic": {"E": 210.0}}
    model.sections["beam"] = Section(
        name="beam",
        material="steel",
        orientation=0.0,
        property_id=1,
    )
    model.boundary_conditions.append({"name": "root_fix"})
    model.loads.append({"name": "tip_force"})
    model.steps.append({"name": "static"})
    model.interactions.append({"name": "contact_a"})
    model.coordinate_systems["global"] = {"origin": [0.0, 0.0, 0.0]}
    model.extras["source"] = "unit-test"

    assert isinstance(model.fe, FEModel)
    assert model.fe_model is model.fe
    assert model.name == "frame"
    assert model.mesh is mesh
    assert model.materials["steel"]["elastic"]["E"] == 210.0
    assert model.sections["beam"].property_id == 1
    assert model.boundary_conditions[0]["name"] == "root_fix"
    assert model.loads[0]["name"] == "tip_force"
    assert model.steps[0]["name"] == "static"
    assert model.interactions[0]["name"] == "contact_a"
    assert model.coordinate_systems["global"]["origin"] == [0.0, 0.0, 0.0]
    assert model.extras["source"] == "unit-test"


@pytest.mark.unit
def test_structural_model_from_fe_deep_copies_backing_data():
    """from_fe should deep-copy FE storage so application layers can diverge."""
    fe = FEModel(name="source-fe")
    fe.mesh = sgio.SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0]]),
        cells=[("line", np.array([[0, 1]]))],
    )
    fe.materials["steel"] = {"elastic": {"E": 210.0}}
    fe.sections["beam"] = Section(
        name="beam",
        material="steel",
        orientation=15.0,
        property_id=7,
    )

    model = StructuralModel.from_fe(fe)

    assert model.fe_model is not fe
    assert model.name == "source-fe"
    assert model.mesh is not fe.mesh
    assert model.mesh is not None
    assert model.mesh.points is not fe.mesh.points
    assert model.materials is not fe.materials
    assert model.sections is not fe.sections
    assert model.sections["beam"] is not fe.sections["beam"]

    model.mesh.points[0, 0] = 99.0
    model.materials["steel"]["elastic"]["E"] = 123.0
    model.sections["beam"].property_id = 9

    assert fe.mesh.points[0, 0] == 0.0
    assert fe.materials["steel"]["elastic"]["E"] == 210.0
    assert fe.sections["beam"].property_id == 7


@pytest.mark.unit
def test_structural_model_can_wrap_mesh_read_from_gmsh_adapter():
    """Gmsh FE data should be wrappable as a second application-layer model."""
    fixture = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "gmsh"
        / "sg21_box_quad4_min_gmsh41.msh"
    )
    registry = get_format_registry()
    reader = registry.get_reader("gmsh")

    mesh = reader.read_input(str(fixture), format_version="4.1")
    model = StructuralModel.from_fe(FEModel(name="gmsh-box", mesh=mesh))

    assert model.name == "gmsh-box"
    assert model.mesh is not None
    assert model.mesh is not mesh
    assert model.mesh.points.shape[0] > 0
    assert len(model.mesh.cells) > 0
