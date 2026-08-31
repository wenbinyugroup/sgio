"""Export an existing Structure Gene mesh as a VTU file for ParaView.

The example reads the VABS cross-section shared with ``preview_sg_mesh`` and
writes only its geometry, topology, point data, and cell data to VTU. Open the
resulting file in ParaView or PyVista; sgio does not read VTK/VTU files here.
"""

from __future__ import annotations

from pathlib import Path

import sgio


EXAMPLE_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXAMPLE_DIR.parent / "preview_sg_mesh" / "sg21t_tri3.sg"
OUTPUT_FILE = EXAMPLE_DIR / "sg21t_tri3.vtu"


def main() -> None:
    """Read the bundled VABS Structure Gene and write a VTU mesh export."""
    sg = sgio.read(
        str(INPUT_FILE),
        file_format="vabs",
        format_version="4",
        sgdim=2,
        model_type="BM2",
    )
    sgio.write(sg, str(OUTPUT_FILE), file_format="vtu")
    print(f"Wrote VTU mesh for ParaView/PyVista: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
