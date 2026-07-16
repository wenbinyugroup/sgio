# Preview A Structure Gene Mesh With PyVista

## Problem description

Once a Structure Gene (SG) is read into sgio, it is useful to *see* the mesh —
the geometry, the cell blocks, and per-element data such as `property_id` —
before running an analysis. This example reads a VABS cross-section and renders
its mesh with [PyVista](https://pyvista.org/).

## Explaination of the solution

`SGMesh` is a backend-neutral mesh container. sgio provides a bridge to PyVista
so any SG mesh can be handed to VTK's renderer:

1. Read the cross-section into a `StructureGene` with `sgio.read`.
2. Call `sg.mesh.to_pyvista()` to get a `pyvista.UnstructuredGrid`. Geometry,
   `point_data`, and `cell_data` (e.g. `property_id`) cross the bridge.
3. Render it — here a headless screenshot; drop `off_screen` / `screenshot`
   for an interactive window.
4. `SGMesh.from_pyvista(grid)` shows the reverse bridge (grid back to `SGMesh`).

PyVista is an **optional dependency** (it pulls in `vtk`). The core sgio IR
does not require it; `to_pyvista` imports PyVista lazily and only fails if you
call it without PyVista installed. Install it with:

```bash
pip install sgio[pyvista]     # or: uv pip install pyvista
```

## Result

Running the script prints the grid summary and the reverse-bridge cell blocks,
and writes `preview.png` — the airfoil cross-section colored by `property_id`
with mesh edges shown. The 2D section lies in the Y-Z plane, so the camera looks
down the X axis (`cpos="yz"`).

Run it with:

```bash
uv run python examples/preview_sg_mesh/run.py
```

## List of all files

- `run.py`
- `sg21t_tri3.sg` — input VABS cross-section (triangular mesh)
- `preview.png` — generated preview image
