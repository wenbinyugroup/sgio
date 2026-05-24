# Convert Gmsh Bundle To VABS

## Problem description

This example starts from an external Gmsh section mesh and converts it to a
VABS input file using the new SG-on-Gmsh bundle convention.

## Explaination of the solution

The example uses:

- `sg21_box_quad4_min_gmsh41.msh`
- `sections.json`
- `config.json`

`run.py` reads the complete bundle with `sgio.read_sg_from_gmsh_bundle(...)`
and then writes the assembled `StructureGene` to VABS format.

This is the recommended path for external CAD + Gmsh workflows because it keeps
the mesh, section payloads, and analysis config clearly separated.

## Result

After running the script, you get `sg21_box_quad4_min_gmsh41.sg`.

Run it with:

```bash
uv run python examples/convert_gmsh_to_vabs/run.py
```

## List of all files

- `run.py`
- `sg21_box_quad4_min_gmsh41.msh`
- `sg21_box_quad4_min_gmsh41.sg`
- `sg21_box_quad4_min_gmsh41.sg.ech`
- `sg21_box_quad4_min_gmsh41.sg.K`
- `sg21_box_quad4_min_gmsh41.sg.opt`
- `sg21_box_quad4_min_gmsh41.sg.v0`
- `sections.json`
- `config.json`
