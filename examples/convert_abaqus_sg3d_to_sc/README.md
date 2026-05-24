# Convert Abaqus 3D SG To SwiftComp

## Problem description

This example starts from a 3D Abaqus mesh in `sg33_cube.inp` and converts it to
a SwiftComp input file.

## Explaination of the solution

The script uses `sgio.convert(...)` directly:

- input format: `abaqus`
- output format: `sc`
- SG dimension: `3`
- model type: `SD1`
- SwiftComp format version: `2.1`

This example does not produce a Gmsh bundle because the target is the solver
input itself, not SG-on-Gmsh exchange.

## Result

After running the script, you get `sg33_cube_sc21.sg`.

Run it with:

```bash
uv run python examples/convert_abaqus_sg3d_to_sc/run.py
```

## List of all files

- `run.py`
- `sg33_cube.inp`
- `sg33_cube_sc21.sg`
- `sg33_cube_sc21.sg.ech`
- `sg33_cube_sc21.sg.k`
- `sg33_cube_sc21.sg.opt`
