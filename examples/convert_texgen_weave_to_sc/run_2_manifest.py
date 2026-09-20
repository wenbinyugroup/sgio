"""Method 2: convert a TexGen plain weave through its SG manifest."""

from __future__ import annotations

import os
from pathlib import Path

import sgio


EXAMPLE_DIR = Path(__file__).resolve().parent
MANIFEST_FILE = EXAMPLE_DIR / "plain_weave_3d.sg.json"
OUTPUT_FILE = EXAMPLE_DIR / "plain_weave_3d_sc21.sg"
OUTPUT_PNG = EXAMPLE_DIR / "pyvista.png"


def main() -> None:
    """Convert the TexGen model and save a PyVista PNG view."""
    # plain_weave_3d.sg.json references plain_weave_3d.inp and holds sgdim and
    # model type, so the conversion takes no SG arguments. It writes the same
    # SwiftComp input as run_1_api.py.
    sg = sgio.convert(
        file_name_in=os.fspath(MANIFEST_FILE),
        file_name_out=os.fspath(OUTPUT_FILE),
        file_format_in="sg_manifest",
        file_format_out="sc",
        file_version_out="2.1",
    )

    plotter = sgio.plot_sg_pyvista(
        sg,
        show_local_axes=True,
        local_axis_scale=0.15,
        opacity=0.45,
    )
    plotter.off_screen = True
    plotter.show(screenshot=str(OUTPUT_PNG), auto_close=False)
    plotter.close()

    print(f"Wrote SwiftComp SG: {OUTPUT_FILE}")
    print(f"Wrote PyVista screenshot: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
