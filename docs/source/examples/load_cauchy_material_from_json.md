# Load Cauchy Continuum Material from JSON

## Problem Description

Given a JSON file containing orthotropic material constants (elastic moduli, Poisson's ratios, shear moduli, etc.), instantiate a `CauchyContinuumModel` object for use in downstream analysis or serialization.

## Solution

```{literalinclude} ../../../examples/load_cauchy_material_from_json/run.py
:language: python
```

`CauchyContinuumModel(**payload)` validates the JSON payload against the model's field definitions. Call `model_dump_json()` to round-trip back to JSON.

## Result

The script prints the loaded material properties and a pretty-printed JSON serialization to the console. No output file is written.

## File List

- [run.py](../../../examples/load_cauchy_material_from_json/run.py): Main Python script
- [material.json](../../../examples/load_cauchy_material_from_json/material.json): Orthotropic carbon/epoxy material definition
