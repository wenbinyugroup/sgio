"""Render merged blade cross-sections to a PNG image with PyVista.

Run ``run.py`` first to merge the section meshes into ``blade_merged.msh``.
This script reads that mesh and creates an off-screen PyVista screenshot.
"""
from __future__ import annotations

from pathlib import Path

import meshio
import pyvista as pv


EXAMPLE_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXAMPLE_DIR / "blade_merged.msh"
OUTPUT_PNG = EXAMPLE_DIR / "blade_3d.png"


def main() -> None:
    """Read the merged mesh and save a PyVista PNG screenshot."""
    mesh = meshio.read(INPUT_FILE)
    grid = pv.from_meshio(mesh)
    grid.clear_data()
    surface = grid.extract_surface(algorithm="dataset_surface")
    boundaries = surface.extract_feature_edges(
        boundary_edges=True,
        feature_edges=False,
        manifold_edges=False,
        non_manifold_edges=False,
    )

    plotter = pv.Plotter(off_screen=True, window_size=(1600, 900))
    plotter.set_background("#f2f4f7")
    plotter.add_mesh(
        surface,
        show_edges=False,
        color="#4c78a8",
        opacity=0.45,
        lighting=False,
    )
    plotter.add_mesh(boundaries, color="#17365d", line_width=3)
    plotter.add_axes()
    plotter.view_isometric()
    plotter.camera.zoom(1.5)
    plotter.show(screenshot=str(OUTPUT_PNG), auto_close=False)
    plotter.close()
    print(f"Wrote PyVista screenshot: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
