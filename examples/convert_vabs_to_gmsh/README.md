# Convert VABS To Gmsh

## Problem description

This example exports a VABS cross-section file as a Gmsh mesh together with the
SG manifest that makes it a complete structure gene.

## Explaination of the solution

The script reads `cs_box_t_vabs41.sg` and writes it with
`sgio.write(..., 'sg_manifest', model_file='main.msh', model_file_format='gmsh')`,
which produces:

- `main.msh` — mesh-bound SG data (nodes, elements, physical groups,
  element-wise fields)
- `main.sg.json` — the SG manifest: `sgdim`, model type, model space, analysis
  configuration, materials, and the sections binding physical groups to
  materials and layup angles

No legacy `$SGLayerDef` or `$SGConfig` blocks are used.

## Result

After running the script, `main.sg.json` and `main.msh` are in the example
directory. `sgio.read('main.sg.json', 'sg_manifest')` reads them back.

Run it with:

```bash
uv run python examples/convert_vabs_to_gmsh/run.py
```

## List of all files

- `run.py`
- `cs_box_t_vabs41.sg`
- `main.msh`
- `main.sg.json`
- `cs_box_t_vabs41.msh` (legacy snapshot kept in the directory, not the canonical output)
