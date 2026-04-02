# Read a VABS Input File

## Problem Description

Given a VABS cross-section input file, read it into a structure gene object to inspect mesh statistics and material assignments before running analysis.

## Solution

```{literalinclude} ../../../examples/read_vabs_input/read_vabs_input.py
:language: python
```

`file_format='vabs'` selects the VABS reader. `model_type='BM1'` tells SGIO to interpret the file as an Euler-Bernoulli cross-section. Use `'BM2'` for Timoshenko.

## Result

The script prints the node count, element count, material count, and the full structure gene object to the console.

## File List

- [read_vabs_input.py](../../../examples/read_vabs_input/read_vabs_input.py): Main Python script
- [sg21eb_tri3_vabs40.sg](../../../examples/read_vabs_input/sg21eb_tri3_vabs40.sg): VABS 4.0 cross-section input file
