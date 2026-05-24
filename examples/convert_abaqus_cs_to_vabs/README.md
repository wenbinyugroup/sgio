# Convert Abaqus Cross-Section To VABS

## Problem description

This example starts from an Abaqus cross-section mesh in `sg2_airfoil.inp` and
converts it to a VABS input file. It also exports the converted section as a
SG-on-Gmsh bundle using the new `main.msh + sections.json + config.json`
contract.

## Explaination of the solution

The script does two things:

1. Read the Abaqus model and convert it to `sg2_airfoil.sg`.
2. Reuse the returned `StructureGene` to write a standards-compliant Gmsh
   bundle:
   - `main.msh`
   - `sections.json`
   - `config.json`

The Gmsh export does not rely on legacy `$SGLayerDef` or `$SGConfig` blocks.
Section/material payloads are written to sidecars instead.

## Result

After running the script, you get:

- `sg2_airfoil.sg` as the VABS input
- `main.msh` as the mesh-bound SG-on-Gmsh file
- `sections.json` as the section/material sidecar
- `config.json` as the analysis-config sidecar

Run it with:

```bash
uv run python examples/convert_abaqus_cs_to_vabs/run.py
```

## List of all files

- `run.py`
- `sg2_airfoil.inp`
- `sg2_airfoil.sg`
- `main.msh`
- `sections.json`
- `config.json`
- `sg2_airfoil.sg.ech`
- `sg2_airfoil.sg.K`
- `sg2_airfoil.sg.K.ech`
- `sg2_airfoil.sg.opt`
- `sg2_airfoil.sg.v0`
- `sg2_airfoil.sg.v1S`
- `sg2_airfoil.sg.v22`
- `sg2_airfoil.msh` (legacy snapshot kept in the directory, not the new canonical output)
