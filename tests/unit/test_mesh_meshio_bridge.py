"""Tests for the SGMesh <-> meshio composition boundary (roadmap Phase 6).

Covers:

* ``SGMesh`` is a composition container, not a ``meshio.Mesh`` subclass.
* ``to_meshio`` / ``from_meshio`` bridge round-trips geometry and data.
* the core mesh module is importable and usable with ``meshio`` absent, and
  ``to_meshio`` fails lazily (only when actually called) in that case.
"""
import subprocess
import sys
import textwrap

import numpy as np
import pytest

import sgio.core.mesh as core_mesh
from sgio.core.mesh import CellBlock, SGMesh


def _sample_mesh() -> SGMesh:
    """Build a small two-block mesh with mixed data containers."""
    points = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]]
    )
    cells = [
        ("triangle", np.array([[0, 1, 2]])),
        ("triangle", np.array([[1, 3, 2]])),
    ]
    return SGMesh(
        points,
        cells,
        point_data={"node_id": np.array([1, 2, 3, 4])},
        cell_data={"property_id": [np.array([1]), np.array([2])]},
        field_data={"steel": np.array([1, 2])},
    )


@pytest.mark.unit
def test_sgmesh_is_composition_not_meshio_subclass():
    """SGMesh must not inherit from meshio.Mesh."""
    import meshio

    mesh = _sample_mesh()
    assert not isinstance(mesh, meshio.Mesh)
    # Attribute surface still mirrors meshio.Mesh so adapters keep working.
    for attr in (
        "points", "cells", "point_data", "cell_data", "field_data",
        "point_sets", "cell_sets", "gmsh_periodic", "info", "cell_point_data",
    ):
        assert hasattr(mesh, attr)


@pytest.mark.unit
def test_to_meshio_produces_equivalent_meshio_mesh():
    """to_meshio yields a real meshio.Mesh with equal geometry and data."""
    import meshio

    mesh = _sample_mesh()
    mm = mesh.to_meshio()

    assert isinstance(mm, meshio.Mesh)
    assert np.array_equal(mm.points, mesh.points)
    assert [cb.type for cb in mm.cells] == ["triangle", "triangle"]
    assert np.array_equal(mm.cells[1].data, mesh.cells[1].data)
    assert np.array_equal(mm.cell_data["property_id"][0], np.array([1]))
    assert np.array_equal(mm.point_data["node_id"], np.array([1, 2, 3, 4]))
    assert np.array_equal(mm.field_data["steel"], np.array([1, 2]))


@pytest.mark.unit
def test_from_meshio_roundtrips_through_bridge():
    """from_meshio(to_meshio(mesh)) preserves geometry and standard data."""
    mesh = _sample_mesh()
    back = SGMesh.from_meshio(mesh.to_meshio())

    assert isinstance(back, SGMesh)
    assert np.array_equal(back.points, mesh.points)
    assert [cb.type for cb in back.cells] == [cb.type for cb in mesh.cells]
    for a, b in zip(back.cells, mesh.cells):
        assert np.array_equal(a.data, b.data)
    assert isinstance(back.cells[0], CellBlock)
    assert np.array_equal(back.cell_data["property_id"][1], np.array([2]))
    assert np.array_equal(back.point_data["node_id"], np.array([1, 2, 3, 4]))


@pytest.mark.unit
def test_to_meshio_drops_cell_point_data():
    """Element-nodal cell_point_data has no meshio counterpart and is dropped."""
    mesh = _sample_mesh()
    mesh.cell_point_data = {
        "stress": [np.zeros((1, 3, 1)), np.zeros((1, 3, 1))]
    }
    mm = mesh.to_meshio()
    assert not hasattr(mm, "cell_point_data") or not getattr(mm, "cell_point_data", None)
    # Standard cell_data still crosses the bridge.
    assert "property_id" in mm.cell_data


@pytest.mark.unit
def test_core_mesh_usable_without_meshio_and_to_meshio_fails_lazily():
    """The core mesh module imports and operates with meshio absent.

    Runs in a subprocess where ``import meshio`` is forced to fail. The core
    mesh module (self-contained, no meshio import) is loaded directly by file
    path — bypassing the sgio package init, whose I/O layer needs meshio — and
    exercised. ``to_meshio`` must fail only when called (lazy import).
    """
    module_path = core_mesh.__file__
    script = textwrap.dedent(
        f"""
        import sys, importlib.util
        # Force any `import meshio` to raise ImportError.
        sys.modules["meshio"] = None

        spec = importlib.util.spec_from_file_location("_sgmesh_isolated", r"{module_path}")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # must not need meshio

        import numpy as np
        mesh = m.SGMesh(
            np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            [("triangle", np.array([[0, 1, 2]]))],
            cell_data={{"property_id": [np.array([1])]}},
        )
        # Core cell operations work without meshio.
        assert mesh.cells[0].dim == 2
        assert m.check_isolated_nodes(mesh) is not None

        # The bridge imports meshio lazily -> only now does it fail.
        try:
            mesh.to_meshio()
        except ImportError:
            print("OK")
        else:
            raise AssertionError("to_meshio should raise ImportError when meshio absent")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout
