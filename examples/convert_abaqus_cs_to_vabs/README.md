# Convert Abaqus Cross-Section To VABS

## Problem description

This example starts from an Abaqus cross-section mesh in `sg2_airfoil.inp` and
converts it to a VABS input file. It also exports the converted section as a
Gmsh mesh with its SG manifest.

## Explaination of the solution

The `.inp` file carries the mesh, materials and sections, but not the SG
parameters: `sgdim` (2), `model_type` (`BM2`, Timoshenko) and `model_space`
(`xy`, the plane the section is drawn in). The script supplies them in two
equivalent ways:

1. **API arguments**: `sgio.convert(..., 'abaqus', 'vabs', sgdim=2,
   model_space='xy', model_type='BM2')`.
2. **SG manifest**: `sg2_airfoil.sg.json` references `sg2_airfoil.inp` and holds
   the same parameters, so `sgio.convert('sg2_airfoil.sg.json', ...,
   'sg_manifest', 'vabs')` needs no SG arguments.

The script asserts that both methods write the same `sg2_airfoil.sg`.

It then reuses the returned `StructureGene` to write `main.msh` and the SG
manifest `main.sg.json` that references it. A `.msh` file holds no materials or
SG parameters, so a Gmsh export is always written through a manifest.

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
- `sg2_airfoil.sg.json`
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
