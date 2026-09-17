# Convert Abaqus Cross-Section to VABS

## Problem Description

Given a 2D beam cross-section mesh created in Abaqus (`.inp` format), convert it to a VABS input file for beam property homogenization using the Timoshenko beam model.

## Solution

The `.inp` file does not state the SG parameters `sgdim`, `model_type` and
`model_space`. The script supplies them in two equivalent ways and asserts that
both write the same VABS input:

1. as arguments of {func}`sgio.convert`;
2. from the SG manifest `sg2_airfoil.sg.json` (see {doc}`/ref/sg_manifest`),
   which references the `.inp` file:

```{literalinclude} ../../../examples/convert_abaqus_cs_to_vabs/sg2_airfoil.sg.json
:language: json
```

```{literalinclude} ../../../examples/convert_abaqus_cs_to_vabs/run.py
:language: python
```

`model_type='BM2'` selects the Timoshenko beam model (includes shear deformation). Use `'BM1'` for the classical Euler-Bernoulli model.

The script also writes the section as a Gmsh mesh `main.msh` with its manifest
`main.sg.json`.

## Result

A VABS input file `sg2_airfoil.sg` is written to the example directory and can be passed directly to VABS for homogenization.

To inspect the Abaqus mesh and its per-element material directions before
homogenization, see {doc}`plot_abaqus_local_csys`.

## File List

- [run.py](../../../examples/convert_abaqus_cs_to_vabs/run.py): Main Python script
- [sg2_airfoil.inp](../../../examples/convert_abaqus_cs_to_vabs/sg2_airfoil.inp): Abaqus cross-section input file
- [sg2_airfoil.sg.json](../../../examples/convert_abaqus_cs_to_vabs/sg2_airfoil.sg.json): SG manifest for the Abaqus input
