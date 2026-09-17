# Convert Gmsh Mesh To VABS

## Problem description

This example starts from an external Gmsh section mesh and converts it to a
VABS input file.

## Explaination of the solution

The example uses:

- `sg21_box_quad4_min_gmsh41.msh` — the section mesh in the `yz` plane
- `sg21_box_quad4_min_gmsh41.sg.json` — the SG manifest referencing the mesh:
  `sgdim`, `model_type` (`BM1`), `model_space` (`yz`), analysis configuration,
  the `matrix` material, and the section binding the physical group to it

`run.py` reads the manifest with `sgio.read(..., 'sg_manifest')` and writes the
assembled `StructureGene` to VABS format.

This is the recommended path for external CAD + Gmsh workflows: the mesh stays
a plain Gmsh file and the manifest holds everything the mesh cannot.

## Result

After running the script, you get `sg21_box_quad4_min_gmsh41.sg`.

Run it with:

```bash
uv run python examples/convert_gmsh_to_vabs/run.py
```

## List of all files

- `run.py`
- `sg21_box_quad4_min_gmsh41.msh`
- `sg21_box_quad4_min_gmsh41.sg.json`
- `sg21_box_quad4_min_gmsh41.sg`
- `sg21_box_quad4_min_gmsh41.sg.ech`
- `sg21_box_quad4_min_gmsh41.sg.K`
- `sg21_box_quad4_min_gmsh41.sg.opt`
- `sg21_box_quad4_min_gmsh41.sg.v0`
