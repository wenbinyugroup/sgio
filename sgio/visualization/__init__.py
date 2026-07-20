"""Visualization tools for structure genes, sections and matrices.

Built on matplotlib and plotly. Two concerns:

- :mod:`sgio.visualization.section` -- geometry: 2D/3D cross-section meshes,
  principal axes and feature centers (matplotlib and plotly backends).
- :mod:`sgio.visualization.matrix` -- stiffness / compliance matrix heatmaps
  for linear-elastic, beam and plate/shell models.
"""

from .section import (
    plot_line_by_point_angle,
    plot_2d_mesh,
    plot_sg_2d,
    plot_model_2d,
    plot_sg_2d_plotly,
    plot_model_2d_plotly,
    plot_sg_3d_beam,
    plot_sg_3d_beam_plotly,
)
from .matrix import (
    plot_matrix,
    plot_matrix_bar3d,
    plot_model_matrix,
)

__all__ = [
    'plot_line_by_point_angle',
    'plot_2d_mesh',
    'plot_sg_2d',
    'plot_model_2d',
    'plot_sg_2d_plotly',
    'plot_model_2d_plotly',
    'plot_sg_3d_beam',
    'plot_sg_3d_beam_plotly',
    'plot_matrix',
    'plot_matrix_bar3d',
    'plot_model_matrix',
]
