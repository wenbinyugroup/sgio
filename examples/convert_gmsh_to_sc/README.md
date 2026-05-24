# Convert Gmsh Bundle To SwiftComp

## Problem description

This example starts from an external Gmsh mesh and converts it to a SwiftComp
input file using the new SG-on-Gmsh bundle convention.

## Explaination of the solution

The example uses three files together:

- `sg33_cube_tetra4_min_gmsh41.msh`
- `sections.json`
- `config.json`

`run.py` assembles them with `sgio.read_sg_from_gmsh_bundle(...)` and then
writes the result to SwiftComp format.

This replaces the old `materials.json`-only path and matches the current
standard where:

- mesh-bound data stay in `main.msh`
- material/section payloads live in `sections.json`
- analysis configuration lives in `config.json`

## Result

After running the script, you get `sg33_cube_tetra4_min_gmsh41.sg`.

Run it with:

```bash
uv run python examples/convert_gmsh_to_sc/run.py
```

## List of all files

- `run.py`
- `sg33_cube_tetra4_min_gmsh41.msh`
- `sg33_cube_tetra4_min_gmsh41.sg`
- `sections.json`
- `config.json`
