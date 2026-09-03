"""Unit tests for the optional PyVista scene factory."""

from __future__ import annotations

import sys

import numpy as np
import pytest

from sgio.core.mesh import SGMesh
from sgio.core.property_ref_csys import build_property_ref_axis_cell_data
from sgio.core.sg import StructureGene
from sgio.visualization.pyvista import (
    _sample_cell_indices,
    create_pyvista_local_axis_multiblock,
    create_pyvista_plotter,
    plot_sg_pyvista,
    plot_pyvista_local_axes,
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
def test_plot_sg_pyvista_returns_a_scene_for_a_structure_gene():
    """The PyVista entry point uses a discrete property-ID mesh legend."""
    pyvista = pytest.importorskip("pyvista")
    sg = StructureGene(name="sample", sgdim=2)
    sg.mesh = _sample_mesh()

    plotter = plot_sg_pyvista(sg, show_local_axes=True, max_local_axes=1)
    try:
        assert isinstance(plotter, pyvista.Plotter)
        assert len(plotter.actors) >= 4
        assert any(
            type(actor).__name__ == "vtkLegendBoxActor"
            for actor in plotter.actors.values()
        )
        assert all(
            type(actor).__name__ != "vtkScalarBarActor"
            for actor in plotter.actors.values()
        )
    finally:
        plotter.close()


@pytest.mark.unit
@pytest.mark.visualization
def test_plot_sg_pyvista_adds_desktop_visibility_widgets():
    """High-level desktop controls must manage faces, edges, nodes, and axes."""
    pytest.importorskip("pyvista")
    sg = StructureGene(name="sample", sgdim=2)
    sg.mesh = _sample_mesh()

    plotter = plot_sg_pyvista(
        sg,
        show_local_axes=True,
        max_local_axes=1,
        widgets=True,
    )
    try:
        assert len(plotter.widgets.button_widgets) == 4
        assert plotter.actors["_sgio_edges"].GetVisibility() == 1
        assert plotter.actors["_sgio_nodes"].GetVisibility() == 0
    finally:
        plotter.close()


@pytest.mark.unit
def test_plot_sg_pyvista_rejects_widgets_for_offline_html(tmp_path):
    """Python callback widgets cannot be serialized into offline HTML."""
    sg = StructureGene(name="sample", sgdim=2)
    sg.mesh = _sample_mesh()

    with pytest.raises(ValueError, match="cannot be exported to offline HTML"):
        plot_sg_pyvista(sg, widgets=True, output_html=tmp_path / "scene.html")


@pytest.mark.unit
@pytest.mark.visualization
def test_plot_sg_pyvista_writes_local_axis_html_when_trame_is_installed(tmp_path):
    """The high-level PyVista entry point must preserve HTML plot guidance."""
    pytest.importorskip("trame")
    sg = StructureGene(name="sample", sgdim=2)
    sg.mesh = _sample_mesh()
    output_html = tmp_path / "section.html"

    plotter = plot_sg_pyvista(
        sg,
        show_local_axes=True,
        max_local_axes=1,
        output_html=output_html,
    )
    try:
        assert output_html.is_file()
        html = output_html.read_text(encoding="utf-8")
        assert "Properties" in html
        assert "Property 1" in html
        assert "Local coordinate axes" in html
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
@pytest.mark.visualization
def test_create_pyvista_local_axis_multiblock_contains_mesh_and_axis_geometry():
    """The VTM scene must carry the mesh plus three explicit glyph blocks."""
    pyvista = pytest.importorskip("pyvista")

    blocks = create_pyvista_local_axis_multiblock(_sample_mesh())

    assert isinstance(blocks, pyvista.MultiBlock)
    assert blocks.keys() == ["mesh", "local_y1", "local_y2", "local_y3"]
    assert blocks["mesh"].n_cells == 2
    for axis_name in ("local_y1", "local_y2", "local_y3"):
        assert blocks[axis_name].n_cells > 0
        np.testing.assert_array_equal(
            np.unique(blocks[axis_name].point_data["source_cell_index"]),
            np.array([0, 1]),
        )


@pytest.mark.unit
@pytest.mark.visualization
def test_pyvista_local_axis_multiblock_roundtrips_through_vtm(tmp_path):
    """VTM output must retain named mesh and local-axis glyph blocks."""
    pyvista = pytest.importorskip("pyvista")
    output_path = tmp_path / "local_axes.vtm"

    create_pyvista_local_axis_multiblock(_sample_mesh(), max_local_axes=1).save(output_path)
    restored = pyvista.read(output_path)

    assert isinstance(restored, pyvista.MultiBlock)
    assert restored.keys() == ["mesh", "local_y1", "local_y2", "local_y3"]
    assert restored["mesh"].n_cells == 2
    assert restored["local_y1"].n_cells > 0


@pytest.mark.unit
@pytest.mark.visualization
def test_plot_pyvista_local_axes_renders_named_vtm_blocks_and_html(tmp_path):
    """The high-level interface must render a VTM scene and its HTML overlay."""
    pytest.importorskip("pyvista")
    output_path = tmp_path / "local_axes.vtm"
    blocks = create_pyvista_local_axis_multiblock(_sample_mesh())
    blocks.save(output_path)
    html_path = tmp_path / "local_axes.html"

    plotter = plot_pyvista_local_axes(
        output_path,
        max_local_axes=1,
        output_html=html_path,
    )
    try:
        assert len(plotter.actors) >= 5
        assert "View controls" in plotter.text.GetText(2)
        assert all(
            type(actor).__name__ != "vtkScalarBarActor"
            for actor in plotter.actors.values()
        )
    finally:
        plotter.close()

    html = html_path.read_text(encoding="utf-8")
    assert "Local coordinate axes" in html
    assert "View controls" in html
    assert "Shift + left drag: pan" in html
    assert "Right drag: pan" not in html
    assert "#sgio-scene-legend { top: 16px; right: 16px; }" in html
    assert "#sgio-view-help { top: 16px; left: 16px;" in html


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
def test_sample_cell_indices_uses_all_cells_when_no_limit_is_requested():
    """A VTM export must be able to request glyphs for every source cell."""
    np.testing.assert_array_equal(_sample_cell_indices(501, None), np.arange(501))


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
