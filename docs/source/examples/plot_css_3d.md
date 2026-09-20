# Plot Blade Cross-Sections in 3D

## Problem Description

A blade is described by a layout CSV listing `(spanwise_location, section_name)`
pairs, with each section stored as a Gmsh mesh (`.msh`). We want a static 3D
view of all section meshes positioned along the span.

## Solution

First, `run.py` uses {func}`sgio.merge_sections_from_csv` to create
`blade_merged.msh`. Then `run_plot_3d.py` reads the merged mesh and renders it
off-screen with PyVista.

```{literalinclude} ../../../examples/plot_css/run.py
:language: python
```

```{literalinclude} ../../../examples/plot_css/run_plot_3d.py
:language: python
```

## Result

`blade_3d.png` shows every cross-section placed at its spanwise station.

```bash
uv run python examples/plot_css/run.py
uv run python examples/plot_css/run_plot_3d.py
```

```{figure} ../../../examples/plot_css/blade_3d.png
:align: center
:width: 90%
```

## File List

- [run_plot_3d.py](../../../examples/plot_css/run_plot_3d.py): Main Python script
- [blade.csv](../../../examples/plot_css/blade.csv): Blade cross-section layout file
- [blade_3d.png](../../../examples/plot_css/blade_3d.png): Generated PyVista screenshot
- `cs/`: Directory of per-section VABS inputs and results
