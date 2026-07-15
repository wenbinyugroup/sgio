"""Visualization of structural/material matrices.

This module renders stiffness / compliance (and related) matrices as
annotated heatmaps with a symmetric-log color scale, which keeps both the
large diagonal terms and the small coupling terms readable in a single view.

Two layers are provided:

- :func:`plot_matrix` -- low-level heatmap of any 2D array. Reusable core.
- :func:`plot_model_matrix` -- high-level entry that pulls the matrix *and*
  its physical row/column labels straight from a model object (linear
  elastic, beam, or plate/shell) and delegates to :func:`plot_matrix`.
"""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from sgio.utils import math as sgmath
from sgio.model.query_types import MatrixKind, SectionMatrixKind

logger = logging.getLogger(__name__)


def _resolve_symmetric_range(
    matrix: np.ndarray,
    vmin: float | None,
    vmax: float | None,
) -> tuple[float, float]:
    """Resolve a color/height range, symmetric about 0 by default.

    With neither bound given the range spans ``[-max(|matrix|), +max(|matrix|)]``;
    with exactly one bound given the other mirrors it to the opposite sign;
    with both given they are honored verbatim.
    """
    if vmin is None and vmax is None:
        vmax = float(np.max(np.abs(matrix)))
        vmin = -vmax
    elif vmin is None:
        vmin = -vmax
    elif vmax is None:
        vmax = -vmin
    return vmin, vmax


def _resolve_linthresh(matrix: np.ndarray, linthresh: float | None) -> float:
    """Resolve the symmetric-log linear-region half-width (must be positive)."""
    if linthresh is None:
        linthresh = abs(sgmath.find_min_nonzero_abs(matrix))
    if linthresh <= 0:
        raise ValueError(f"linthresh must be positive; got {linthresh}")
    return linthresh


def _build_norm(
    matrix: np.ndarray,
    symlog: bool,
    vmin: float | None,
    vmax: float | None,
    linthresh: float | None,
) -> tuple[mcolors.Normalize, float]:
    """Build a color normalization shared by the heatmap and bar3d plots.

    Returns the norm and the effective ``linthresh`` (0 when ``symlog`` is
    ``False``).
    """
    vmin, vmax = _resolve_symmetric_range(matrix, vmin, vmax)
    if symlog:
        linthresh = _resolve_linthresh(matrix, linthresh)
        norm = mcolors.SymLogNorm(
            linthresh=linthresh, linscale=1,
            vmin=vmin, vmax=vmax, base=10,
        )
        return norm, linthresh
    return mcolors.Normalize(vmin=vmin, vmax=vmax), 0.0


def plot_matrix(
    matrix,
    fig=None,
    ax=None,
    row_labels: Sequence[str] | None = None,
    col_labels: Sequence[str] | None = None,
    cmap: str = 'RdBu_r',
    annotate: bool = True,
    font_size: int = 8,
    symlog: bool = True,
    vmin: float | None = None,
    vmax: float | None = None,
    linthresh: float | None = None,
    **kwargs,
):
    """Plot a heatmap of an arbitrary 2D matrix.

    By default the color scale is centered on 0 and symmetric
    (``vmin = -vmax``), so a diverging colormap places the neutral color at
    zero and mirrors the sign of each entry. It defaults to a symmetric-log
    (``SymLogNorm``) mapping so that entries spanning several orders of
    magnitude -- typical of stiffness / compliance matrices -- remain
    simultaneously legible.

    The color range can be overridden with ``vmin`` / ``vmax``. Passing only
    one of them mirrors it to the opposite sign so the scale stays symmetric;
    passing both uses them verbatim (which may be asymmetric).

    Parameters
    ----------
    matrix : array_like
        A 2D array (``n_rows`` x ``n_cols``) to visualize.
    fig : matplotlib.figure.Figure
        Figure used to attach the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.
    row_labels : sequence of str, optional
        Tick labels for the rows. Defaults to ``1 .. n_rows``.
    col_labels : sequence of str, optional
        Tick labels for the columns. Defaults to ``1 .. n_cols``.
    cmap : str, optional
        Colormap name. Default ``'coolwarm'`` (diverging, neutral at 0).
    annotate : bool, optional
        Whether to annotate each cell with its value. Default ``True``.
    font_size : int, optional
        Font size for the annotations. Default ``8``.
    symlog : bool, optional
        Use a symmetric-log color scale. When ``False`` a linear scale is
        used. Default ``True``.
    vmin, vmax : float, optional
        Lower / upper bounds of the color scale. When both are ``None`` the
        scale spans ``[-max(|matrix|), +max(|matrix|)]``. When only one is
        given, the other defaults to its negation (symmetric scale).
    linthresh : float, optional
        Half-width of the linear region around 0 for the symmetric-log scale.
        Only used when ``symlog`` is ``True``. Defaults to the smallest
        nonzero absolute entry of the matrix. Must be positive.
    **kwargs
        Extra keyword arguments forwarded to ``ax.matshow``.

    Returns
    -------
    matplotlib.image.AxesImage
        The heatmap image object.
    """
    if fig is None or ax is None:
        raise ValueError("Both 'fig' and 'ax' must be provided")

    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2:
        raise ValueError(f"'matrix' must be 2D; got shape {matrix.shape}")

    num_rows, num_cols = matrix.shape

    # Color normalization: symmetric about 0, symmetric-log by default.
    norm, _ = _build_norm(matrix, symlog, vmin, vmax, linthresh)

    cax = ax.matshow(matrix, cmap=cmap, norm=norm, **kwargs)
    fig.colorbar(cax, ax=ax)

    # Ticks and labels.
    ax.set_xticks(np.arange(num_cols))
    ax.set_yticks(np.arange(num_rows))
    ax.set_xticklabels(
        col_labels if col_labels is not None else np.arange(1, num_cols + 1)
    )
    ax.set_yticklabels(
        row_labels if row_labels is not None else np.arange(1, num_rows + 1)
    )
    ax.tick_params(axis='both', length=0)

    # Annotate each cell with its numeric value.
    if annotate:
        for i in range(num_rows):
            for j in range(num_cols):
                ax.text(
                    j, i, f'{matrix[i, j]:.2e}',
                    fontsize=font_size, ha='center', va='center', color='black',
                )

    return cax


def _symlog_heights(values: np.ndarray, linthresh: float) -> np.ndarray:
    """Signed symmetric-log transform of matrix values into bar heights.

    Compresses several orders of magnitude while preserving sign, so both the
    large diagonal terms and the small coupling terms stay visible as 3D bars.
    """
    return np.sign(values) * np.log10(1.0 + np.abs(values) / linthresh)


def _symlog_zticks(
    vmax_abs: float, linthresh: float, max_per_side: int = 6,
) -> tuple[list[float], list[str]]:
    """Decade z-tick positions/labels for the symmetric-log bar heights."""
    kmin = int(np.floor(np.log10(linthresh)))
    kmax = int(np.ceil(np.log10(vmax_abs))) if vmax_abs > 0 else kmin
    ks = list(range(kmin, kmax + 1))
    # Thin the decades so the axis does not get overcrowded with ticks.
    if len(ks) > max_per_side:
        stride = int(np.ceil(len(ks) / max_per_side))
        ks = ks[::stride]
    decades = np.array([10.0 ** k for k in ks], dtype=float)
    values = np.concatenate([-decades[::-1], [0.0], decades])
    positions = _symlog_heights(values, linthresh)
    labels = ['0' if v == 0 else f'{v:.0e}' for v in values]
    return list(positions), labels


def plot_matrix_bar3d(
    matrix,
    fig=None,
    ax=None,
    row_labels: Sequence[str] | None = None,
    col_labels: Sequence[str] | None = None,
    cmap: str = 'RdBu_r',
    symlog: bool = True,
    vmin: float | None = None,
    vmax: float | None = None,
    linthresh: float | None = None,
    bar_width: float = 0.7,
    **kwargs,
):
    """Plot a 2D matrix as a 3D bar chart using matplotlib ``bar3d``.

    Each entry becomes a bar whose height encodes its value and whose color is
    mapped through ``cmap`` with a scale symmetric about 0. By default both the
    bar heights and the color scale use a symmetric-log mapping, so the large
    diagonal terms and the tiny coupling terms of a stiffness / compliance
    matrix are legible together. Positive entries rise; negative entries drop.

    Parameters
    ----------
    matrix : array_like
        A 2D array (``n_rows`` x ``n_cols``) to visualize.
    fig : matplotlib.figure.Figure
        Figure used to attach the colorbar.
    ax : mpl_toolkits.mplot3d.axes3d.Axes3D
        A 3D axes to plot on. Create with ``fig.add_subplot(projection='3d')``.
    row_labels : sequence of str, optional
        Tick labels for the rows. Defaults to ``1 .. n_rows``.
    col_labels : sequence of str, optional
        Tick labels for the columns. Defaults to ``1 .. n_cols``.
    cmap : str, optional
        Colormap name. Default ``'RdBu_r'`` (diverging, neutral at 0).
    symlog : bool, optional
        Use a symmetric-log scale for both bar heights and color. When
        ``False`` a linear scale is used. Default ``True``.
    vmin, vmax : float, optional
        Bounds of the color scale. When both are ``None`` the scale spans
        ``[-max(|matrix|), +max(|matrix|)]``. When only one is given, the
        other defaults to its negation (symmetric scale).
    linthresh : float, optional
        Half-width of the linear region around 0 for the symmetric-log scale
        (used for both heights and color). Only used when ``symlog`` is
        ``True``. Defaults to the smallest nonzero absolute entry. Must be
        positive.
    bar_width : float, optional
        Bar footprint width in cell units (0 < ``bar_width`` <= 1). Default
        ``0.7``.
    **kwargs
        Extra keyword arguments forwarded to ``ax.bar3d``.

    Returns
    -------
    mpl_toolkits.mplot3d.art3d.Poly3DCollection
        The bar collection returned by ``ax.bar3d``.
    """
    if fig is None or ax is None:
        raise ValueError("Both 'fig' and 'ax' must be provided")
    if not hasattr(ax, 'bar3d'):
        raise ValueError(
            "ax must be a 3D axes; create with fig.add_subplot(projection='3d')"
        )

    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2:
        raise ValueError(f"'matrix' must be 2D; got shape {matrix.shape}")

    num_rows, num_cols = matrix.shape

    # Color normalization: symmetric about 0, symmetric-log by default.
    norm, eff_linthresh = _build_norm(matrix, symlog, vmin, vmax, linthresh)
    colormap = plt.get_cmap(cmap)

    # Bar footprint positions; center each bar on its (col, row) cell.
    xs, ys = np.meshgrid(np.arange(num_cols), np.arange(num_rows))
    xpos = xs.ravel().astype(float) - bar_width / 2
    ypos = ys.ravel().astype(float) - bar_width / 2
    zpos = np.zeros_like(xpos)

    values = matrix.ravel()
    # Bar heights: symlog-compressed (signed) or raw values.
    if symlog:
        heights = _symlog_heights(values, eff_linthresh)
    else:
        heights = values
    colors = colormap(norm(values))

    bars = ax.bar3d(
        xpos, ypos, zpos,
        bar_width, bar_width, heights,
        color=colors, shade=True, **kwargs,
    )

    # Colorbar keyed to the true values.
    mappable = plt.cm.ScalarMappable(norm=norm, cmap=colormap)
    mappable.set_array([])
    fig.colorbar(mappable, ax=ax, shrink=0.6, pad=0.1)

    # Row/column ticks; invert the row axis so row 1 reads at the back.
    ax.set_xticks(np.arange(num_cols))
    ax.set_yticks(np.arange(num_rows))
    ax.set_xticklabels(
        col_labels if col_labels is not None else np.arange(1, num_cols + 1)
    )
    ax.set_yticklabels(
        row_labels if row_labels is not None else np.arange(1, num_rows + 1)
    )
    ax.invert_yaxis()

    # Height (z) axis: label decades on the symmetric-log scale.
    if symlog:
        vmax_abs = max(abs(norm.vmin), abs(norm.vmax))
        positions, labels = _symlog_zticks(vmax_abs, eff_linthresh)
        ax.set_zticks(positions)
        ax.set_zticklabels(labels)

    return bars


# ---------------------------------------------------------------------------
# High-level model-aware matrix plotting (skeleton)
# ---------------------------------------------------------------------------

# Normalize the user-facing ``kind`` argument to the typed selectors used by
# the two different model APIs (material-level vs. section-level).
_MATERIAL_KIND = {
    'stiffness': MatrixKind.STIFFNESS,
    'compliance': MatrixKind.COMPLIANCE,
}
_SECTION_KIND = {
    'stiffness': SectionMatrixKind.STIFFNESS,
    'compliance': SectionMatrixKind.COMPLIANCE,
}

# Voigt component labels for the 6x6 linear-elastic (solid) matrices, which
# carry no theory schema of their own.
_VOIGT_LABELS = ['11', '22', '33', '23', '13', '12']


def _extract_model_matrix(
    model, kind: str,
) -> tuple[np.ndarray, list[str] | None, list[str] | None]:
    """Extract a matrix and its physical labels from a model.

    Dispatches on the model API:

    - Beam and plate/shell section models expose :meth:`get_section_matrix`
      taking a :class:`~sgio.model.query_types.SectionMatrixKind`, and a
      ``theory_schema`` describing per-matrix row/column quantities.
    - Linear-elastic (solid) models expose :meth:`get_matrix` taking a
      :class:`~sgio.model.query_types.MatrixKind`; rows/columns are the
      6 Voigt stress/strain components.

    Parameters
    ----------
    model : object
        A linear-elastic, beam, or plate/shell model instance.
    kind : {'stiffness', 'compliance'}
        Which matrix to extract.

    Returns
    -------
    matrix : np.ndarray
        The extracted 2D matrix.
    row_labels, col_labels : list of str or None
        Physical quantity labels for the rows/columns, or ``None`` when the
        model does not provide them.
    """
    key = kind.lower()
    if key not in _MATERIAL_KIND:
        raise ValueError(
            f"kind must be one of {sorted(_MATERIAL_KIND)}; got {kind!r}"
        )

    # --- Section-level models (beam / plate-shell) ---
    if hasattr(model, 'get_section_matrix'):
        section_kind = _SECTION_KIND[key]
        matrix = model.get_section_matrix(section_kind)
        if matrix is None:
            raise ValueError(
                f"{type(model).__name__} has no {key} matrix"
            )
        # Row/column physical labels come from the theory schema, keyed by the
        # model attribute backing this matrix kind.
        attr = model._SECTION_MATRIX_ATTRS[section_kind]
        schema = model.theory_schema.matrices[attr]
        row_labels = list(schema.row_quantities)
        col_labels = list(schema.column_quantities)
        return np.asarray(matrix, dtype=float), row_labels, col_labels

    # --- Material-level models (linear elastic / solid) ---
    if hasattr(model, 'get_matrix'):
        matrix = model.get_matrix(_MATERIAL_KIND[key])
        if matrix is None:
            raise ValueError(
                f"{type(model).__name__} has no {key} matrix"
            )
        return np.asarray(matrix, dtype=float), list(_VOIGT_LABELS), list(_VOIGT_LABELS)

    raise TypeError(
        f"Unsupported model type for matrix plotting: {type(model).__name__}"
    )


def plot_model_matrix(
    model,
    kind: str = 'stiffness',
    fig=None,
    ax=None,
    cmap: str = 'RdBu_r',
    annotate: bool = True,
    font_size: int = 8,
    symlog: bool = True,
    title: str | None = None,
    **kwargs,
):
    """Plot the stiffness / compliance matrix of a structural model.

    High-level convenience wrapper that resolves the requested matrix and its
    physical row/column labels from ``model`` and renders it via
    :func:`plot_matrix`. Supports linear-elastic (solid), beam, and
    plate/shell models.

    Parameters
    ----------
    model : object
        A linear-elastic, beam, or plate/shell model instance.
    kind : {'stiffness', 'compliance'}, optional
        Which matrix to plot. Default ``'stiffness'``.
    fig : matplotlib.figure.Figure, optional
        Figure to draw on. A new one is created when omitted.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on. A new one is created when omitted.
    cmap : str, optional
        Colormap name. Default ``'coolwarm'`` (diverging, neutral at 0).
    annotate : bool, optional
        Annotate each cell with its value. Default ``True``.
    font_size : int, optional
        Annotation font size. Default ``8``.
    symlog : bool, optional
        Use a symmetric-log color scale. Default ``True``.
    title : str, optional
        Axes title. Defaults to a description built from the model/kind.
    **kwargs
        Forwarded to :func:`plot_matrix`.

    Returns
    -------
    (matplotlib.figure.Figure, matplotlib.axes.Axes)
        The figure and axes containing the heatmap.
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots()

    matrix, row_labels, col_labels = _extract_model_matrix(model, kind)

    plot_matrix(
        matrix, fig=fig, ax=ax,
        row_labels=row_labels, col_labels=col_labels,
        cmap=cmap, annotate=annotate, font_size=font_size, symlog=symlog,
        **kwargs,
    )

    if title is None:
        title = f"{type(model).__name__} {kind}"
    ax.set_title(title)

    return fig, ax
