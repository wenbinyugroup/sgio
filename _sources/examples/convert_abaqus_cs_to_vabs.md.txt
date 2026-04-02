# Convert Abaqus Cross-Section to VABS

## Problem Description

Given a 2D beam cross-section mesh created in Abaqus (`.inp` format), convert it to a VABS input file for beam property homogenization using the Timoshenko beam model.

## Solution

SGIO provides two approaches: a one-step `convert()` call, or the explicit `read()` + `write()` pair.

```{literalinclude} ../../../examples/convert_abaqus_cs_to_vabs/run.py
:language: python
```

`model_type='bm2'` selects the Timoshenko beam model (includes shear deformation). Use `'bm1'` for the classical Euler-Bernoulli model.

## Result

A VABS input file `sg2_airfoil_2.sg` is written to the working directory and can be passed directly to VABS for homogenization.

## File List

- [run.py](../../../examples/convert_abaqus_cs_to_vabs/run.py): Main Python script
- [sg2_airfoil.inp](../../../examples/convert_abaqus_cs_to_vabs/sg2_airfoil.inp): Abaqus cross-section input file
