"""Visualize the example Structure Gene through sgio's high-level PyVista API.

The public ``sgio.plot_sg_pyvista`` interface reads the Structure Gene, draws
the mesh and sampled element-local axes, and writes interactive HTML with a
local-axis legend and view controls. ``run.py`` independently writes the full
VTM local-axis scene for ParaView.

Install the HTML-export dependency before running::

    uv sync --extra pyvista-html
    uv run python examples/export_sg_mesh_to_vtu/plot.py
"""

from __future__ import annotations

from pathlib import Path

import sgio


EXAMPLE_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXAMPLE_DIR.parent / "preview_sg_mesh" / "sg21t_tri3.sg"
OUTPUT_HTML = EXAMPLE_DIR / "pyvista.html"


def main() -> None:
    """Create the requested PyVista scene and interactive HTML output."""
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
        output_html=OUTPUT_HTML,
    )
    plotter.close()
    print(f"Wrote interactive PyVista view: {OUTPUT_HTML.resolve()}")


if __name__ == "__main__":
    main()
