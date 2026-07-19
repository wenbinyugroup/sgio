# View Blade Cross-Section Failure Results In ParaView

## Problem description

A blade (or rotor, or any beam-like slender structure) is modelled as a series
of 2D cross-sections distributed along its span. After a VABS failure analysis,
each section has a per-element **failure index** and **strength ratio** written
to a `*.sg.fi` file. We want to inspect these fields as contour plots on *all*
sections of the whole blade at once, interactively — rotating, slicing, and
color-mapping in [ParaView](https://www.paraview.org/).

## Explaination of the solution

sgio reads both the mesh and the failure output, and bridges the mesh to VTK via
PyVista, whose native `.vtm`/`.vtu` files ParaView opens directly. The layout of
sections along the span is given by `blade.csv` (a `location, cs` table).

For every section listed in `blade.csv`, [`run.py`](run.py):

1. reads the Structure Gene mesh with `sgio.read(..., file_format="vabs")`;
2. reads the failure output with
   `sgio.read_output_state(..., analysis="fi", tool_version="4.1")`, which
   returns per-element `failure_index` (`fi`) and `strength_ratio` (`sr`);
3. attaches both as element (cell) data with
   `mesh.add_cell_data_from_dict(...)` (ordered by `cell_data['element_id']`);
4. places the section at its spanwise station by setting the mesh's `x1`
   coordinate (`mesh.points[:, 0] = location`);
5. bridges the mesh to a `pyvista.UnstructuredGrid` with
   `sg.mesh.to_pyvista()`.

All section grids are collected into one `pyvista.MultiBlock` and saved as
`blade_fi.vtm`, so the entire blade is a single ParaView dataset.

Two details worth noting:

- **Failure-output header.** VABS 4.1+ writes a header line above the failure
  table; `tool_version="4.1"` tells the reader to skip it. Without it the parse
  is off by one line and returns `None`.
- **Strength-ratio sentinel.** VABS writes `1.7976931E+308` (the max double) as
  the strength ratio of unloaded elements (infinite margin). The script masks
  these to `NaN` so they do not swamp the color scale; ParaView renders them as
  blank, and you can isolate the rest with a *Threshold* filter.

PyVista is an **optional dependency** (it pulls in `vtk`). Install it with:

```bash
pip install sgio[pyvista]     # or: uv pip install pyvista
```

## Result

Running the script writes `blade_fi.vtm` (plus a `blade_fi/` folder holding one
`.vtu` per section). Open `blade_fi.vtm` in ParaView and color by
`failure_index` or `strength_ratio` to see the field on every section along the
blade axis (`x1`). The other carried-over arrays (`property_id`,
`element_id`, `property_ref_csys`) are available too.

Run it with:

```bash
uv run python examples/view_css_fi_paraview/run.py
```

## List of all files

- `run.py` — the export script
- `blade.csv` — section layout (`location, cs`)
- `blade1/main_cs_*/main_cs_*.sg` — input VABS cross-section meshes
- `blade1/main_cs_*/main_cs_*.sg.fi` — VABS failure output (failure index /
  strength ratio)
- `blade_fi.vtm` (+ `blade_fi/`) — generated ParaView MultiBlock file
