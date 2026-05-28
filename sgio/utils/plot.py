from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from sgio.utils import math as sgmath

from sgio.core.mesh import SGMesh
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



def plot_line_by_point_angle(ax, point, angle_degrees, color='r', linestyle='--', label='', **kwargs):
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
    sg, model, ax,
    ec_mesh='0.5', fc_mesh='0.9', lw_mesh=0.2,
    legend_kwards={},
    **kwargs):
    """
    Plot a 2D structure gene.

    Parameters
    ----------
    sg : StructureGene
        The 2D structure gene to be plotted.
    model : dict
        The model containing the information of the structure gene.
    ax : matplotlib.axes.Axes
        The axes object to plot on.
    ec_mesh : str, optional
        The edge color of the mesh. Default is '0.5'.
    fc_mesh : str, optional
        The face color of the mesh. Default is '0.9'.
    lw_mesh : float, optional
        The line width of the mesh. Default is 0.2.
    **kwargs : dict, optional
        Additional keyword arguments to pass to matplotlib plotting functions.
    """
    if sg is None or model is None or ax is None:
        raise ValueError("Arguments 'sg', 'model', and 'ax' cannot be None")

    handlers = []
    labels = []

    # Plot the mesh
    if not hasattr(sg, 'mesh'):
        raise ValueError("The 'sg' object must have a 'mesh' attribute")
    plot_2d_mesh(ax, sg.mesh, edge_color=ec_mesh, face_color=fc_mesh, line_width=lw_mesh)

    origin = (0, 0)
    o, = ax.plot(*origin, marker='o', mec='k', mfc='none', markersize=5)
    # handlers.append(o)
    # labels.append('Origin')

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
    half_diag = 0.5 * float(np.linalg.norm(plane_range)) if np.all(np.isfinite(plane_range)) else 1.0
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
    in_plane_pad = 0.05 * max(float(np.max(plane_range)) if np.all(np.isfinite(plane_range)) else 1.0, 1e-9)

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




def _segments_to_plotly_trace_xyz(
    segments_3d: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Flatten 3D segments into NaN-separated x/y/z arrays for plotly.

    Plotly draws disconnected line segments efficiently when all segments
    are put into a single Scatter3d trace with ``NaN`` as a break between
    pairs of endpoints.

    Parameters
    ----------
    segments_3d : np.ndarray
        Array of shape ``(n, 2, 3)``.

    Returns
    -------
    tuple of np.ndarray
        Three 1D arrays ``(x, y, z)`` of length ``3 * n``.
    """
    n = segments_3d.shape[0]
    if n == 0:
        return (np.empty(0), np.empty(0), np.empty(0))
    flat = np.full((n, 3, 3), np.nan, dtype=float)
    flat[:, 0, :] = segments_3d[:, 0, :]
    flat[:, 1, :] = segments_3d[:, 1, :]
    flat = flat.reshape(-1, 3)
    return flat[:, 0], flat[:, 1], flat[:, 2]


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
    input_format, model_type, file_extension, output_extension,
    location_column, section_column, axis, show_principal_axes, pba_scale,
    connect_centers, show_origin_axis
        See :func:`plot_sg_3d_beam`.
    mesh_color : str, optional
        Color string for mesh wireframe lines (plotly notation).
    mesh_width : float, optional
        Mesh line width in pixels.
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
        x, y, z = _segments_to_plotly_trace_xyz(merged)
        traces.append(
            go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(color=mesh_color, width=mesh_width),
                name='Mesh',
                hoverinfo='skip',
            )
        )

    if all_pba2_segs:
        merged = np.stack(all_pba2_segs, axis=0)
        x, y, z = _segments_to_plotly_trace_xyz(merged)
        traces.append(
            go.Scatter3d(
                x=x, y=y, z=z, mode='lines',
                line=dict(color='rgba(70,130,200,0.7)', width=1.5),
                name='Principal bending axis x2',
                hoverinfo='skip',
            )
        )
    if all_pba3_segs:
        merged = np.stack(all_pba3_segs, axis=0)
        x, y, z = _segments_to_plotly_trace_xyz(merged)
        traces.append(
            go.Scatter3d(
                x=x, y=y, z=z, mode='lines',
                line=dict(color='rgba(210,90,90,0.7)', width=1.5),
                name='Principal bending axis x3',
                hoverinfo='skip',
            )
        )

    def _center_traces(points, color, marker_symbol, name_marker, name_line):
        if not points:
            return
        arr = np.asarray(points)
        traces.append(
            go.Scatter3d(
                x=arr[:, 0], y=arr[:, 1], z=arr[:, 2],
                mode='markers',
                marker=dict(symbol=marker_symbol, color=color, size=4, opacity=0.85),
                name=name_marker,
            )
        )
        if connect_centers and len(points) >= 2:
            traces.append(
                go.Scatter3d(
                    x=arr[:, 0], y=arr[:, 1], z=arr[:, 2],
                    mode='lines',
                    line=dict(color=color, width=2),
                    opacity=0.6,
                    name=name_line,
                )
            )

    # Origin reference axis (dotted-style polyline through section origins).
    if origins_3d:
        arr = np.asarray(origins_3d)
        traces.append(
            go.Scatter3d(
                x=arr[:, 0], y=arr[:, 1], z=arr[:, 2],
                mode='markers',
                marker=dict(symbol='circle-open', color='rgba(80,80,80,0.7)', size=4),
                name='Origin',
            )
        )
        if show_origin_axis and len(origins_3d) >= 2:
            traces.append(
                go.Scatter3d(
                    x=arr[:, 0], y=arr[:, 1], z=arr[:, 2],
                    mode='lines',
                    line=dict(color='rgba(80,80,80,1)', width=1.5, dash='dot'),
                    name='Beam reference axis',
                )
            )

    _center_traces(
        mass_centers_3d, 'rgba(70,130,200,1)', 'square',
        'Mass center', 'Mass center line',
    )
    _center_traces(
        tension_centers_3d, 'rgba(170,110,180,1)', 'diamond',
        'Tension center', 'Tension center line',
    )
    _center_traces(
        shear_centers_3d, 'rgba(180,160,80,1)', 'cross',
        'Shear center', 'Shear center line',
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
            **scene_aspect,
        ),
        margin=dict(l=0, r=0, t=40 if title else 0, b=0),
    )

    fig = go.Figure(data=traces, layout=layout_dict)

    if output_html is not None:
        fig.write_html(str(output_html), include_plotlyjs='cdn', full_html=True)
        logger.info("Wrote 3D plot to %s", output_html)

    return fig




def plot_matrix(
    matrix, fig=None, ax=None, cmap='viridis',
    annotate=True, font_size=8,
    **kwargs):
    """
    Plot a heatmap of a given 6x6 matrix.

    Parameters
    ----------
    matrix : np.ndarray
        A 6x6 numpy array to visualize as a heatmap.
    fig : matplotlib.figure.Figure, optional
        The figure object to use for plotting.
    ax : matplotlib.axes.Axes, optional
        The axes object to plot on.
    cmap : str, optional
        Colormap to use for the heatmap. Default is 'viridis'.
    annotate : bool, optional
        Whether to annotate each cell with its value. Default is True.
    font_size : int, optional
        Font size for annotations. Default is 8.
    **kwargs
        Additional keyword arguments for `ax.matshow`.

    Returns
    -------
    matplotlib.image.AxesImage
        The image object for the heatmap.
    """
    
    if fig is None or ax is None:
        raise ValueError("Both 'fig' and 'ax' must be provided")

    if not isinstance(matrix, np.ndarray) or matrix.shape != (6, 6):
        raise ValueError("Input 'matrix' must be a 6x6 numpy array")

    num_rows, num_cols = matrix.shape

    try:
        upper_bound = np.max(np.abs(matrix))
        lower_bound = abs(sgmath.find_min_nonzero_abs(matrix))
    except Exception as e:
        raise ValueError(f"Error in computing bounds: {e}")

    # Plot the matrix
    try:
        cax = ax.matshow(
            matrix, cmap=cmap,
            norm=mcolors.SymLogNorm(
                linthresh=lower_bound, linscale=1,
                vmin=-upper_bound, vmax=upper_bound,
                base=10)
        )
    except Exception as e:
        raise RuntimeError(f"Error in plotting the matrix: {e}")

    # Add a color bar
    try:
        fig.colorbar(cax, ax=ax)
    except Exception as e:
        raise RuntimeError(f"Error in adding colorbar: {e}")

    # Set the ticks and labels
    ax.set_xticks(np.arange(num_cols))
    ax.set_yticks(np.arange(num_rows))
    ax.set_xticklabels(np.arange(1, num_cols + 1))
    ax.set_yticklabels(np.arange(1, num_rows + 1))
    ax.tick_params(axis='both', length=0)

    # Annotate each cell with the numeric value
    if annotate:
        for i in range(num_rows):
            for j in range(num_cols):
                text = f'{matrix[i, j]:.2e}'
                ax.text(j, i, text, fontsize=font_size, ha='center', va='center', color='black')

    return cax
