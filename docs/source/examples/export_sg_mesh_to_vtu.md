# Export an SG Mesh to VTU

## Problem description

An SG mesh often needs to be inspected in ParaView or exchanged with another
VTK-based tool. The output must retain mesh geometry, connectivity, and the
node and element arrays needed to color or filter the mesh.

## Explaination of the solution

`run.py` reads an existing VABS Structure Gene and writes its mesh through
{func}`sgio.write` with `file_format="vtu"`. It also writes a VTM scene whose
`mesh`, `local_y1`, `local_y2`, and `local_y3` blocks contain the full mesh and
explicit local-axis glyph geometry for ParaView.

```{literalinclude} ../../../examples/export_sg_mesh_to_vtu/run.py
:language: python
```

Run the example:

```powershell
uv run python examples/export_sg_mesh_to_vtu/run.py
```

The VTK/VTU adapter is a **mesh-only writer**: it preserves points, cell
topology, `point_data`, and `cell_data`, including multicomponent local-axis
arrays. It deliberately rejects element-nodal fields and point/cell sets
because those containers have no lossless VTK/VTU mapping in this interface.
It does not implement `sgio.read(..., file_format="vtu")`.

Use the separate `plot.py` example to read the Structure Gene through the
high-level {func}`sgio.plot_sg_pyvista` interface and produce a browser scene.
The VTM written by `run.py` remains complete for ParaView; the browser scene
samples local-axis glyphs for responsive rendering.

```powershell
uv run python examples/export_sg_mesh_to_vtu/plot.py
```

For a desktop inspection window, run `plot_desktop.py`. Its checkboxes toggle
the local axes, faces, edges, and nodes independently. Desktop widgets require
a live PyVista window, so they are deliberately separate from the HTML export.

```powershell
uv run python examples/export_sg_mesh_to_vtu/plot_desktop.py
```

## Result

The script creates `sg21t_tri3.vtu` and `sg21t_tri3_local_axes.vtm`. Open the
VTM in ParaView to inspect the complete local-axis arrows, or open
`pyvista.html` after running `plot.py` for sampled browser rendering. Run
`plot_desktop.py` for the desktop visibility controls.

## List of all files

- [run.py](../../../examples/export_sg_mesh_to_vtu/run.py): VTU/VTM export script.
- [plot.py](../../../examples/export_sg_mesh_to_vtu/plot.py): High-level PyVista HTML plot.
- [plot_desktop.py](../../../examples/export_sg_mesh_to_vtu/plot_desktop.py):
  High-level PyVista desktop plot with visibility controls.
- [sg21t_tri3.sg](../../../examples/preview_sg_mesh/sg21t_tri3.sg): Existing VABS input.
- `sg21t_tri3.vtu`: Generated VTU mesh.
- `sg21t_tri3_local_axes.vtm`: Generated complete local-axis scene.
- `pyvista.html`: Generated sampled browser scene.
