"""Tests for phase 3 material ID handling cleanup."""

from __future__ import annotations

from io import StringIO

import numpy as np
import pytest
from meshio import Mesh

import sgio
from sgio.iofunc._mesh_convert import mesh_to_sg, restore_sg_from_mesh_extras
from sgio.iofunc.common import build_material_id_map, write_material_combos


@pytest.mark.unit
def test_structure_gene_removes_legacy_material_id_api():
    """StructureGene should no longer expose material ID bookkeeping state."""
    sg = sgio.StructureGene()

    assert not hasattr(sg, "material_name_id_pairs")
    assert not hasattr(sg, "add_material_name_id_pair")
    assert not hasattr(sg, "sync_material_name_id_pairs")
    assert not hasattr(sg, "get_export_material_ids")
    assert not hasattr(sg, "get_material_name_by_id")
    assert not hasattr(sg, "get_material_id_by_name")
    assert not hasattr(sg, "findMaterialByName")
    assert not hasattr(sg, "findComboByMaterialOrientation")


@pytest.mark.unit
def test_material_combo_writer_uses_adapter_local_material_ids():
    """Material combo export should use sequential IDs built from materials."""
    sg = sgio.StructureGene()
    sg.materials["fiber"] = sgio.CauchyContinuumModel(name="fiber")
    sg.materials["matrix"] = sgio.CauchyContinuumModel(name="matrix")
    sg.mocombos[7] = ("matrix", 15.0)

    buffer = StringIO()
    mat_id_map = build_material_id_map(sg.materials)
    write_material_combos(sg, buffer, mat_id_map=mat_id_map)

    line = buffer.getvalue().splitlines()[0]
    tokens = line.split("!")[0].split()

    assert mat_id_map == {"fiber": 1, "matrix": 2}
    assert tokens[:3] == ["7", "2", "1.500000000000e+01"]


@pytest.mark.unit
def test_restore_sg_from_mesh_extras_uses_mesh_field_names():
    """Gmsh layer definitions should resolve names from mesh field data."""
    mesh = Mesh(
        points=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            dtype=float,
        ),
        cells=[("triangle", np.array([[0, 1, 2]], dtype=int))],
        cell_data={"property_id": [np.array([5], dtype=int)]},
        field_data={"matrix": np.array([5, 2], dtype=int)},
    )
    mesh.sg_layer_defs = {1: (5, 30.0)}
    mesh.sg_configs = {"sgdim": 2, "model": 1, "do_damping": 1, "thermal": 1}

    sg = mesh_to_sg(mesh, sgdim=2, model_type="PL1")
    restore_sg_from_mesh_extras(sg, mesh)

    assert sg.mocombos[1] == ("matrix", 30.0)
    assert "matrix" in sg.materials
    assert sg.analysis_config.model == 1
    assert sg.analysis_config.do_damping == 1
    assert sg.analysis_config.physics == 1


@pytest.mark.unit
def test_restore_sg_from_mesh_extras_falls_back_to_generated_material_name():
    """Gmsh layer definitions without field names should get generated names."""
    mesh = Mesh(
        points=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            dtype=float,
        ),
        cells=[("triangle", np.array([[0, 1, 2]], dtype=int))],
        cell_data={"property_id": [np.array([7], dtype=int)]},
        field_data={},
    )
    mesh.sg_layer_defs = {2: (7, 0.0)}
    mesh.sg_configs = {}

    sg = mesh_to_sg(mesh, sgdim=2, model_type="PL1")
    restore_sg_from_mesh_extras(sg, mesh)

    assert sg.mocombos[2] == ("Material_7", 0.0)
    assert "Material_7" in sg.materials
