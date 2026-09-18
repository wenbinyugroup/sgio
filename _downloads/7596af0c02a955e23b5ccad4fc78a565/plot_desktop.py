"""Inspect the example Structure Gene with desktop PyVista controls.

This script demonstrates the interactive checkboxes provided by
``sgio.plot_sg_pyvista``.  They control local coordinate axes, faces, edges,
and nodes in a live PyVista window.  They are intentionally separate from the
offline HTML export in ``plot.py``.

Run with::

    uv run python examples/export_sg_mesh_to_vtu/plot_desktop.py
"""

from __future__ import annotations

from pathlib import Path

import sgio


EXAMPLE_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXAMPLE_DIR.parent / "preview_sg_mesh" / "sg21t_tri3.sg"


def main() -> None:
    """Open a desktop PyVista window with high-level visibility controls."""
    sg = sgio.read(
        str(INPUT_FILE),
        file_format="vabs",
        format_version="4",
        sgdim=2,
        model_type="BM2",
    )
    sgio.plot_sg_pyvista(
        sg,
        show_local_axes=True,
        widgets=True,
        show=True,
    )


if __name__ == "__main__":
    main()
