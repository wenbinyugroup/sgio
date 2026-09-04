"""Optional PyVista scenes for three-dimensional mesh inspection."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from sgio.core.mesh import SGMesh
from sgio.core.property_ref_csys import property_ref_csys_to_axes, resolve_element_local_csys
from sgio.core.sg import StructureGene

if TYPE_CHECKING:
    import pyvista


_AXIS_COLORS = {"y1": "red", "y2": "green", "y3": "blue"}
_PROPERTY_COLORS = (
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
)
_PROPERTY_CATEGORY_NAME = "_sgio_property_category"
_VTM_AXIS_COLORS = {"local_y1": "red", "local_y2": "green", "local_y3": "blue"}
_VTM_AXIS_LABELS = {
    "local_y1": "local y1 (red)",
    "local_y2": "local y2 (green)",
    "local_y3": "local y3 (blue)",
}
_DEFAULT_LOCAL_AXIS_SCALE = 0.025
_VIEW_HELP = "\n".join(
    [
        "View controls",
        "Left drag: rotate",
        "Shift + left drag: pan",
        "Mouse wheel: zoom",
    ]
)
_HTML_OVERLAY_STYLE = """
<style id="sgio-view-overlay-style">
#sgio-view-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  pointer-events: none;
  color: #1f2937;
  font: 14px/1.4 Arial, sans-serif;
}
#sgio-view-overlay .panel {
  position: absolute;
  max-width: 235px;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.2);
}
#sgio-scene-legend { top: 16px; right: 16px; }
#sgio-view-help { top: 16px; left: 16px; white-space: pre-line; }
#sgio-view-overlay .title { font-weight: 700; margin-bottom: 4px; }
#sgio-view-overlay .section { margin-top: 8px; }
#sgio-view-overlay .section:first-child { margin-top: 0; }
#sgio-view-overlay .swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 5px;
  border: 1px solid rgba(15, 23, 42, 0.35);
  border-radius: 2px;
}
</style>
""".strip()
_HTML_VIEW_HELP = """
<div id="sgio-view-help" class="panel"><div class="title">View controls</div>
Left drag: rotate
Shift + left drag: pan
Mouse wheel: zoom</div>
""".strip()


def create_pyvista_plotter(
    mesh: SGMesh,
    *,
    scalars: str | None = None,
    show_edges: bool = True,
    show_local_axes: bool = False,
    max_local_axes: int = 500,
    local_axis_scale: float | None = None,
) -> pyvista.Plotter:
    """Create an interactive PyVista scene for an ``SGMesh``.

    Parameters
    ----------
    mesh : SGMesh
        Mesh to render.
    scalars : str, optional
        Point- or cell-data array used to color the mesh.
    show_edges : bool, optional
        Show mesh edges. Default is ``True``.
    show_local_axes : bool, optional
        Overlay red ``y1``, green ``y2``, and blue ``y3`` element axes.
    max_local_axes : int, optional
        Maximum number of cells receiving local-axis glyphs. Sampling is
        deterministic and evenly distributed. Default is 500.
    local_axis_scale : float, optional
        Glyph length in mesh coordinate units. If omitted, the length is 2.5%
        of the mesh bounding-box diagonal.

    Returns
    -------
    pyvista.Plotter
        Scene ready for caller-controlled ``show()``, screenshots, or HTML
        export.

    Raises
    ------
    ImportError
        If the optional ``pyvista`` dependency is not installed.
    TypeError
        If ``mesh`` is not an ``SGMesh``.
    ValueError
        If ``scalars`` does not name a renderable array, or local-axis options
        are invalid.
    """
    if not isinstance(mesh, SGMesh):
        raise TypeError(f"mesh must be an SGMesh; got {type(mesh).__name__}.")

    plotter, _ = _create_pyvista_scene(
        mesh,
        scalars=scalars,
        show_edges=show_edges,
        show_local_axes=show_local_axes,
        max_local_axes=max_local_axes,
        local_axis_scale=local_axis_scale,
        categorical_property_ids=False,
        widgets=False,
    )
    return plotter


def plot_sg_pyvista(
    sg: StructureGene,
    *,
    scalars: str | None = "property_id",
    show_edges: bool = True,
    show_local_axes: bool = False,
    max_local_axes: int = 500,
    local_axis_scale: float | None = None,
    output_html: str | Path | None = None,
    show: bool = False,
    widgets: bool = False,
) -> pyvista.Plotter:
    """Plot one structure gene with PyVista.

    This is the single-SG PyVista entry point. It hides the mesh extraction and
    returns the native plotter for further PyVista customization. If local axes
    are shown, its HTML output also includes the browser-native axis legend and
    view-control help.

    Parameters
    ----------
    sg : StructureGene
        Structure gene containing the mesh to render.
    scalars : str, optional
        Array used to color the mesh. ``"property_id"`` (the default) uses a
        discrete property color map and legend without a scalar bar. Other
        arrays use PyVista's regular scalar rendering. Pass ``None`` to leave
        the mesh uncolored.
    show_edges : bool, optional
        Show mesh edges. Default is ``True``.
    show_local_axes : bool, optional
        Draw sampled element-local y1/y2/y3 arrows. Default is ``False``.
    max_local_axes : int, optional
        Maximum number of cells receiving local-axis glyphs. Default is 500.
    local_axis_scale : float, optional
        Glyph length in mesh coordinate units.
    output_html : str or pathlib.Path, optional
        Optional self-contained interactive HTML output.
    show : bool, optional
        Open PyVista's desktop window before returning. Default is ``False``.
    widgets : bool, optional
        Add desktop checkbox widgets for local axes, faces, edges, and nodes.
        Widgets require a live PyVista window and cannot be exported to an
        offline HTML file. Default is ``False``.

    Returns
    -------
    pyvista.Plotter
        Plotter containing the SG mesh and optional local-axis glyphs.

    Raises
    ------
    TypeError
        If ``sg`` is not a :class:`~sgio.StructureGene`.
    ValueError
        If ``sg`` has no mesh or plotting options are invalid.
    ImportError
        If the optional ``pyvista`` dependency is not installed.
    """
    if not isinstance(sg, StructureGene):
        raise TypeError(f"sg must be a StructureGene; got {type(sg).__name__}.")
    if sg.mesh is None:
        raise ValueError("sg must contain a mesh.")
    if widgets and output_html is not None:
        raise ValueError("widgets cannot be exported to offline HTML; use show=True instead.")

    plotter, property_legend = _create_pyvista_scene(
        sg.mesh,
        scalars=scalars,
        show_edges=show_edges,
        show_local_axes=show_local_axes,
        max_local_axes=max_local_axes,
        local_axis_scale=local_axis_scale,
        categorical_property_ids=scalars == "property_id",
        widgets=widgets,
    )
    if output_html is not None:
        html_path = Path(output_html)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        plotter.export_html(str(html_path))
        _add_html_overlay(
            html_path,
            property_legend=property_legend,
            include_local_axes=show_local_axes,
        )
    if show:
        plotter.show()
    return plotter


def _create_pyvista_scene(
    mesh: SGMesh,
    *,
    scalars: str | None,
    show_edges: bool,
    show_local_axes: bool,
    max_local_axes: int,
    local_axis_scale: float | None,
    categorical_property_ids: bool,
    widgets: bool,
) -> tuple[pyvista.Plotter, list[tuple[str, str]]]:
    """Create one scene and return property-legend entries for HTML export."""
    if not isinstance(mesh, SGMesh):
        raise TypeError(f"mesh must be an SGMesh; got {type(mesh).__name__}.")

    pyvista = _import_pyvista()
    grid = mesh.to_pyvista()
    _validate_scalars(grid, scalars)

    plotter = pyvista.Plotter()
    property_legend: list[tuple[str, str]] = []
    if categorical_property_ids:
        mesh_actor, property_legend = _add_property_id_mesh(
            plotter,
            grid,
            show_edges=show_edges and not widgets,
        )
    else:
        mesh_kwargs: dict[str, Any] = {"show_edges": show_edges and not widgets}
        if scalars is not None:
            mesh_kwargs["scalars"] = scalars
        mesh_actor = plotter.add_mesh(grid, **mesh_kwargs)

    axis_legend: list[tuple[str, str]] = []
    axis_actors: list[Any] = []
    if show_local_axes:
        axis_actors, axis_legend = _add_local_axis_glyphs(
            plotter,
            grid,
            mesh,
            max_local_axes=max_local_axes,
            local_axis_scale=local_axis_scale,
            pyvista=pyvista,
        )
    _add_scene_legend(plotter, property_legend + axis_legend)
    if widgets:
        _add_sg_visibility_widgets(
            plotter,
            grid,
            mesh_actor,
            axis_actors,
            show_edges=show_edges,
        )
    return plotter, property_legend


def _add_property_id_mesh(
    plotter: pyvista.Plotter,
    grid: pyvista.UnstructuredGrid,
    *,
    show_edges: bool,
) -> tuple[Any, list[tuple[str, str]]]:
    """Add mesh cells with a discrete property-ID color map and legend."""
    property_ids = np.unique(np.asarray(grid.cell_data["property_id"]))
    category_values = np.searchsorted(property_ids, grid.cell_data["property_id"])
    grid.cell_data[_PROPERTY_CATEGORY_NAME] = category_values
    colors = [_PROPERTY_COLORS[index % len(_PROPERTY_COLORS)] for index in range(len(property_ids))]
    actor = plotter.add_mesh(
        grid,
        scalars=_PROPERTY_CATEGORY_NAME,
        cmap=colors,
        clim=(-0.5, len(property_ids) - 0.5),
        categories=True,
        show_edges=show_edges,
        show_scalar_bar=False,
    )
    legend = [
        (f"Property {property_id:g}", color)
        for property_id, color in zip(property_ids, colors)
    ]
    return actor, legend


def _add_scene_legend(plotter: pyvista.Plotter, labels: list[tuple[str, str]]) -> None:
    """Add one discrete legend shared by property regions and local axes."""
    if labels:
        plotter.add_legend(labels=labels, bcolor="white", face="rectangle", loc="upper right")


def _add_sg_visibility_widgets(
    plotter: pyvista.Plotter,
    grid: pyvista.UnstructuredGrid,
    mesh_actor: Any,
    axis_actors: list[Any],
    *,
    show_edges: bool,
) -> None:
    """Add desktop checkbox widgets that toggle high-level scene actors."""
    edge_actor = plotter.add_mesh(
        grid,
        style="wireframe",
        color="black",
        line_width=1.0,
        name="_sgio_edges",
    )
    edge_actor.SetVisibility(show_edges)
    node_actor = plotter.add_points(
        grid.points,
        color="black",
        point_size=5,
        render_points_as_spheres=True,
        name="_sgio_nodes",
    )
    node_actor.SetVisibility(False)

    controls = [
        ("Local axes", axis_actors, bool(axis_actors)),
        ("Faces", [mesh_actor], True),
        ("Edges", [edge_actor], show_edges),
        ("Nodes", [node_actor], False),
    ]
    for index, (label, actors, value) in enumerate(controls):
        y_position = 210 - 36 * index
        plotter.add_text(label, position=(50, y_position + 6), font_size=10)
        plotter.add_checkbox_button_widget(
            _visibility_callback(actors, plotter),
            value=value,
            position=(10, y_position),
            size=24,
            border_size=1,
        )


def _visibility_callback(actors: list[Any], plotter: pyvista.Plotter) -> Any:
    """Return a PyVista checkbox callback for one actor group."""
    def set_visibility(value: bool) -> None:
        for actor in actors:
            actor.SetVisibility(value)
        plotter.render()

    return set_visibility


def create_pyvista_local_axis_multiblock(
    mesh: SGMesh,
    *,
    max_local_axes: int | None = None,
    local_axis_scale: float | None = None,
) -> pyvista.MultiBlock:
    """Create a VTM-ready mesh and local-axis glyph scene.

    Parameters
    ----------
    mesh : SGMesh
        Mesh providing geometry and element local-coordinate data.
    max_local_axes : int, optional
        Maximum number of cells receiving local-axis glyphs. ``None`` writes
        glyphs for every cell, which is the default for VTM export.
    local_axis_scale : float, optional
        Glyph length in mesh coordinate units. If omitted, the length is 2.5%
        of the mesh bounding-box diagonal.

    Returns
    -------
    pyvista.MultiBlock
        Blocks named ``mesh``, ``local_y1``, ``local_y2``, and ``local_y3``.
        The three local-axis blocks are omitted when no local coordinate system
        is present on the mesh.

    Raises
    ------
    ImportError
        If the optional ``pyvista`` dependency is not installed.
    TypeError
        If ``mesh`` is not an ``SGMesh``.
    ValueError
        If local-axis options or local-coordinate data are invalid.
    """
    if not isinstance(mesh, SGMesh):
        raise TypeError(f"mesh must be an SGMesh; got {type(mesh).__name__}.")

    pyvista = _import_pyvista()
    grid = mesh.to_pyvista()
    blocks = pyvista.MultiBlock()
    blocks["mesh"] = grid
    for axis_name, glyphs in _build_local_axis_glyphs(
        grid,
        mesh,
        max_local_axes=max_local_axes,
        local_axis_scale=local_axis_scale,
        pyvista=pyvista,
    ).items():
        blocks[f"local_{axis_name}"] = glyphs
    return blocks


def plot_pyvista_local_axes(
    vtm_file: str | Path,
    *,
    max_local_axes: int = 500,
    output_html: str | Path | None = None,
    show: bool = False,
) -> pyvista.Plotter:
    """Plot a VTM mesh scene with sampled element local-axis glyphs.

    Parameters
    ----------
    vtm_file : str or pathlib.Path
        VTM file created by :func:`create_pyvista_local_axis_multiblock`.
        It must contain ``mesh``, ``local_y1``, ``local_y2``, and
        ``local_y3`` blocks.
    max_local_axes : int, optional
        Maximum number of source cells rendered as local-axis glyphs. The VTM
        remains complete; this limit applies only to this interactive scene.
        Default is 500.
    output_html : str or pathlib.Path, optional
        Write a self-contained interactive HTML file. The output includes
        browser-native local-axis legend and interaction help.
    show : bool, optional
        Open PyVista's desktop window before returning. Default is ``False``.

    Returns
    -------
    pyvista.Plotter
        Plotter containing the mesh and sampled red, green, and blue glyphs.

    Raises
    ------
    ImportError
        If the optional ``pyvista`` dependency is not installed.
    FileNotFoundError
        If ``vtm_file`` does not exist.
    ValueError
        If the VTM scene or local-axis limit is invalid.
    """
    input_path = Path(vtm_file)
    if not input_path.is_file():
        raise FileNotFoundError(f"VTM file does not exist: {input_path}")

    pyvista = _import_pyvista()
    blocks = pyvista.read(input_path)
    block_names = set(blocks.keys()) if isinstance(blocks, pyvista.MultiBlock) else set()
    required_blocks = {"mesh", *(_VTM_AXIS_COLORS.keys())}
    missing_blocks = required_blocks - block_names
    if missing_blocks:
        raise ValueError(
            "VTM scene is missing required blocks: "
            f"{', '.join(sorted(missing_blocks))}."
        )

    plotter = pyvista.Plotter()
    mesh = blocks["mesh"]
    mesh_kwargs: dict[str, Any] = {"show_edges": True, "show_scalar_bar": False}
    if "property_id" in mesh.cell_data:
        mesh_kwargs["scalars"] = "property_id"
    plotter.add_mesh(mesh, **mesh_kwargs)
    for axis_name, color in _VTM_AXIS_COLORS.items():
        plotter.add_mesh(
            _sample_axis_glyphs(blocks[axis_name], max_local_axes),
            color=color,
            label=_VTM_AXIS_LABELS[axis_name],
        )
    plotter.add_legend(bcolor="white", face="circle", loc="upper right", size=(0.12, 0.12))
    plotter.add_text(_VIEW_HELP, position="upper_left", font_size=10)
    plotter.add_axes()
    plotter.view_yz()

    if output_html is not None:
        html_path = Path(output_html)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        plotter.export_html(str(html_path))
        _add_html_overlay(html_path)
    if show:
        plotter.show()
    return plotter


def _import_pyvista() -> Any:
    """Import PyVista only when a PyVista scene is requested."""
    try:
        import pyvista
    except ModuleNotFoundError as exc:
        raise ImportError(
            "PyVista visualization requires the optional dependency. "
            "Install it with 'uv sync --extra pyvista'."
        ) from exc
    return pyvista


def _validate_scalars(grid: Any, scalars: str | None) -> None:
    """Validate a selected point- or cell-data array for rendering."""
    if scalars is None:
        return
    if not isinstance(scalars, str):
        raise TypeError(f"scalars must be a string or None; got {type(scalars).__name__}.")
    if scalars not in grid.array_names:
        raise ValueError(f"Scalar field {scalars!r} is not present in the PyVista grid.")


def _sample_cell_indices(cell_count: int, max_local_axes: int | None) -> np.ndarray:
    """Return deterministic, evenly distributed cell indices for glyph rendering."""
    if max_local_axes is not None and (
        not isinstance(max_local_axes, int) or max_local_axes <= 0
    ):
        raise ValueError("max_local_axes must be positive.")
    if cell_count <= 0:
        return np.empty(0, dtype=int)
    if max_local_axes is None:
        return np.arange(cell_count, dtype=int)
    return np.linspace(0, cell_count - 1, min(cell_count, max_local_axes), dtype=int)


def _add_local_axis_glyphs(
    plotter: pyvista.Plotter,
    grid: pyvista.UnstructuredGrid,
    mesh: SGMesh,
    *,
    max_local_axes: int,
    local_axis_scale: float | None,
    pyvista: Any,
) -> tuple[list[Any], list[tuple[str, str]]]:
    """Add sampled local y1/y2/y3 arrows and return actors and labels."""
    glyphs_by_name = _build_local_axis_glyphs(
        grid,
        mesh,
        max_local_axes=max_local_axes,
        local_axis_scale=local_axis_scale,
        pyvista=pyvista,
    )
    actors = []
    for axis_name, glyphs in glyphs_by_name.items():
        actors.append(
            plotter.add_mesh(
                glyphs,
                color=_AXIS_COLORS[axis_name],
                label=axis_name,
                lighting=False,
            )
        )
    return actors, [(axis_name, _AXIS_COLORS[axis_name]) for axis_name in glyphs_by_name]


def _build_local_axis_glyphs(
    grid: pyvista.UnstructuredGrid,
    mesh: SGMesh,
    *,
    max_local_axes: int,
    local_axis_scale: float | None,
    pyvista: Any,
) -> dict[str, Any]:
    """Build local-axis arrow geometry for scene actors or VTM blocks."""
    cell_csys_blocks = resolve_element_local_csys(mesh.cell_data, mesh.cells)
    if cell_csys_blocks is None:
        return {}

    cell_indices = _sample_cell_indices(grid.n_cells, max_local_axes)
    if cell_indices.size == 0:
        return {}

    cell_csys = np.concatenate(cell_csys_blocks, axis=0)
    if len(cell_csys) != grid.n_cells:
        raise ValueError(
            "Element local-coordinate data does not align with the PyVista grid cell count."
        )

    axis_length = _resolve_local_axis_scale(grid, local_axis_scale)
    centers = grid.cell_centers().points[cell_indices]
    axes_by_name = _axes_from_csys(cell_csys[cell_indices])
    glyphs_by_name = {}
    for axis_name, vectors in axes_by_name.items():
        seeds = pyvista.PolyData(centers)
        seeds["local_axis"] = vectors
        seeds["source_cell_index"] = cell_indices
        glyphs_by_name[axis_name] = seeds.glyph(
            orient="local_axis",
            scale=False,
            factor=axis_length,
        )
    return glyphs_by_name


def _sample_axis_glyphs(glyphs: Any, max_local_axes: int) -> Any:
    """Return whole glyphs for evenly sampled source-cell indices."""
    if not isinstance(max_local_axes, int) or max_local_axes <= 0:
        raise ValueError("max_local_axes must be positive.")
    source_indices = np.unique(glyphs.point_data["source_cell_index"])
    selected_indices = np.linspace(
        source_indices[0],
        source_indices[-1],
        min(len(source_indices), max_local_axes),
        dtype=int,
    )
    return glyphs.extract_values(
        selected_indices,
        scalars="source_cell_index",
        preference="point",
    )


def _add_html_overlay(
    output_path: Path,
    *,
    property_legend: list[tuple[str, str]] | None = None,
    include_local_axes: bool = True,
) -> None:
    """Add browser-native discrete legends and interaction help to HTML."""
    html = output_path.read_text(encoding="utf-8")
    if "</body>" not in html:
        raise ValueError(f"PyVista HTML output has no closing body tag: {output_path}")
    overlay = _build_html_overlay(
        property_legend=property_legend or [],
        include_local_axes=include_local_axes,
    )
    output_path.write_text(
        html.replace("</body>", f"{overlay}\n</body>", 1),
        encoding="utf-8",
    )


def _build_html_overlay(
    *,
    property_legend: list[tuple[str, str]],
    include_local_axes: bool,
) -> str:
    """Return the DOM overlay for property regions, axes, and view controls."""
    sections: list[str] = []
    if property_legend:
        sections.append(_build_html_legend_section("Properties", property_legend))
    if include_local_axes:
        axis_legend = [(axis_name, color) for axis_name, color in _AXIS_COLORS.items()]
        sections.append(_build_html_legend_section("Local coordinate axes", axis_legend))
    legend = ""
    if sections:
        legend = f'<div id="sgio-scene-legend" class="panel">{"".join(sections)}</div>'
    return "\n".join(
        [
            _HTML_OVERLAY_STYLE,
            '<div id="sgio-view-overlay">',
            legend,
            _HTML_VIEW_HELP,
            "</div>",
        ]
    )


def _build_html_legend_section(title: str, labels: list[tuple[str, str]]) -> str:
    """Return one safely escaped HTML legend section."""
    items = "".join(
        f'<div><span class="swatch" style="background:{escape(color)}"></span>{escape(label)}</div>'
        for label, color in labels
    )
    return f'<div class="section"><div class="title">{escape(title)}</div>{items}</div>'


def _resolve_local_axis_scale(grid: pyvista.UnstructuredGrid, scale: float | None) -> float:
    """Resolve an explicit or bounds-relative glyph length."""
    if scale is not None:
        if not np.isfinite(scale) or scale <= 0.0:
            raise ValueError("local_axis_scale must be positive.")
        return float(scale)

    bounds = np.asarray(grid.bounds, dtype=float).reshape(3, 2)
    diagonal = float(np.linalg.norm(bounds[:, 1] - bounds[:, 0]))
    if diagonal <= 0.0:
        raise ValueError("Cannot derive local-axis scale from zero-size mesh bounds.")
    return diagonal * _DEFAULT_LOCAL_AXIS_SCALE


def _axes_from_csys(cell_csys: np.ndarray) -> dict[str, np.ndarray]:
    """Convert canonical local-coordinate rows into y1/y2/y3 vectors."""
    axes = {"y1": [], "y2": [], "y3": []}
    for csys in cell_csys:
        axis_y1, axis_y2, axis_y3 = property_ref_csys_to_axes(csys)
        axes["y1"].append(axis_y1)
        axes["y2"].append(axis_y2)
        axes["y3"].append(axis_y3)
    return {axis_name: np.asarray(vectors) for axis_name, vectors in axes.items()}
