# Convert Abaqus Cross-Section To VABS

## Problem description

This example starts from an Abaqus cross-section mesh in `sg2_airfoil.inp` and
converts it to a VABS input file. It also exports the converted section as a
Gmsh mesh with its SG manifest.

## Explaination of the solution

The script does two things:

1. Read the Abaqus model and convert it to `sg2_airfoil.sg`.
2. Reuse the returned `StructureGene` to write `main.msh` and the SG manifest
   `main.sg.json` that references it.

The Gmsh export does not rely on legacy `$SGLayerDef` or `$SGConfig` blocks.
Materials, sections and SG parameters are written to the manifest instead.

## Result

After running the script, you get:

- `sg2_airfoil.sg` as the VABS input
- `main.msh` as the Gmsh model file
- `main.sg.json` as the SG manifest

Run it with:

```bash
uv run python examples/convert_abaqus_cs_to_vabs/run.py
```

## List of all files

- `run.py`
- `sg2_airfoil.inp`
- `sg2_airfoil.sg`
- `main.msh`
- `main.sg.json`
- `sg2_airfoil.sg.ech`
- `sg2_airfoil.sg.K`
- `sg2_airfoil.sg.K.ech`
- `sg2_airfoil.sg.opt`
- `sg2_airfoil.sg.v0`
- `sg2_airfoil.sg.v1S`
- `sg2_airfoil.sg.v22`
- `sg2_airfoil.msh` (legacy snapshot kept in the directory, not the new canonical output)
