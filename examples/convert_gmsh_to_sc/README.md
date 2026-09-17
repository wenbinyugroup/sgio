# Convert Gmsh Mesh To SwiftComp

## Problem description

This example starts from an external Gmsh mesh and converts it to a SwiftComp
input file.

## Explaination of the solution

A `.msh` file carries only the mesh, so the example uses an SG manifest:

- `sg33_cube_tetra4_min_gmsh41.msh` — the mesh and its `matrix` physical group
- `sg33_cube_tetra4_min_gmsh41.sg.json` — the SG manifest referencing the mesh:
  `sgdim`, `model_type` (`SD1`), analysis configuration, the `matrix` material,
  and the section binding the physical group to it

`run.py` reads the manifest with `sgio.read(..., 'sg_manifest')` and writes the
result to SwiftComp format.

## Result

After running the script, you get `sg33_cube_tetra4_min_gmsh41.sg`.

Run it with:

```bash
uv run python examples/convert_gmsh_to_sc/run.py
```

## List of all files

- `run.py`
- `sg33_cube_tetra4_min_gmsh41.msh`
- `sg33_cube_tetra4_min_gmsh41.sg.json`
- `sg33_cube_tetra4_min_gmsh41.sg`
