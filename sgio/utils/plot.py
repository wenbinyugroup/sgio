import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.collections import PatchCollection

from sgio.utils import math as sgmath

from sgio.core.mesh import SGMesh



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

    origin = (0, 0)
    tension_center = (model.get('tc2'), model.get('tc3'))
    shear_center = (model.get('sc2'), model.get('sc3'))
    mass_center = (model.get('mc2'), model.get('mc3'))

    phi_pba_2 = model.get('phi_pba')
    if phi_pba_2 is None:
        raise ValueError("Model must contain 'phi_pba'")
    phi_pba_3 = phi_pba_2 + 90

    if not hasattr(sg, 'mesh'):
        raise ValueError("The 'sg' object must have a 'mesh' attribute")
    
    # Plot the mesh
    plot_2d_mesh(ax, sg.mesh, edge_color=ec_mesh, face_color=fc_mesh, line_width=lw_mesh)

    # Plot the principal bending axes
    plot_line_by_point_angle(ax, origin, phi_pba_2, color='b')
    plot_line_by_point_angle(ax, origin, phi_pba_3, color='r')

    # Plot the centers
    ax.plot(*origin, marker='o', mec='k', mfc='none', markersize=5)
    ax.plot(*mass_center, ls='none', marker='s', mec='C0', mfc='none', markersize=5)
    ax.plot(*tension_center, ls='none', marker='p', mec='C4', mfc='none', markersize=5)
    ax.plot(*shear_center, ls='none', marker='d', mec='C8', mfc='none', markersize=5)

    # Add a legend
    ax.legend(
        ['Principal bending axis x2', 'Principal bending axis x3',
         'Mass center', 'Tension center', 'Shear center'],
        ncols=5,
        bbox_to_anchor=(0.5, 1),
        loc='lower center',
    )









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
