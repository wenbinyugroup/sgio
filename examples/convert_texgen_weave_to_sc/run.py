"""Convert a TexGen plain weave to SwiftComp and export an interactive view."""

from __future__ import annotations

import os
from pathlib import Path

import sgio


EXAMPLE_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXAMPLE_DIR / "plain_weave_3d.inp"
MANIFEST_FILE = EXAMPLE_DIR / "plain_weave_3d.sg.json"
OUTPUT_FILE = EXAMPLE_DIR / "plain_weave_3d_sc21.sg"
OUTPUT_HTML = EXAMPLE_DIR / "pyvista.html"


def main() -> None:
    """Convert the TexGen model and save an interactive PyVista HTML view."""
    # Method 1: pass the SG parameters as arguments.
    sgio.convert(
        file_name_in=os.fspath(INPUT_FILE),
        file_name_out=os.fspath(OUTPUT_FILE),
        file_format_in="abaqus",
        file_format_out="sc",
        sgdim=3,
        file_version_out="2.1",
        model_type="SD1",
    )
    api_output = OUTPUT_FILE.read_text()

    # Method 2: read the same SG parameters from the SG manifest, which
    # references plain_weave_3d.inp.
    sg = sgio.convert(
        file_name_in=os.fspath(MANIFEST_FILE),
        file_name_out=os.fspath(OUTPUT_FILE),
        file_format_in="sg_manifest",
        file_format_out="sc",
        file_version_out="2.1",
    )

    # Both methods write the same SwiftComp input.
    assert OUTPUT_FILE.read_text() == api_output

    plotter = sgio.plot_sg_pyvista(
        sg,
        show_local_axes=True,
        local_axis_scale=0.15,
        opacity=0.45,
        output_html=OUTPUT_HTML,
    )
    plotter.close()

    print(f"Wrote SwiftComp SG: {OUTPUT_FILE}")
    print(f"Wrote interactive PyVista view: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
