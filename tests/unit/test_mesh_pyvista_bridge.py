"""Tests for the SGMesh <-> pyvista bridge (roadmap Phase 9).

Covers:

* ``to_pyvista`` / ``from_pyvista`` round-trip geometry and data (skipped when
  pyvista is not installed).
* pyvista is an optional dependency: importing / using the core mesh does not
  require it, and ``to_pyvista`` fails lazily (only when called) if absent.
"""
import subprocess
import sys
import textwrap

import numpy as np
import pytest

import sgio.core.mesh as core_mesh
from sgio.core.mesh import SGMesh


def _sample_mesh() -> SGMesh:
    """Two-block mesh (triangles + a line) with point/cell data."""
    points = np.array(
        [[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 0, 0]], dtype=float
    )
    return SGMesh(
        points,
        [
            ("triangle", np.array([[0, 1, 2], [1, 3, 2]])),
            ("line", np.array([[3, 4]])),
        ],
        point_data={"node_id": np.array([1, 2, 3, 4, 5])},
        cell_data={"property_id": [np.array([5, 6]), np.array([9])]},
    )


@pytest.mark.unit
def test_to_pyvista_produces_unstructured_grid():
    """to_pyvista yields a pyvista.UnstructuredGrid with matching size."""
    pyvista = pytest.importorskip("pyvista")

    mesh = _sample_mesh()
    grid = mesh.to_pyvista()

    assert isinstance(grid, pyvista.UnstructuredGrid)
    assert grid.n_points == 5
    assert grid.n_cells == 3
    assert "node_id" in grid.point_data
    assert "property_id" in grid.cell_data


@pytest.mark.unit
def test_from_pyvista_roundtrips_geometry_and_data():
    """from_pyvista(to_pyvista(mesh)) preserves geometry and per-block data."""
    pytest.importorskip("pyvista")

    mesh = _sample_mesh()
    back = SGMesh.from_pyvista(mesh.to_pyvista())

    assert isinstance(back, SGMesh)
    # Same points (block order may differ: pyvista groups by VTK cell type).
    assert np.allclose(np.sort(back.points, axis=0), np.sort(mesh.points, axis=0))

    block_by_type = {cb.type: cb for cb in back.cells}
    assert set(block_by_type) == {"triangle", "line"}
    assert len(block_by_type["triangle"]) == 2
    assert len(block_by_type["line"]) == 1

    # cell_data is split per block, aligned with each type.
    pid = {cb.type: arr for cb, arr in zip(back.cells, back.cell_data["property_id"])}
    assert sorted(pid["triangle"].tolist()) == [5, 6]
    assert pid["line"].tolist() == [9]
    assert "node_id" in back.point_data


@pytest.mark.unit
def test_core_mesh_usable_without_pyvista_and_to_pyvista_fails_lazily():
    """The core mesh imports and operates with pyvista absent.

    Runs in a subprocess where ``import pyvista`` is forced to fail. The core
    mesh module is loaded directly by file path (bypassing the sgio package
    init) and exercised. ``to_pyvista`` must raise only when called.
    """
    module_path = core_mesh.__file__
    script = textwrap.dedent(
        f"""
        import sys, importlib.util
        sys.modules["pyvista"] = None  # force `import pyvista` to fail

        spec = importlib.util.spec_from_file_location("_sgmesh_isolated", r"{module_path}")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # must not need pyvista

        import numpy as np
        mesh = m.SGMesh(
            np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            [("triangle", np.array([[0, 1, 2]]))],
        )
        assert mesh.cells[0].dim == 2  # core ops work without pyvista

        try:
            mesh.to_pyvista()
        except ImportError:
            print("OK")
        else:
            raise AssertionError("to_pyvista should raise ImportError when pyvista absent")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout
