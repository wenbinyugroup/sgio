# Plot Blade Cross-Sections in 3D

## Problem Description

A blade is described by a layout CSV listing `(spanwise_location, section_name)`
pairs, with each section stored as a VABS input (`.sg`) plus its homogenization
result (`.sg.K`). We want to view all sections together in 3D, positioned along
the span, and interact with the result smoothly even for dense meshes.

## Solution

{func}`sgio.plot_sg_3d_beam_plotly` reads the layout CSV, loads each section and
its analysis result, and renders them as an interactive plotly figure written to
a standalone HTML file. Open the HTML in a browser to rotate, zoom, and pan.

```{literalinclude} ../../../examples/plot_css/run_plot_3d.py
:language: python
```

Key arguments:

- `csv_file` / `section_dir` — the layout table and where the section files live
- `input_format` / `model_type` — how to read each section (`vabs`, `BM2` here)
- `aspect_mode='data'` — preserve true relative proportions of span vs. chord
- `output_html` — write a self-contained interactive HTML file

{func}`sgio.plot_sg_3d_beam` is the matplotlib equivalent, useful for static
figures; the plotly version is preferable for interactive inspection of large
meshes.

## Result

`blade_3d.html` is written and opened in the default browser, showing every
cross-section placed at its spanwise station.

```bash
uv run python examples/plot_css/run_plot_3d.py
```

## File List

- [run_plot_3d.py](../../../examples/plot_css/run_plot_3d.py): Main Python script
- [blade.csv](../../../examples/plot_css/blade.csv): Blade cross-section layout file
- `cs/`: Directory of per-section VABS inputs and results
