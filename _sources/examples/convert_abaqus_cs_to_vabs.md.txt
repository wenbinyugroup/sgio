# Convert Abaqus Cross-Section to VABS

## Problem Description

Given a 2D beam cross-section mesh created in Abaqus (`.inp` format), convert it to a VABS input file for beam property homogenization using the Timoshenko beam model.

## Solution

The `.inp` file does not state the SG parameters `sgdim`, `model_type` and
`model_space`. There are two ways to supply them, one script each; both write
the same VABS input.

`model_type='BM2'` selects the Timoshenko beam model (includes shear
deformation). Use `'BM1'` for the classical Euler-Bernoulli model.

### Method 1: API arguments

The SG parameters are arguments of {func}`sgio.convert`.

```{literalinclude} ../../../examples/convert_abaqus_cs_to_vabs/run_1_api.py
:language: python
```

### Method 2: SG manifest

`sg2_airfoil.sg.json` (see {doc}`/ref/sg_manifest`) references the `.inp` file
and holds the same parameters, so the conversion takes no SG arguments:

```{literalinclude} ../../../examples/convert_abaqus_cs_to_vabs/sg2_airfoil.sg.json
:language: json
```

```{literalinclude} ../../../examples/convert_abaqus_cs_to_vabs/run_2_manifest.py
:language: python
```

This script also writes the section as a Gmsh mesh `main.msh` with its manifest
`main.sg.json`. A `.msh` file holds no materials or SG parameters, so a Gmsh
export is always written through a manifest.

## Result

A VABS input file `sg2_airfoil.sg` is written to the example directory and can be passed directly to VABS for homogenization.

To inspect the Abaqus mesh and its per-element material directions before
homogenization, see {doc}`plot_abaqus_local_csys`.

## File List

- [run_1_api.py](../../../examples/convert_abaqus_cs_to_vabs/run_1_api.py): Conversion with SG arguments
- [run_2_manifest.py](../../../examples/convert_abaqus_cs_to_vabs/run_2_manifest.py): Conversion through the SG manifest
- [sg2_airfoil.inp](../../../examples/convert_abaqus_cs_to_vabs/sg2_airfoil.inp): Abaqus cross-section input file
- [sg2_airfoil.sg.json](../../../examples/convert_abaqus_cs_to_vabs/sg2_airfoil.sg.json): SG manifest for the Abaqus input
