"""Tests for backend-neutral high-level structure-gene plotting entries."""

from __future__ import annotations

import matplotlib
import numpy as np

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sgio.core.mesh import SGMesh
from sgio.core.sg import StructureGene
from sgio.visualization import plot_sg_matplotlib, plot_sg_plotly


def _sample_sg() -> StructureGene:
    """Build a minimal two-dimensional structure gene for plotting tests."""
    sg = StructureGene(name="sample", sgdim=2)
    sg.mesh = SGMesh(
        points=np.array(
            [[0.0, -1.0, -1.0], [0.0, 1.0, -1.0], [0.0, 0.0, 1.0]]
        ),
        cells=[("triangle", np.array([[0, 1, 2]], dtype=int))],
    )
    return sg


def test_plot_sg_matplotlib_creates_axes_for_a_structure_gene():
    """The matplotlib entry point creates and populates axes by default."""
    axes = plot_sg_matplotlib(_sample_sg())
    try:
        assert axes.collections
        assert axes.lines
    finally:
        plt.close(axes.figure)


def test_plot_sg_plotly_returns_figure_and_writes_html(tmp_path):
    """The Plotly entry point renders the SG and can persist its HTML figure."""
    output_html = tmp_path / "section.html"

    figure = plot_sg_plotly(_sample_sg(), output_html=output_html)

    assert len(figure.data) == 2
    assert output_html.is_file()

