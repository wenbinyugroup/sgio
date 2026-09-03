from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from sgio.core.mesh import SGMesh
from sgio.core.sg import StructureGene
from sgio.model.query_types import SectionAxis, SectionCenter

logger = logging.getLogger(__name__)


# Cell type -> list of (i, j) node index pairs defining edges.
# For quadratic elements, edges follow the gmsh ordering used elsewhere in plot.py.
_CELL_EDGES = {
    'triangle': [(0, 1), (1, 2), (2, 0)],
    'triangle6': [(0, 3), (3, 1), (1, 4), (4, 2), (2, 5), (5, 0)],
    'quad': [(0, 1), (1, 2), (2, 3), (3, 0)],
    'quad8': [(0, 4), (4, 1), (1, 5), (5, 2), (2, 6), (6, 3), (3, 7), (7, 0)],
    'quad9': [(0, 4), (4, 1), (1, 5), (5, 2), (2, 6), (6, 3), (3, 7), (7, 0)],
}



def plot_line_by_point_angle(
    ax, point, angle_degrees, color='r', linestyle='--', label='', **kwargs
):
    """
    Plot a line on the given axes object.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to plot on.
    point : tuple
        A tuple (x, y) representing a point on the line.
    angle_degrees : float
        The angle in degrees between the line and the x-axis.
    color : str, optional
        Color of the line. Default is 'r'.
    linestyle : str, optional
        Line style, e.g., '--' for dashed. Default is '--'.
    label : str, optional
        Label for the line. Default is ''.
    kwargs : dict, optional
        Additional keyword arguments for the plotting function.

    Returns
    -------
    line : matplotlib.lines.Line2D
        The plotted line.
    """

    # Convert angle from degrees to radians
    angle_radians = np.deg2rad(angle_degrees)

    # Calculate the slope of the line
    slope = np.tan(angle_radians)

    # Plot the line
    line = ax.axline(point, slope=slope, color=color, linestyle=linestyle, label=label, **kwargs)

    # Return the plotted line
    return line









def plot_2d_mesh(
    ax, mesh,
    edge_color='black', face_color='none', line_width=0.5,
    padding=0.05, **kwargs):
    """
    Plot a 2D mesh using matplotlib with axis limits set beyond the bounding box of the mesh.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to plot on.
    mesh : meshio.Mesh
        The meshio mesh object to be visualized.
    edge_color : str, optional
        The color of the edges of the mesh. Default is 'black'.
    face_color : str, optional
        The color of the faces of the mesh. Default is 'none'.
    line_width : float, optional
        The width of the edges of the mesh. Default is 0.5.
    padding : float, optional
        Fractional padding around the mesh bounding box. Default is 0.05.
    **kwargs : dict, optional
        Additional keyword arguments to pass to matplotlib plotting functions.
    """
    if ax is None:
        raise ValueError('ax argument cannot be None')

    if mesh is None:
        raise ValueError('mesh argument cannot be None')

    if not isinstance(mesh, SGMesh):
        raise ValueError('mesh argument must be a sgio.core.mesh.SGMesh object')

    if mesh.points is None:
        raise ValueError('The mesh must have points')

    if mesh.cells is None:
        raise ValueError('The mesh must have cells')

    # Set aspect ratio to equal for accurate representation
    ax.set_aspect('equal')

    # Calculate the minimum and maximum coordinates of the mesh
    min_x, min_y = np.min(mesh.points[:, 1:], axis=0)
    max_x, max_y = np.max(mesh.points[:, 1:], axis=0)

    # Compute the ranges for x and y
    range_x = max_x - min_x
    range_y = max_y - min_y

    # Prepare a list to store polygon patches
    patches = []
    for cell_block in mesh.cells:
        cell_type = cell_block.type
        cell_data = cell_block.data

        if cell_type == 'triangle':
            # Create polygons for triangles
            for triangle in cell_data:
                if triangle is None:
                    raise ValueError('A triangle cell is None')
                if len(triangle) != 3:
                    raise ValueError('A triangle cell must have 3 nodes')
                pts = mesh.points[triangle, 1:]
                polygon = plt.Polygon(
                    pts, edgecolor=edge_color, facecolor=face_color, linewidth=line_width)
                patches.append(polygon)

        elif cell_type == 'triangle6':
            # Create polygons for quadratic triangles with 6 nodes
            for triangle in cell_data:
                if triangle is None:
                    raise ValueError('A triangle cell is None')
                if len(triangle) != 6:
                    raise ValueError('A triangle6 cell must have 6 nodes')
                pts = mesh.points[triangle[[0, 3, 1, 4, 2, 5]], 1:]
                polygon = plt.Polygon(
                    pts, edgecolor=edge_color, facecolor=face_color, linewidth=line_width)
                patches.append(polygon)

        elif cell_type == 'quad':
            # Create polygons for quadrilaterals
            for quad in cell_data:
                if quad is None:
                    raise ValueError('A quad cell is None')
                if len(quad) != 4:
                    raise ValueError('A quad cell must have 4 nodes')
                pts = mesh.points[quad, 1:]
                polygon = plt.Polygon(
                    pts, edgecolor=edge_color, facecolor=face_color, linewidth=line_width)
                patches.append(polygon)

    # Create a PatchCollection from the list of polygons
    patch_collection = PatchCollection(patches, match_original=True)
    ax.add_collection(patch_collection)

    # Set the limits of the axes with specified padding
    ax.set_xlim(min_x - padding * range_x, max_x + padding * range_x)
    ax.set_ylim(min_y - padding * range_y, max_y + padding * range_y)









def plot_sg_2d(
    sg, ax=None,
    ec_mesh='0.5', fc_mesh='0.9', lw_mesh=0.2,
    show_origin=True,
    **kwargs):
    """
    Plot the mesh of a 2D structure gene.

    Draws only the section geometry (mesh and, optionally, the origin
    marker). The constitutive-model overlays (principal bending axes and
    feature centers) are drawn separately by :func:`plot_model_2d`, so the two
    can be combined on the same axes or used independently.

    Parameters
    ----------
    sg : StructureGene
        The 2D structure gene to be plotted.
    ax : matplotlib.axes.Axes
        The axes object to plot on.
    ec_mesh : str, optional
        The edge color of the mesh. Default is '0.5'.
    fc_mesh : str, optional
        The face color of the mesh. Default is '0.9'.
    lw_mesh : float, optional
        The line width of the mesh. Default is 0.2.
    show_origin : bool, optional
        Whether to mark the section origin (0, 0). Default is True.
    **kwargs : dict, optional
        Additional keyword arguments to pass to matplotlib plotting functions.
    """
    if sg is None or ax is None:
        raise ValueError("Arguments 'sg' and 'ax' cannot be None")

    # Plot the mesh
    if not hasattr(sg, 'mesh'):
        raise ValueError("The 'sg' object must have a 'mesh' attribute")
    plot_2d_mesh(ax, sg.mesh, edge_color=ec_mesh, face_color=fc_mesh, line_width=lw_mesh)

    if show_origin:
        ax.plot(0, 0, marker='o', mec='k', mfc='none', markersize=5)


def plot_sg_matplotlib(
    sg: StructureGene,
    *,
    ax: Any | None = None,
    figure_size: tuple[float, float] = (10.0, 8.0),
    edge_color: str = '0.5',
    face_color: str = '0.9',
    line_width: float = 0.2,
    show_origin: bool = True,
) -> Any:
    """Plot one structure-gene cross-section with matplotlib.

    This is the single-section matplotlib entry point. It creates an axes when
    one is not supplied, draws the SG mesh in its ``(x2, x3)`` plane, and
    returns the axes for caller-controlled labels, model overlays, and file
    output. Use :func:`plot_sg_2d` when composing into an existing axes is the
    primary concern.

    Parameters
    ----------
    sg : StructureGene
        Structure gene containing a two-dimensional section mesh.
    ax : matplotlib.axes.Axes, optional
        Existing axes to draw on. A new figure and axes are created by default.
    figure_size : tuple of float, optional
        Size in inches used only when creating a new figure. Default is
        ``(10.0, 8.0)``.
    edge_color : str, optional
        Mesh edge color. Default is ``'0.5'``.
    face_color : str, optional
        Mesh face color. Default is ``'0.9'``.
    line_width : float, optional
        Mesh edge line width. Default is ``0.2``.
    show_origin : bool, optional
        Whether to mark the section origin. Default is ``True``.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the section mesh.

    Raises
    ------
    TypeError
        If ``sg`` is not a :class:`~sgio.StructureGene`.
    ValueError
        If ``sg`` has no mesh.
    """
    _validate_plot_sg(sg)
    if ax is None:
        _, ax = plt.subplots(figsize=figure_size)
    plot_sg_2d(
        sg,
        ax,
        ec_mesh=edge_color,
        fc_mesh=face_color,
        lw_mesh=line_width,
        show_origin=show_origin,
    )
    return ax


def plot_model_2d(
    model, ax=None,
    origin=(0, 0),
    legend_kwards={},
    **kwargs):
    """
    Plot the constitutive-model overlays of a 2D beam section.

    Draws the principal bending axes and the feature centers (mass / tension /
    shear) derived from the analysis result. Intended to be combined with
    :func:`plot_sg_2d`, which draws the underlying section mesh, but can also
    be used on its own.

    Parameters
    ----------
    model : object
        The constitutive model providing the principal axes (via
        ``get_axis_angle``) and feature centers (via ``get_center``).
    ax : matplotlib.axes.Axes
        The axes object to plot on.
    origin : tuple of float, optional
        The section origin through which the principal axes pass. Default is
        ``(0, 0)``.
    legend_kwards : dict, optional
        Keyword arguments forwarded to ``ax.legend``. If empty, a default
        legend placement is used.
    **kwargs : dict, optional
        Additional keyword arguments to pass to matplotlib plotting functions.
    """
    if model is None or ax is None:
        raise ValueError("Arguments 'model' and 'ax' cannot be None")

    handlers = []
    labels = []

    # Plot the principal bending axes
    phi_pba_2 = model.get_axis_angle(SectionAxis.BENDING)
    if phi_pba_2 is None:
        raise ValueError("Model must contain 'phi_pba'")
    phi_pba_3 = phi_pba_2 + 90
    pba_2 = plot_line_by_point_angle(ax, origin, phi_pba_2, color='b')
    pba_3 = plot_line_by_point_angle(ax, origin, phi_pba_3, color='r')
    handlers.extend([pba_2, pba_3])
    labels.extend(['Principal bending axis x2', 'Principal bending axis x3'])

    # Plot the centers

    mass_center = model.get_center(SectionCenter.MASS)
    mc, = ax.plot(*mass_center, ls='none', marker='s', mec='C0', mfc='none', markersize=5)
    handlers.append(mc)
    labels.append('Mass center')

    tension_center = model.get_center(SectionCenter.TENSION)
    tc, = ax.plot(*tension_center, ls='none', marker='p', mec='C4', mfc='none', markersize=5)
    handlers.append(tc)
    labels.append('Tension center')

    if model.label == 'bm2':
        shear_center = model.get_center(SectionCenter.SHEAR)
        sc, = ax.plot(*shear_center, ls='none', marker='d', mec='C8', mfc='none', markersize=5)
        handlers.append(sc)
        labels.append('Shear center')

    # Add a legend
    if legend_kwards:
        ax.legend(
            handlers, labels,
            **legend_kwards
        )
    else:
        ax.legend(
            handlers, labels,
            ncols=5,
            bbox_to_anchor=(0.5, 1),
            loc='lower center',
        )









def _extract_section_edges(
    mesh: SGMesh, mode: str = 'regions'
) -> np.ndarray:
    """Extract edges from a 2D section mesh.

    Parameters
    ----------
    mesh : SGMesh
        Section mesh whose ``points`` columns 1 and 2 are the (x2, x3) coords.
    mode : {'wireframe', 'boundary', 'regions'}, optional
        - ``'wireframe'``: every unique element edge.
        - ``'boundary'``: only edges on the outer section boundary (each
          shared by exactly one element).
        - ``'regions'`` (default): outer-boundary edges plus material
          interfaces — edges shared by two elements with different
          ``property_id``. Gives a clean layup outline at a fraction of
          the cost of a full wireframe.

    Returns
    -------
    np.ndarray
        Array of shape ``(n_edges, 2, 2)`` with edge endpoint (x2, x3)
        coords.
    """
    if mode not in ('wireframe', 'boundary', 'regions'):
        raise ValueError(
            f"mode must be one of 'wireframe', 'boundary', 'regions'; got {mode!r}"
        )

    points_2d = mesh.points[:, 1:3]

    # Map sorted edge key -> list of property_ids of incident elements.
    # For 'wireframe', we just need uniqueness — empty list is fine.
    edge_props: dict[tuple[int, int], list[int]] = {}

    property_arrays = mesh.cell_data.get('property_id') if mode == 'regions' else None

    for block_idx, cell_block in enumerate(mesh.cells):
        edge_template = _CELL_EDGES.get(cell_block.type)
        if edge_template is None:
            continue
        prop_array = None
        if property_arrays is not None and block_idx < len(property_arrays):
            prop_array = np.asarray(property_arrays[block_idx], dtype=int)
        for cell_idx, cell in enumerate(cell_block.data):
            pid = int(prop_array[cell_idx]) if prop_array is not None else 0
            for i, j in edge_template:
                a, b = int(cell[i]), int(cell[j])
                key = (a, b) if a < b else (b, a)
                edge_props.setdefault(key, []).append(pid)

    if not edge_props:
        return np.empty((0, 2, 2), dtype=float)

    if mode == 'wireframe':
        keys = list(edge_props.keys())
    elif mode == 'boundary':
        keys = [k for k, props in edge_props.items() if len(props) == 1]
    else:  # 'regions'
        keys = [
            k for k, props in edge_props.items()
            if len(props) == 1 or len(set(props)) > 1
        ]

    if not keys:
        return np.empty((0, 2, 2), dtype=float)

    segs = np.empty((len(keys), 2, 2), dtype=float)
    for k, (a, b) in enumerate(keys):
        segs[k, 0] = points_2d[a]
        segs[k, 1] = points_2d[b]
    return segs


def _embed_segments_3d(
    segments_2d: np.ndarray, location: float, axis: int
) -> np.ndarray:
    """Embed 2D (x2, x3) segments into 3D at a given spanwise location.

    Parameters
    ----------
    segments_2d : np.ndarray
        Array of shape ``(n, 2, 2)``.
    location : float
        Spanwise position along the chosen axis.
    axis : int
        Index of the spanwise axis (0, 1 or 2) in the 3D output.

    Returns
    -------
    np.ndarray
        Array of shape ``(n, 2, 3)``.
    """
    n = segments_2d.shape[0]
    segs_3d = np.empty((n, 2, 3), dtype=float)
    plane_axes = [a for a in range(3) if a != axis]
    segs_3d[:, :, axis] = location
    segs_3d[:, :, plane_axes[0]] = segments_2d[:, :, 0]
    segs_3d[:, :, plane_axes[1]] = segments_2d[:, :, 1]
    return segs_3d


def _section_point_to_3d(
    point_2d: Sequence[float], location: float, axis: int
) -> np.ndarray:
    """Embed one 2D section point into 3D."""
    p = np.zeros(3, dtype=float)
    plane_axes = [a for a in range(3) if a != axis]
    p[axis] = location
    p[plane_axes[0]] = point_2d[0]
    p[plane_axes[1]] = point_2d[1]
    return p


def _principal_axis_segment_2d(
    origin: Sequence[float], angle_degrees: float, half_length: float
) -> np.ndarray:
    """Return a 2D line segment centred on ``origin`` along a given angle."""
    a = np.deg2rad(angle_degrees)
    direction = np.array([np.cos(a), np.sin(a)], dtype=float)
    p0 = np.asarray(origin, dtype=float) - half_length * direction
    p1 = np.asarray(origin, dtype=float) + half_length * direction
    return np.stack([p0, p1], axis=0)


def _load_sections_from_layout(
    layout: Iterable[tuple[float, str]],
    section_dir: str | Path,
    input_format: str,
    model_type: str,
    file_extension: str | None,
    output_extension: str,
    **read_kwargs,
) -> list[tuple[float, str, "object", "object"]]:
    """Load (sg, model) for every layout row.

    Returns a list of ``(location, section_name, sg, model)`` tuples.
    """
    from sgio.iofunc.main import read, read_output_model
    from sgio.iofunc.utils import resolve_section_path

    sections: list[tuple[float, str, object, object]] = []
    root = Path(section_dir)
    for location, section_name in layout:
        section_path = resolve_section_path(
            section_name=section_name,
            section_dir=root,
            file_extension=file_extension,
            input_format=input_format,
        )
        logger.info("Loading section %s at location=%s", section_path, location)
        sg = read(
            str(section_path),
            file_format=input_format,
            model_type=model_type,
            **read_kwargs,
        )
        output_path = section_path.with_suffix(section_path.suffix + output_extension)
        if not output_path.exists():
            raise FileNotFoundError(
                f"Section result file not found: {output_path}"
            )
        model = read_output_model(
            str(output_path),
            file_format=input_format,
            model_type=model_type,
            sg=sg,
        )
        if model is None:
            raise RuntimeError(
                f"Failed to read section result from {output_path}"
            )
        sections.append((float(location), section_name, sg, model))
    return sections


def plot_sg_3d_beam(
    csv_file: str | Path,
    section_dir: str | Path,
    ax,
    input_format: str = 'vabs',
    model_type: str = 'BM2',
    file_extension: str | None = None,
    output_extension: str = '.K',
    location_column: str = 'location',
    section_column: str = 'cs',
    axis: int = 0,
    ec_mesh: str = '0.5',
    lw_mesh: float = 0.3,
    mesh_style: str = 'regions',
    show_principal_axes: bool = True,
    pba_scale: float = 0.6,
    connect_centers: bool = True,
    show_origin_axis: bool = True,
    aspect_mode: str = 'cube',
    legend_kwargs: dict | None = None,
    **read_kwargs,
):
    """Plot multiple beam cross-sections in 3D along the spanwise direction.

    For every section listed in the layout CSV the function loads the
    structure gene (mesh) and the analysis result (constitutive model with
    centers and principal axes), then renders each section as a wireframe in
    a 3D matplotlib axes. Feature centers (mass / tension / shear) are
    connected across sections by polylines.

    Parameters
    ----------
    csv_file : str or Path
        Layout CSV file. Must contain a location column and a section column.
    section_dir : str or Path
        Directory containing the section input files.
    ax : mpl_toolkits.mplot3d.axes3d.Axes3D
        A 3D matplotlib axes object to plot on. Create with
        ``fig.add_subplot(projection='3d')``.
    input_format : str, optional
        Format of section input files (``'vabs'``, ``'sc'``,
        ``'swiftcomp'``). Default is ``'vabs'``.
    model_type : str, optional
        Macro structural model type. Default is ``'BM2'`` (Timoshenko beam).
    file_extension : str, optional
        Explicit section file extension; if ``None``, inferred from
        ``input_format``.
    output_extension : str, optional
        Extension appended to the section path to locate the analysis
        result file. Default is ``'.K'`` (so ``foo.sg`` -> ``foo.sg.K``).
    location_column : str, optional
        Name of the location column in the CSV. Default ``'location'``.
    section_column : str, optional
        Name of the section column in the CSV. Default ``'cs'``.
    axis : int, optional
        Spanwise axis index (0, 1, or 2). Default 0 (x is spanwise).
    ec_mesh : str, optional
        Mesh edge color. Default ``'0.5'``.
    lw_mesh : float, optional
        Mesh line width. Default ``0.3``.
    show_principal_axes : bool, optional
        Whether to draw principal bending axes at each section. Default True.
    pba_scale : float, optional
        Principal-axis segment length as a fraction of half the section's
        in-plane bounding-box diagonal. Default 0.6.
    connect_centers : bool, optional
        Whether to draw 3D polylines connecting mass / tension / shear
        centers across sections. Default True.
    show_origin_axis : bool, optional
        Whether to draw a reference line through (0, 0) of each section.
        Default True.
    legend_kwargs : dict, optional
        Extra keyword arguments forwarded to ``ax.legend``.
    **read_kwargs
        Extra keyword arguments forwarded to :func:`sgio.read`.

    Returns
    -------
    dict
        Diagnostic dictionary with keys ``'locations'``, ``'mass_centers'``,
        ``'tension_centers'``, ``'shear_centers'`` (each a list of 3D
        points), and ``'sections'`` (the loaded ``(location, name, sg,
        model)`` tuples).
    """
    from sgio.iofunc.layout import read_section_layout_csv

    if ax is None:
        raise ValueError("ax must be a 3D matplotlib axes")
    if not hasattr(ax, 'add_collection3d'):
        raise ValueError(
            "ax must be a 3D axes; create with fig.add_subplot(projection='3d')"
        )
    if axis not in (0, 1, 2):
        raise ValueError(f"axis must be 0, 1, or 2; got {axis}")

    layout = read_section_layout_csv(
        csv_file=csv_file,
        location_column=location_column,
        section_column=section_column,
    )
    sections = _load_sections_from_layout(
        layout=layout,
        section_dir=section_dir,
        input_format=input_format,
        model_type=model_type,
        file_extension=file_extension,
        output_extension=output_extension,
        **read_kwargs,
    )

    locations: list[float] = []
    mass_centers_3d: list[np.ndarray] = []
    tension_centers_3d: list[np.ndarray] = []
    shear_centers_3d: list[np.ndarray] = []
    origins_3d: list[np.ndarray] = []

    plane_axes = [a for a in range(3) if a != axis]

    # Track in-plane extents to set axis limits and scale axis-line lengths.
    plane_min = np.array([np.inf, np.inf])
    plane_max = np.array([-np.inf, -np.inf])

    for location, section_name, sg, model in sections:
        locations.append(location)

        if sg.mesh is None:
            raise ValueError(f"Section '{section_name}' has no mesh")
        section_pts = sg.mesh.points[:, 1:3]
        if section_pts.size > 0:
            plane_min = np.minimum(plane_min, section_pts.min(axis=0))
            plane_max = np.maximum(plane_max, section_pts.max(axis=0))

        # Mesh wireframe.
        segs_2d = _extract_section_edges(sg.mesh, mode=mesh_style)
        if segs_2d.shape[0] > 0:
            segs_3d = _embed_segments_3d(segs_2d, location, axis)
            collection = Line3DCollection(
                segs_3d, colors=ec_mesh, linewidths=lw_mesh
            )
            ax.add_collection3d(collection)

        # Feature centers.
        origin_3d = _section_point_to_3d((0.0, 0.0), location, axis)
        origins_3d.append(origin_3d)

        mass_center = model.get_center(SectionCenter.MASS)
        mc_3d = _section_point_to_3d(mass_center, location, axis)
        mass_centers_3d.append(mc_3d)

        tension_center = model.get_center(SectionCenter.TENSION)
        tc_3d = _section_point_to_3d(tension_center, location, axis)
        tension_centers_3d.append(tc_3d)

        if getattr(model, 'label', '') == 'bm2':
            shear_center = model.get_center(SectionCenter.SHEAR)
            sc_3d = _section_point_to_3d(shear_center, location, axis)
            shear_centers_3d.append(sc_3d)

    # In-plane half-extent used to size principal-axis segments.
    plane_range = plane_max - plane_min
    half_diag = (
        0.5 * float(np.linalg.norm(plane_range))
        if np.all(np.isfinite(plane_range))
        else 1.0
    )
    pba_half_len = max(pba_scale * half_diag, 1e-9)

    # Per-section principal bending axes.
    if show_principal_axes:
        pba_segs_2: list[np.ndarray] = []
        pba_segs_3: list[np.ndarray] = []
        for (location, _name, _sg, model) in sections:
            phi2 = model.get_axis_angle(SectionAxis.BENDING)
            if phi2 is None:
                continue
            phi3 = phi2 + 90.0
            seg2_2d = _principal_axis_segment_2d((0.0, 0.0), phi2, pba_half_len)
            seg3_2d = _principal_axis_segment_2d((0.0, 0.0), phi3, pba_half_len)
            pba_segs_2.append(_embed_segments_3d(seg2_2d[None, :, :], location, axis)[0])
            pba_segs_3.append(_embed_segments_3d(seg3_2d[None, :, :], location, axis)[0])
        if pba_segs_2:
            ax.add_collection3d(
                Line3DCollection(pba_segs_2, colors='b', linewidths=0.8)
            )
        if pba_segs_3:
            ax.add_collection3d(
                Line3DCollection(pba_segs_3, colors='r', linewidths=0.8)
            )

    handlers: list = []
    labels: list[str] = []

    def _scatter(points, marker, edge_color, label):
        if not points:
            return None
        arr = np.asarray(points)
        h = ax.scatter(
            arr[:, 0], arr[:, 1], arr[:, 2],
            marker=marker, edgecolors=edge_color, facecolors='none',
            s=30, depthshade=False,
        )
        handlers.append(h)
        labels.append(label)
        return h

    _scatter(origins_3d, 'o', 'k', 'Origin')
    _scatter(mass_centers_3d, 's', 'C0', 'Mass center')
    _scatter(tension_centers_3d, 'p', 'C4', 'Tension center')
    _scatter(shear_centers_3d, 'd', 'C8', 'Shear center')

    # Connecting polylines across sections.
    if connect_centers:
        def _polyline(points, color, label, linestyle='-'):
            if len(points) < 2:
                return
            arr = np.asarray(points)
            line, = ax.plot(
                arr[:, 0], arr[:, 1], arr[:, 2],
                color=color, linestyle=linestyle, linewidth=1.2,
            )
            handlers.append(line)
            labels.append(label)

        if show_origin_axis:
            _polyline(origins_3d, 'k', 'Beam reference axis', linestyle=':')
        _polyline(mass_centers_3d, 'C0', 'Mass center line')
        _polyline(tension_centers_3d, 'C4', 'Tension center line')
        _polyline(shear_centers_3d, 'C8', 'Shear center line')

    # Set sensible 3D axis limits so the spans aren't dwarfed by the section.
    spanwise_min = min(locations) if locations else 0.0
    spanwise_max = max(locations) if locations else 1.0
    span_pad = 0.05 * max(spanwise_max - spanwise_min, 1.0)
    largest_plane_range = (
        float(np.max(plane_range)) if np.all(np.isfinite(plane_range)) else 1.0
    )
    in_plane_pad = 0.05 * max(largest_plane_range, 1e-9)

    limits = [None, None, None]
    limits[axis] = (spanwise_min - span_pad, spanwise_max + span_pad)
    limits[plane_axes[0]] = (
        float(plane_min[0]) - in_plane_pad,
        float(plane_max[0]) + in_plane_pad,
    )
    limits[plane_axes[1]] = (
        float(plane_min[1]) - in_plane_pad,
        float(plane_max[1]) + in_plane_pad,
    )
    ax.set_xlim(*limits[0])
    ax.set_ylim(*limits[1])
    ax.set_zlim(*limits[2])

    if aspect_mode == 'cube':
        box_aspect = (1.0, 1.0, 1.0)
    elif aspect_mode == 'data':
        box_aspect = (
            limits[0][1] - limits[0][0],
            limits[1][1] - limits[1][0],
            limits[2][1] - limits[2][0],
        )
    else:
        raise ValueError(
            f"aspect_mode must be 'cube' or 'data'; got {aspect_mode!r}"
        )
    try:
        ax.set_box_aspect(box_aspect)
    except Exception:
        pass

    if legend_kwargs is None:
        ax.legend(handlers, labels, loc='upper left', fontsize=8)
    else:
        ax.legend(handlers, labels, **legend_kwargs)

    return {
        'locations': locations,
        'mass_centers': mass_centers_3d,
        'tension_centers': tension_centers_3d,
        'shear_centers': shear_centers_3d,
        'sections': sections,
    }




def _segments_to_nan_coords(
    segments_nd: np.ndarray,
) -> tuple[np.ndarray, ...]:
    """Flatten ``(n, 2, D)`` line segments into ``D`` NaN-separated arrays.

    Plotly draws many disconnected line segments efficiently when they are
    placed in a single trace with ``NaN`` separating each endpoint pair.
    Works for both 2D (``D == 2``) and 3D (``D == 3``) segments, so the same
    routine serves the 2D and 3D section plots.

    Parameters
    ----------
    segments_nd : np.ndarray
        Array of shape ``(n, 2, D)``.

    Returns
    -------
    tuple of np.ndarray
        ``D`` 1D arrays, each of length ``3 * n``.
    """
    segments_nd = np.asarray(segments_nd, dtype=float)
    n, _, d = segments_nd.shape
    if n == 0:
        return tuple(np.empty(0) for _ in range(d))
    flat = np.full((n, 3, d), np.nan, dtype=float)
    flat[:, 0, :] = segments_nd[:, 0, :]
    flat[:, 1, :] = segments_nd[:, 1, :]
    flat = flat.reshape(-1, d)
    return tuple(flat[:, i] for i in range(d))


def _line_trace(
    segments_nd: np.ndarray, name: str, color: str, width: float,
    dash: str | None = None, hoverinfo: str = 'skip',
):
    """Build a plotly line trace from ``(n, 2, D)`` segments.

    Returns a :class:`plotly.graph_objects.Scatter` for 2D segments
    (``D == 2``) or a :class:`plotly.graph_objects.Scatter3d` for 3D
    segments (``D == 3``).
    """
    import plotly.graph_objects as go

    coords = _segments_to_nan_coords(segments_nd)
    line = dict(color=color, width=width)
    if dash is not None:
        line['dash'] = dash
    if len(coords) == 2:
        return go.Scatter(
            x=coords[0], y=coords[1], mode='lines',
            line=line, name=name, hoverinfo=hoverinfo,
        )
    return go.Scatter3d(
        x=coords[0], y=coords[1], z=coords[2], mode='lines',
        line=line, name=name, hoverinfo=hoverinfo,
    )


def _points_trace(
    points_nd, name: str, color: str, mode: str,
    symbol: str | None = None, size: int = 4,
    opacity: float = 1.0, width: float = 2, dash: str | None = None,
):
    """Build a plotly marker/line trace from a sequence of points.

    Auto-selects 2D vs 3D scatter from the point dimensionality, so it
    serves both the 2D and 3D section plots. ``mode`` is the plotly scatter
    mode (``'markers'`` or ``'lines'``).
    """
    import plotly.graph_objects as go

    arr = np.atleast_2d(np.asarray(points_nd, dtype=float))
    d = arr.shape[1]
    kwargs: dict = dict(mode=mode, name=name)
    if 'markers' in mode:
        kwargs['marker'] = dict(symbol=symbol, color=color, size=size, opacity=opacity)
    if 'lines' in mode:
        line = dict(color=color, width=width)
        if dash is not None:
            line['dash'] = dash
        kwargs['line'] = line
        kwargs['opacity'] = opacity
    if d == 2:
        return go.Scatter(x=arr[:, 0], y=arr[:, 1], **kwargs)
    return go.Scatter3d(x=arr[:, 0], y=arr[:, 1], z=arr[:, 2], **kwargs)


def _add_center_traces(
    traces: list, points, color: str, symbol: str,
    name_marker: str, name_line: str | None = None, connect: bool = False,
):
    """Append marker (and optional connecting-line) traces for feature points.

    ``points`` is a sequence of 2D or 3D points. The connecting line is only
    added when ``connect`` is True, ``name_line`` is given and there are at
    least two points (used by the 3D multi-section plot).
    """
    if points is None or len(points) == 0:
        return
    traces.append(
        _points_trace(points, name_marker, color, 'markers', symbol=symbol, opacity=0.85)
    )
    if connect and name_line is not None and len(points) >= 2:
        traces.append(
            _points_trace(points, name_line, color, 'lines', width=2, opacity=0.6)
        )


def _compose_2d_figure(fig, traces: list, title: str):
    """Add ``traces`` to a 2D section figure, creating one if needed.

    When ``fig`` is ``None`` a new figure is created with the standard 2D
    section layout (equal aspect, x2/x3 axis titles); otherwise the traces are
    appended to the existing figure so :func:`plot_sg_2d_plotly` and
    :func:`plot_model_2d_plotly` can share one figure.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure or None
        Existing figure to add to, or ``None`` to create a new one.
    traces : list
        Plotly traces to add.
    title : str
        Figure title, applied only when a new figure is created.

    Returns
    -------
    plotly.graph_objects.Figure
        The figure the traces were added to.
    """
    import plotly.graph_objects as go

    if fig is None:
        layout_dict = dict(
            title=title,
            xaxis_title='x2',
            yaxis_title='x3',
            # Equal aspect ratio so the section is not distorted.
            yaxis=dict(scaleanchor='x', scaleratio=1),
            margin=dict(l=0, r=0, t=40 if title else 10, b=0),
        )
        fig = go.Figure(layout=layout_dict)
    if traces:
        fig.add_traces(traces)
    return fig


def plot_sg_2d_plotly(
    sg,
    mesh_style: str = 'regions',
    mesh_color: str = 'rgba(30,30,30,0.9)',
    mesh_width: float = 1.5,
    show_origin: bool = True,
    fig=None,
    output_html: str | Path | None = None,
    title: str = '',
):
    """Plot the mesh of a single 2D cross-section using plotly.

    Plotly counterpart of :func:`plot_sg_2d`. Renders only the section
    geometry (mesh as a region outline or full wireframe, plus an optional
    origin marker). The constitutive-model overlays are drawn separately by
    :func:`plot_model_2d_plotly`; pass its returned ``fig`` between the two (or
    the same ``fig``) to combine them.

    Parameters
    ----------
    sg : StructureGene
        The 2D structure gene to plot; must have a ``mesh`` attribute.
    mesh_style : {'regions', 'boundary', 'wireframe'}, optional
        Mesh rendering style; see :func:`_extract_section_edges`. Default
        ``'regions'``.
    mesh_color : str, optional
        Color string for mesh lines (plotly notation).
    mesh_width : float, optional
        Mesh line width in pixels. Default 1.5.
    show_origin : bool, optional
        Whether to mark the section origin (0, 0). Default True.
    fig : plotly.graph_objects.Figure, optional
        Existing figure to add the mesh traces to. If ``None`` a new figure is
        created. Default ``None``.
    output_html : str or Path, optional
        If given, the figure is written to this HTML file.
    title : str, optional
        Optional figure title (used only when creating a new figure).

    Returns
    -------
    plotly.graph_objects.Figure
        The figure the mesh was added to.
    """
    if sg is None:
        raise ValueError("Argument 'sg' cannot be None")
    if getattr(sg, 'mesh', None) is None:
        raise ValueError("The 'sg' object must have a mesh")

    traces: list = []

    # Mesh region outline / wireframe.
    segs_2d = _extract_section_edges(sg.mesh, mode=mesh_style)
    if segs_2d.shape[0] > 0:
        traces.append(_line_trace(segs_2d, 'Mesh', mesh_color, mesh_width))

    # Origin marker.
    if show_origin:
        _add_center_traces(
            traces, [(0.0, 0.0)], 'rgba(80,80,80,0.7)', 'circle-open', 'Origin'
        )

    fig = _compose_2d_figure(fig, traces, title)

    if output_html is not None:
        fig.write_html(str(output_html), include_plotlyjs='cdn', full_html=True)
        logger.info("Wrote 2D plot to %s", output_html)

    return fig


def plot_sg_plotly(
    sg: StructureGene,
    *,
    mesh_style: str = 'regions',
    mesh_color: str = 'rgba(30,30,30,0.9)',
    mesh_width: float = 1.5,
    show_origin: bool = True,
    fig: Any | None = None,
    output_html: str | Path | None = None,
    title: str = '',
) -> Any:
    """Plot one structure-gene cross-section with Plotly.

    This is the single-section Plotly entry point. It returns the native
    Plotly figure, which callers can continue to customize or write to HTML.
    Use :func:`plot_sg_2d_plotly` when composing geometry with model overlays
    in an existing figure is the primary concern.

    Parameters
    ----------
    sg : StructureGene
        Structure gene containing a two-dimensional section mesh.
    mesh_style : {'regions', 'boundary', 'wireframe'}, optional
        Mesh rendering style. Default is ``'regions'``.
    mesh_color : str, optional
        Plotly color for mesh lines.
    mesh_width : float, optional
        Mesh line width in pixels. Default is ``1.5``.
    show_origin : bool, optional
        Whether to mark the section origin. Default is ``True``.
    fig : plotly.graph_objects.Figure, optional
        Existing figure to draw on.
    output_html : str or pathlib.Path, optional
        Optional output HTML file.
    title : str, optional
        Figure title when a new figure is created.

    Returns
    -------
    plotly.graph_objects.Figure
        Figure containing the section mesh.

    Raises
    ------
    TypeError
        If ``sg`` is not a :class:`~sgio.StructureGene`.
    ValueError
        If ``sg`` has no mesh.
    """
    _validate_plot_sg(sg)
    return plot_sg_2d_plotly(
        sg,
        mesh_style=mesh_style,
        mesh_color=mesh_color,
        mesh_width=mesh_width,
        show_origin=show_origin,
        fig=fig,
        output_html=output_html,
        title=title,
    )


def _validate_plot_sg(sg: StructureGene) -> None:
    """Validate the common structure-gene input for high-level plotters."""
    if not isinstance(sg, StructureGene):
        raise TypeError(f"sg must be a StructureGene; got {type(sg).__name__}.")
    if sg.mesh is None:
        raise ValueError("sg must contain a mesh.")


def plot_model_2d_plotly(
    model, sg=None,
    pba_length: float | None = None,
    pba_scale: float = 0.6,
    show_principal_axes: bool = True,
    show_centers: bool = True,
    fig=None,
    output_html: str | Path | None = None,
    title: str = '',
):
    """Plot the constitutive-model overlays of a 2D beam section using plotly.

    Plotly counterpart of :func:`plot_model_2d`. Renders the principal bending
    axes and the feature centers (mass / tension / shear). Intended to be
    combined with :func:`plot_sg_2d_plotly` by sharing the ``fig``, but can be
    used on its own.

    Because the principal-axis segments are drawn with a finite length, their
    size is taken from ``pba_length`` if given, otherwise from the section
    in-plane extent (when ``sg`` is provided), otherwise a unit length.

    Parameters
    ----------
    model : object
        Constitutive model with ``get_center`` / ``get_axis_angle`` methods.
    sg : StructureGene, optional
        Structure gene whose mesh sets the principal-axis segment length when
        ``pba_length`` is not given. Default ``None``.
    pba_length : float, optional
        Explicit half-length of the principal-axis segments. Overrides the
        value derived from ``sg``. Default ``None``.
    pba_scale : float, optional
        Principal-axis segment length as a fraction of half the section's
        in-plane bounding-box diagonal (used only when the length is derived
        from ``sg``). Default 0.6.
    show_principal_axes : bool, optional
        Whether to draw the principal bending axes. Default True.
    show_centers : bool, optional
        Whether to draw mass / tension / shear centers. Default True.
    fig : plotly.graph_objects.Figure, optional
        Existing figure to add the overlay traces to. If ``None`` a new figure
        is created. Default ``None``.
    output_html : str or Path, optional
        If given, the figure is written to this HTML file.
    title : str, optional
        Optional figure title (used only when creating a new figure).

    Returns
    -------
    plotly.graph_objects.Figure
        The figure the overlays were added to.
    """
    if model is None:
        raise ValueError("Argument 'model' cannot be None")

    traces: list = []

    # Determine the principal-axis segment half-length.
    if pba_length is not None:
        pba_half_len = max(float(pba_length), 1e-9)
    elif sg is not None and getattr(sg, 'mesh', None) is not None:
        section_pts = sg.mesh.points[:, 1:3]
        if section_pts.size > 0:
            plane_range = section_pts.max(axis=0) - section_pts.min(axis=0)
            half_diag = 0.5 * float(np.linalg.norm(plane_range))
        else:
            half_diag = 1.0
        pba_half_len = max(pba_scale * half_diag, 1e-9)
    else:
        pba_half_len = 1.0

    # Principal bending axes.
    if show_principal_axes:
        phi2 = model.get_axis_angle(SectionAxis.BENDING)
        if phi2 is not None:
            phi3 = phi2 + 90.0
            seg2 = _principal_axis_segment_2d((0.0, 0.0), phi2, pba_half_len)
            seg3 = _principal_axis_segment_2d((0.0, 0.0), phi3, pba_half_len)
            traces.append(
                _line_trace(seg2[None, :, :], 'Principal bending axis x2',
                            'rgba(70,130,200,0.7)', 1.5)
            )
            traces.append(
                _line_trace(seg3[None, :, :], 'Principal bending axis x3',
                            'rgba(210,90,90,0.7)', 1.5)
            )

    # Feature centers (single section -> one point each).
    if show_centers:
        _add_center_traces(
            traces, [tuple(model.get_center(SectionCenter.MASS))],
            'rgba(70,130,200,1)', 'square', 'Mass center',
        )
        _add_center_traces(
            traces, [tuple(model.get_center(SectionCenter.TENSION))],
            'rgba(170,110,180,1)', 'diamond', 'Tension center',
        )
        if getattr(model, 'label', '') == 'bm2':
            _add_center_traces(
                traces, [tuple(model.get_center(SectionCenter.SHEAR))],
                'rgba(180,160,80,1)', 'cross', 'Shear center',
            )

    fig = _compose_2d_figure(fig, traces, title)

    if output_html is not None:
        fig.write_html(str(output_html), include_plotlyjs='cdn', full_html=True)
        logger.info("Wrote 2D plot to %s", output_html)

    return fig


def plot_sg_3d_beam_plotly(
    csv_file: str | Path,
    section_dir: str | Path,
    input_format: str = 'vabs',
    model_type: str = 'BM2',
    file_extension: str | None = None,
    output_extension: str = '.K',
    location_column: str = 'location',
    section_column: str = 'cs',
    axis: int = 0,
    mesh_color: str = 'rgba(30,30,30,0.9)',
    mesh_width: float = 1.5,
    mesh_style: str = 'regions',
    show_principal_axes: bool = True,
    pba_scale: float = 0.6,
    connect_centers: bool = True,
    show_origin_axis: bool = True,
    aspect_mode: str = 'cube',
    projection: str = 'orthographic',
    show_projection_buttons: bool = True,
    output_html: str | Path | None = None,
    title: str = '',
    **read_kwargs,
):
    """Plot multiple beam cross-sections in 3D using plotly (HTML output).

    Functionally equivalent to :func:`plot_sg_3d_beam` but renders with
    plotly so the interactive 3D view runs smoothly in a browser even for
    meshes with thousands of edges.

    Parameters
    ----------
    csv_file : str or Path
        Layout CSV file.
    section_dir : str or Path
        Directory containing section input files.
    input_format : str, optional
        See :func:`plot_sg_3d_beam`.
    model_type : str, optional
        See :func:`plot_sg_3d_beam`.
    file_extension : str, optional
        See :func:`plot_sg_3d_beam`.
    output_extension : str, optional
        See :func:`plot_sg_3d_beam`.
    location_column : str, optional
        See :func:`plot_sg_3d_beam`.
    section_column : str, optional
        See :func:`plot_sg_3d_beam`.
    axis : int, optional
        See :func:`plot_sg_3d_beam`.
    show_principal_axes : bool, optional
        See :func:`plot_sg_3d_beam`.
    pba_scale : float, optional
        See :func:`plot_sg_3d_beam`.
    connect_centers : bool, optional
        See :func:`plot_sg_3d_beam`.
    show_origin_axis : bool, optional
        See :func:`plot_sg_3d_beam`.
    mesh_color : str, optional
        Color string for mesh wireframe lines (plotly notation).
    mesh_width : float, optional
        Mesh line width in pixels.
    projection : {'orthographic', 'perspective'}, optional
        Initial 3D camera projection type. Default ``'orthographic'``.
    show_projection_buttons : bool, optional
        Whether to add HTML buttons for switching between orthographic and
        perspective projection. Default True.
    output_html : str or Path, optional
        If given, the figure is written to this HTML file.
    title : str, optional
        Optional figure title.
    **read_kwargs
        Forwarded to :func:`sgio.read`.

    Returns
    -------
    plotly.graph_objects.Figure
        The constructed plotly figure.
    """
    import plotly.graph_objects as go

    from sgio.iofunc.layout import read_section_layout_csv

    if axis not in (0, 1, 2):
        raise ValueError(f"axis must be 0, 1, or 2; got {axis}")
    if projection not in ('orthographic', 'perspective'):
        raise ValueError(
            f"projection must be 'orthographic' or 'perspective'; got {projection!r}"
        )

    layout = read_section_layout_csv(
        csv_file=csv_file,
        location_column=location_column,
        section_column=section_column,
    )
    sections = _load_sections_from_layout(
        layout=layout,
        section_dir=section_dir,
        input_format=input_format,
        model_type=model_type,
        file_extension=file_extension,
        output_extension=output_extension,
        **read_kwargs,
    )

    all_mesh_segs: list[np.ndarray] = []
    all_pba2_segs: list[np.ndarray] = []
    all_pba3_segs: list[np.ndarray] = []
    origins_3d: list[np.ndarray] = []
    mass_centers_3d: list[np.ndarray] = []
    tension_centers_3d: list[np.ndarray] = []
    shear_centers_3d: list[np.ndarray] = []

    plane_min = np.array([np.inf, np.inf])
    plane_max = np.array([-np.inf, -np.inf])

    # First pass: meshes, centers, plane extents.
    for location, section_name, sg, model in sections:
        if sg.mesh is None:
            raise ValueError(f"Section '{section_name}' has no mesh")
        section_pts = sg.mesh.points[:, 1:3]
        if section_pts.size > 0:
            plane_min = np.minimum(plane_min, section_pts.min(axis=0))
            plane_max = np.maximum(plane_max, section_pts.max(axis=0))

        segs_2d = _extract_section_edges(sg.mesh, mode=mesh_style)
        if segs_2d.shape[0] > 0:
            all_mesh_segs.append(_embed_segments_3d(segs_2d, location, axis))

        origins_3d.append(_section_point_to_3d((0.0, 0.0), location, axis))
        mass_centers_3d.append(
            _section_point_to_3d(model.get_center(SectionCenter.MASS), location, axis)
        )
        tension_centers_3d.append(
            _section_point_to_3d(model.get_center(SectionCenter.TENSION), location, axis)
        )
        if getattr(model, 'label', '') == 'bm2':
            shear_centers_3d.append(
                _section_point_to_3d(model.get_center(SectionCenter.SHEAR), location, axis)
            )

    plane_range = plane_max - plane_min
    half_diag = (
        0.5 * float(np.linalg.norm(plane_range))
        if np.all(np.isfinite(plane_range))
        else 1.0
    )
    pba_half_len = max(pba_scale * half_diag, 1e-9)

    # Second pass: principal bending axes (need pba_half_len).
    if show_principal_axes:
        for location, _name, _sg, model in sections:
            phi2 = model.get_axis_angle(SectionAxis.BENDING)
            if phi2 is None:
                continue
            phi3 = phi2 + 90.0
            seg2 = _principal_axis_segment_2d((0.0, 0.0), phi2, pba_half_len)
            seg3 = _principal_axis_segment_2d((0.0, 0.0), phi3, pba_half_len)
            all_pba2_segs.append(
                _embed_segments_3d(seg2[None, :, :], location, axis)[0]
            )
            all_pba3_segs.append(
                _embed_segments_3d(seg3[None, :, :], location, axis)[0]
            )

    traces: list = []

    # Mesh wireframe — one consolidated trace for performance.
    if all_mesh_segs:
        merged = np.concatenate(all_mesh_segs, axis=0)
        traces.append(_line_trace(merged, 'Mesh', mesh_color, mesh_width))

    if all_pba2_segs:
        merged = np.stack(all_pba2_segs, axis=0)
        traces.append(
            _line_trace(merged, 'Principal bending axis x2',
                        'rgba(70,130,200,0.7)', 1.5)
        )
    if all_pba3_segs:
        merged = np.stack(all_pba3_segs, axis=0)
        traces.append(
            _line_trace(merged, 'Principal bending axis x3',
                        'rgba(210,90,90,0.7)', 1.5)
        )

    # Origin reference axis (dotted-style polyline through section origins).
    if origins_3d:
        _add_center_traces(
            traces, origins_3d, 'rgba(80,80,80,0.7)', 'circle-open', 'Origin'
        )
        if show_origin_axis and len(origins_3d) >= 2:
            traces.append(
                _points_trace(origins_3d, 'Beam reference axis',
                              'rgba(80,80,80,1)', 'lines', width=1.5, dash='dot')
            )

    _add_center_traces(
        traces, mass_centers_3d, 'rgba(70,130,200,1)', 'square',
        'Mass center', 'Mass center line', connect=connect_centers,
    )
    _add_center_traces(
        traces, tension_centers_3d, 'rgba(170,110,180,1)', 'diamond',
        'Tension center', 'Tension center line', connect=connect_centers,
    )
    _add_center_traces(
        traces, shear_centers_3d, 'rgba(180,160,80,1)', 'cross',
        'Shear center', 'Shear center line', connect=connect_centers,
    )

    # Build figure with a manual data-aspect ratio so the spanwise axis
    # isn't stretched out of proportion with the section in-plane size.
    spanwise_min = min(p[axis] for p in origins_3d) if origins_3d else 0.0
    spanwise_max = max(p[axis] for p in origins_3d) if origins_3d else 1.0
    span_len = max(spanwise_max - spanwise_min, 1e-9)
    in_plane_size = (
        float(max(plane_range)) if np.all(np.isfinite(plane_range)) else 1.0
    )
    in_plane_size = max(in_plane_size, 1e-9)

    # Map global axis index 0/1/2 (spanwise=x1, in-plane=x2/x3) to plotly's
    # x/y/z scene axes so the in-plane axes always show as x2 and x3.
    axis_keys = ['x', 'y', 'z']
    plane_axes = [a for a in range(3) if a != axis]
    axis_labels = {axis: 'x1', plane_axes[0]: 'x2', plane_axes[1]: 'x3'}

    if aspect_mode == 'cube':
        scene_aspect = dict(aspectmode='cube')
    elif aspect_mode == 'data':
        scene_aspect = dict(aspectmode='data')
    elif aspect_mode == 'manual':
        sizes = {axis: span_len, plane_axes[0]: in_plane_size, plane_axes[1]: in_plane_size}
        scene_aspect = dict(
            aspectmode='manual',
            aspectratio={axis_keys[i]: sizes[i] for i in range(3)},
        )
    else:
        raise ValueError(
            f"aspect_mode must be 'cube', 'data', or 'manual'; got {aspect_mode!r}"
        )

    layout_dict = dict(
        title=title,
        scene=dict(
            xaxis_title=axis_labels[0],
            yaxis_title=axis_labels[1],
            zaxis_title=axis_labels[2],
            camera=dict(
                projection=dict(type=projection),
            ),
            **scene_aspect,
        ),
        margin=dict(l=0, r=0, t=40 if title else 0, b=0),
    )
    if show_projection_buttons:
        layout_dict['updatemenus'] = [
            dict(
                type='buttons',
                direction='left',
                x=0.02,
                y=0.98,
                xanchor='left',
                yanchor='top',
                buttons=[
                    dict(
                        label='Orthographic',
                        method='relayout',
                        args=[{'scene.camera.projection.type': 'orthographic'}],
                    ),
                    dict(
                        label='Perspective',
                        method='relayout',
                        args=[{'scene.camera.projection.type': 'perspective'}],
                    ),
                ],
            )
        ]

    fig = go.Figure(data=traces, layout=layout_dict)

    if output_html is not None:
        fig.write_html(str(output_html), include_plotlyjs='cdn', full_html=True)
        logger.info("Wrote 3D plot to %s", output_html)

    return fig
