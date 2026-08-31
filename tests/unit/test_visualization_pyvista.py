"""Unit tests for the optional PyVista scene factory."""

from __future__ import annotations

import sys

import numpy as np
import pytest

from sgio.core.mesh import SGMesh
from sgio.core.property_ref_csys import build_property_ref_axis_cell_data
from sgio.visualization.pyvista import (
    _sample_cell_indices,
    create_pyvista_plotter,
)


def _sample_mesh(*, local_csys: bool = True) -> SGMesh:
    """Build a two-cell mesh with optional canonical local-coordinate data."""
    cell_data = {"property_id": [np.array([1, 2], dtype=int)]}
    if local_csys:
        csys = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        cell_data["element_local_csys"] = [np.array([csys, csys])]
        # This deliberately invalid compatibility field proves that the
        # canonical field remains the scene factory's priority.
        cell_data["property_ref_csys"] = [np.zeros((2, 9))]

    return SGMesh(
        points=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]]
        ),
        cells=[("triangle", np.array([[0, 1, 2], [1, 3, 2]], dtype=int))],
        cell_data=cell_data,
    )


@pytest.mark.unit
@pytest.mark.visualization
def test_create_pyvista_plotter_returns_a_mesh_and_local_axis_scene():
    """The public factory adds one mesh actor and three local-axis glyph actors."""
    pyvista = pytest.importorskip("pyvista")

    plotter = create_pyvista_plotter(
        _sample_mesh(),
        scalars="property_id",
        show_local_axes=True,
        max_local_axes=1,
    )
    try:
        assert isinstance(plotter, pyvista.Plotter)
        assert len(plotter.actors) >= 4
    finally:
        plotter.close()


@pytest.mark.unit
@pytest.mark.visualization
def test_create_pyvista_plotter_rebuilds_axis_compatibility_fields():
    """Axis compatibility fields must be usable when canonical data is absent."""
    pytest.importorskip("pyvista")
    mesh = _sample_mesh(local_csys=False)
    csys = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    mesh.cell_data.update(build_property_ref_axis_cell_data([[csys, csys]]))

    plotter = create_pyvista_plotter(mesh, show_local_axes=True)
    try:
        assert len(plotter.actors) >= 4
    finally:
        plotter.close()


@pytest.mark.unit
def test_create_pyvista_plotter_rejects_unknown_scalar_field():
    """Selected coloring data must exist on the converted mesh."""
    with pytest.raises(ValueError, match="Scalar field 'missing'"):
        create_pyvista_plotter(_sample_mesh(), scalars="missing")


@pytest.mark.unit
def test_create_pyvista_plotter_imports_pyvista_lazily(monkeypatch):
    """Importing visualization stays usable without installing PyVista."""
    monkeypatch.setitem(sys.modules, "pyvista", None)

    with pytest.raises(ImportError, match="uv sync --extra pyvista"):
        create_pyvista_plotter(_sample_mesh())


@pytest.mark.unit
def test_sample_cell_indices_is_deterministic_and_bounded():
    """Glyph sampling must evenly select at most the requested cell count."""
    np.testing.assert_array_equal(_sample_cell_indices(5, 3), np.array([0, 2, 4]))
    np.testing.assert_array_equal(_sample_cell_indices(2, 5), np.array([0, 1]))

    with pytest.raises(ValueError, match="max_local_axes must be positive"):
        _sample_cell_indices(1, 0)


@pytest.mark.unit
@pytest.mark.visualization
def test_pyvista_plotter_exports_html_when_trame_is_installed(tmp_path):
    """HTML export is delegated to PyVista when its optional Trame extra exists."""
    pytest.importorskip("trame")
    output_path = tmp_path / "local_axes.html"
    plotter = create_pyvista_plotter(_sample_mesh(), show_local_axes=True)
    try:
        plotter.export_html(output_path)
    finally:
        plotter.close()

    assert output_path.is_file()
    assert output_path.stat().st_size > 0
