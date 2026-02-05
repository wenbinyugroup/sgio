# Load Cauchy Material from JSON

This example shows how to instantiate the renamed `CauchyContinuumModel`
class directly from serialized JSON data.

## Files

- `material.json` — Sample orthotropic material definition
- `run.py` — Script that loads the JSON payload and builds the model

## Usage

```bash
uv run python examples/load_cauchy_material_from_json/run.py
```

The script will:

1. Deserialize the JSON file into a Python dictionary
2. Build a `CauchyContinuumModel` instance with full validation
3. Print select engineering constants and re-serialize the model

Adapt `material.json` to match your own material database, or replace the
JSON source with data streamed from a service. The `CauchyContinuumModel`
constructor accepts any keyword arguments documented in the API reference.
