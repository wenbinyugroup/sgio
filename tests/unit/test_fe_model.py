"""Tests for the FEModel core container and StructureGene FE proxies."""

import numpy as np
import pytest

import sgio
from sgio.core import FEModel, Section


@pytest.mark.unit
def test_fe_model_is_independently_usable():
    """FEModel should work as a standalone finite element container."""
    fe = FEModel(name="demo")
    mesh = sgio.SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        cells=[("line", np.array([[0, 1]]))],
    )

    fe.mesh = mesh
    fe.extras["source"] = "unit-test"

    assert fe.name == "demo"
    assert fe.mesh is mesh
    assert fe.materials == {}
    assert fe.sections == {}
    assert fe.orientations == {}
    assert fe.material_source_ids == {}
    assert fe.extras["source"] == "unit-test"


@pytest.mark.unit
def test_fe_model_material_source_ids_carry_per_format_provenance():
    """FEModel should hold a per-material, per-format solver-id side map."""
    fe = FEModel(name="prov")

    assert fe.material_source_ids == {}

    fe.material_source_ids["steel"] = {"vabs": 3}
    fe.material_source_ids.setdefault("foam", {})["swiftcomp"] = 5

    assert fe.material_source_ids["steel"]["vabs"] == 3
    assert fe.material_source_ids["foam"]["swiftcomp"] == 5

    # Distinct FEModel instances must not share the default side map.
    assert FEModel().material_source_ids == {}


@pytest.mark.unit
def test_structure_gene_proxies_fe_model_storage():
    """StructureGene legacy accessors should forward to FEModel storage."""
    sg = sgio.StructureGene(name="proxy-sg", sgdim=1)
    mesh = sgio.SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        cells=[("line", np.array([[0, 1]]))],
    )
    material = sgio.CauchyContinuumModel(name="mat1")

    sg.mesh = mesh
    sg.materials["mat1"] = material
    sg.sections["sec1"] = Section(
        name="sec1",
        material="mat1",
        orientation=45.0,
        property_id=1,
    )

    assert isinstance(sg.fe_model, FEModel)
    assert sgio.FEModel is FEModel
    assert sg.name == "proxy-sg"
    assert sg.fe_model.name == "proxy-sg"
    assert sg.fe_model.mesh is mesh
    assert sg.fe_model.materials["mat1"] is material
    assert sg.mocombos[1] == ("mat1", 45.0)
    assert sg.fe_model.sections["sec1"].material == "mat1"
    assert sg.fe_model.sections["sec1"].orientation == 45.0
    assert sg.fe_model.sections["sec1"].property_id == 1

    replacement_mesh = sgio.SGMesh(
        points=np.array([[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]),
        cells=[("line", np.array([[0, 1]]))],
    )
    sg.fe_model.mesh = replacement_mesh

    assert sg.mesh is replacement_mesh
