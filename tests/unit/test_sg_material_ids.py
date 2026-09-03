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
def test_build_material_id_map_prefers_source_ids():
    """Remembered per-format ids should be honored regardless of dict order."""
    materials = {"a": None, "b": None, "c": None}
    source_ids = {
        "a": {"vabs": 2},
        "b": {"vabs": 3},
        "c": {"vabs": 1},
    }

    result = build_material_id_map(materials, source_ids, "vabs")

    assert result == {"a": 2, "b": 3, "c": 1}


@pytest.mark.unit
def test_build_material_id_map_fills_gaps_for_materials_without_provenance():
    """Materials lacking provenance should fill the smallest free ids in order."""
    materials = {"a": None, "b": None, "c": None}
    # Only "b" has a remembered id; "a"/"c" must fill the remaining 1..n gaps.
    source_ids = {"b": {"vabs": 2}}

    result = build_material_id_map(materials, source_ids, "vabs")

    assert result == {"a": 1, "b": 2, "c": 3}


@pytest.mark.unit
def test_build_material_id_map_ignores_other_format_provenance():
    """Provenance for a different format must not affect this format's map."""
    materials = {"a": None, "b": None}
    source_ids = {"a": {"swiftcomp": 2}, "b": {"swiftcomp": 1}}

    result = build_material_id_map(materials, source_ids, "vabs")

    assert result == {"a": 1, "b": 2}


@pytest.mark.unit
def test_build_material_id_map_falls_back_when_provenance_invalid():
    """Duplicate or out-of-range remembered ids should force positional numbering."""
    materials = {"a": None, "b": None}

    # Duplicate remembered id cannot form a valid 1..n assignment.
    duplicate = {"a": {"vabs": 1}, "b": {"vabs": 1}}
    assert build_material_id_map(materials, duplicate, "vabs") == {"a": 1, "b": 2}

    # Out-of-range remembered id (> n) is invalid for a 2-material file.
    out_of_range = {"a": {"vabs": 5}}
    assert build_material_id_map(materials, out_of_range, "vabs") == {"a": 1, "b": 2}


@pytest.mark.unit
def test_build_material_id_map_without_provenance_is_positional():
    """Absent provenance keeps the legacy positional numbering (no regression)."""
    materials = {"a": None, "b": None, "c": None}

    assert build_material_id_map(materials) == {"a": 1, "b": 2, "c": 3}
    assert build_material_id_map(materials, {}, "vabs") == {"a": 1, "b": 2, "c": 3}


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

    sg = mesh_to_sg(mesh, sgdim=2, model_type="PL1", section_names={"matrix"})
    restore_sg_from_mesh_extras(sg, mesh)

    assert sg.mocombos[1] == ("matrix", 30.0)
    # The layer definition binds a name; the material payload itself comes from
    # the section data, so nothing is fabricated here.
    assert sg.materials == {}
    assert sg.analysis_config.model == 1
    assert sg.analysis_config.do_damping == 1
    assert sg.analysis_config.physics == 1


@pytest.mark.unit
def test_restore_sg_from_mesh_extras_ignores_unresolvable_layer_defs():
    """A layer definition naming no known physical group must not invent one."""
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

    assert dict(sg.mocombos) == {}
    assert sg.materials == {}
