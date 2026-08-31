"""Optional PyVista scenes for three-dimensional mesh inspection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from sgio.core.mesh import SGMesh
from sgio.core.property_ref_csys import property_ref_csys_to_axes, resolve_element_local_csys

if TYPE_CHECKING:
    import pyvista


_AXIS_COLORS = {"y1": "red", "y2": "green", "y3": "blue"}
_DEFAULT_LOCAL_AXIS_SCALE = 0.025


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

    pyvista = _import_pyvista()
    grid = mesh.to_pyvista()
    _validate_scalars(grid, scalars)

    plotter = pyvista.Plotter()
    mesh_kwargs: dict[str, Any] = {"show_edges": show_edges}
    if scalars is not None:
        mesh_kwargs["scalars"] = scalars
    plotter.add_mesh(grid, **mesh_kwargs)

    if show_local_axes:
        _add_local_axis_glyphs(
            plotter,
            grid,
            mesh,
            max_local_axes=max_local_axes,
            local_axis_scale=local_axis_scale,
            pyvista=pyvista,
        )

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


def _sample_cell_indices(cell_count: int, max_local_axes: int) -> np.ndarray:
    """Return deterministic, evenly distributed cell indices for glyph rendering."""
    if not isinstance(max_local_axes, int) or max_local_axes <= 0:
        raise ValueError("max_local_axes must be positive.")
    if cell_count <= 0:
        return np.empty(0, dtype=int)
    return np.linspace(0, cell_count - 1, min(cell_count, max_local_axes), dtype=int)


def _add_local_axis_glyphs(
    plotter: pyvista.Plotter,
    grid: pyvista.UnstructuredGrid,
    mesh: SGMesh,
    *,
    max_local_axes: int,
    local_axis_scale: float | None,
    pyvista: Any,
) -> None:
    """Add sampled local y1/y2/y3 arrows to an existing PyVista scene."""
    cell_csys_blocks = resolve_element_local_csys(mesh.cell_data, mesh.cells)
    if cell_csys_blocks is None:
        return

    cell_indices = _sample_cell_indices(grid.n_cells, max_local_axes)
    if cell_indices.size == 0:
        return

    cell_csys = np.concatenate(cell_csys_blocks, axis=0)
    if len(cell_csys) != grid.n_cells:
        raise ValueError(
            "Element local-coordinate data does not align with the PyVista grid cell count."
        )

    axis_length = _resolve_local_axis_scale(grid, local_axis_scale)
    centers = grid.cell_centers().points[cell_indices]
    axes_by_name = _axes_from_csys(cell_csys[cell_indices])
    for axis_name, vectors in axes_by_name.items():
        seeds = pyvista.PolyData(centers)
        seeds["local_axis"] = vectors
        arrows = seeds.glyph(orient="local_axis", scale=False, factor=axis_length)
        plotter.add_mesh(
            arrows,
            color=_AXIS_COLORS[axis_name],
            label=axis_name,
            lighting=False,
        )
    plotter.add_legend(bcolor="white", face="circle", size=(0.12, 0.12))


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
