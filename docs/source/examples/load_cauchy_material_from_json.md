# Load Cauchy Continuum Material from JSON

## Problem Description

Given a JSON file containing orthotropic material constants (elastic moduli, Poisson's ratios, shear moduli, etc.), instantiate a `CauchyContinuumModel` object for use in downstream analysis or serialization.

## Solution

```{literalinclude} ../../../examples/load_cauchy_material_from_json/run.py
:language: python
```

{func}`sgio.read_material_from_json` parses one standard JSON material record
and validates it against the model's field definitions, returning a mapping of
material name to model object. `write_material_to_json` performs the reverse
round-trip.

## Result

The script prints the loaded material, selected engineering constants (`e1`,
`g12`, `nu12`), and the re-serialized JSON. It also writes `material_out.json`
next to the script.

## File List

- [run.py](../../../examples/load_cauchy_material_from_json/run.py): Main Python script
- [sections.json](../../../examples/load_cauchy_material_from_json/sections.json): Orthotropic carbon/epoxy material definition
