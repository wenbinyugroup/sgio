"""Export an Abaqus cross-section and its local axes as interactive HTML.

The script reads ``sg2_airfoil.inp`` and uses sgio's PyVista scene factory to
render the mesh with sampled element local coordinate systems. The exported
HTML can be opened in a browser for interactive inspection.

Install the HTML-export extra before running it::

    uv sync --extra pyvista-html
"""
from __future__ import annotations

import argparse
from pathlib import Path

import sgio


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the local-axis HTML export."""
    example_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=example_dir / "sg2_airfoil.inp",
        help="Abaqus .inp cross-section to read (default: bundled airfoil).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=example_dir / "sg2_airfoil_local_csys.html",
        help="Destination interactive HTML file.",
    )
    parser.add_argument(
        "--max-axes",
        type=int,
        default=500,
        help="Maximum number of cells whose local axes are rendered.",
    )
    parser.add_argument(
        "--axis-scale",
        type=float,
        default=None,
        help="Arrow length in mesh units (default: 2.5%% of bounds diagonal).",
    )
    return parser.parse_args()


def main() -> None:
    """Read the requested Abaqus section and export its interactive plot."""
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(f"Abaqus input file does not exist: {args.input}")

    sg = sgio.read(
        str(args.input),
        file_format="abaqus",
        sgdim=2,
        model_type="BM2",
    )
    plotter = sgio.create_pyvista_plotter(
        sg.mesh,
        scalars="property_id",
        show_local_axes=True,
        max_local_axes=args.max_axes,
        local_axis_scale=args.axis_scale,
    )
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        plotter.export_html(str(args.output))
    finally:
        plotter.close()
    print(f"Wrote interactive local-coordinate view: {args.output.resolve()}")


if __name__ == "__main__":
    main()
