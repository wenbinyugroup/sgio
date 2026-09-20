"""Visualize the example Structure Gene through sgio's high-level PyVista API.

The public ``sgio.plot_sg_pyvista`` interface reads the Structure Gene, draws
the mesh and sampled element-local axes, and writes a PNG screenshot. ``run.py``
independently writes the full VTM local-axis scene for ParaView.

Install the PyVista dependency before running::

    uv sync --extra pyvista
    uv run python examples/export_sg_mesh_to_vtu/plot.py
"""

from __future__ import annotations

from pathlib import Path

import sgio


EXAMPLE_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXAMPLE_DIR.parent / "preview_sg_mesh" / "sg21t_tri3.sg"
OUTPUT_PNG = EXAMPLE_DIR / "pyvista.png"


def main() -> None:
    """Create the requested PyVista scene and PNG output."""
    sg = sgio.read(
        str(INPUT_FILE),
        file_format="vabs",
        format_version="4",
        sgdim=2,
        model_type="BM2",
    )
    plotter = sgio.plot_sg_pyvista(
        sg,
        show_local_axes=True,
    )
    plotter.off_screen = True
    plotter.show(screenshot=str(OUTPUT_PNG), auto_close=False)
    plotter.close()
    print(f"Wrote PyVista screenshot: {OUTPUT_PNG.resolve()}")


if __name__ == "__main__":
    main()
