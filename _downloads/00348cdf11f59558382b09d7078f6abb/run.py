"""Read a TexGen plain weave once and write SwiftComp SGs for two macro models."""

from __future__ import annotations

import os
from pathlib import Path

import sgio


EXAMPLE_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXAMPLE_DIR / "plain_weave_3d.inp"
OUTPUT_FILE_SD = EXAMPLE_DIR / "plain_weave_3d_sc21_sd.sg"
OUTPUT_FILE_PL = EXAMPLE_DIR / "plain_weave_3d_sc21_pl.sg"


def main() -> None:

    # Read the TexGen model once; the macro model is given per write below
    sg = sgio.read(
        filename=os.fspath(INPUT_FILE),
        file_format="abaqus",
        sgdim=3,
    )
    sg.analysis_config.physics = 1  # Thermoelastic analysis

    # Write one SG per macro model. sg.omega is None, so each write computes
    # omega from the mesh bounding box for its own model: the SG volume for
    # SD1, the in-plane (y1, y2) area for PL1.
    for model_type, output_file in (("SD1", OUTPUT_FILE_SD), ("PL1", OUTPUT_FILE_PL)):
        sgio.write(
            sg=sg,
            filename=os.fspath(output_file),
            file_format="sc",
            format_version="2.1",  # SwiftComp 2.1
            model_type=model_type,
        )
        print(f"Wrote SwiftComp SG ({model_type}): {output_file}")


if __name__ == "__main__":
    main()
