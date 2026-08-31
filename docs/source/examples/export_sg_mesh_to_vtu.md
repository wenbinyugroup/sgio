# Export an SG Mesh to VTU

## Problem description

An SG mesh often needs to be inspected in ParaView or exchanged with another
VTK-based tool. The output must retain mesh geometry, connectivity, and the
node and element arrays needed to color or filter the mesh.

## Explaination of the solution

`run.py` reads an existing VABS Structure Gene and writes its mesh through
{func}`sgio.write` with `file_format="vtu"`.

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

## Result

The script creates `sg21t_tri3.vtu`. Open it in ParaView, or use
`pyvista.read("sg21t_tri3.vtu")` in a PyVista-enabled environment. Select
`property_id`, `element_id`, or another saved field in the viewer to inspect
the mesh.

## List of all files

- [run.py](../../../examples/export_sg_mesh_to_vtu/run.py): VTU export script.
- [sg21t_tri3.sg](../../../examples/preview_sg_mesh/sg21t_tri3.sg): Existing VABS input.
- `sg21t_tri3.vtu`: Generated VTU mesh.
