# Load Cauchy Material from JSON

## Problem description

This example shows how to load a `CauchyContinuumModel` from the standard
material/section JSON schema and write it back without falling back to the old
flat `model_dump()` layout.

## Explaination of the solution

The canonical input is `sections.json`. It stores one material record using the
grouped schema:

- top-level identity and metadata such as `name`, `model`, `label`
- grouped elastic constants under `elastic`
- grouped strength constants under `strength`
- semantic failure-criterion tokens such as `tsai-wu`

`run.py` reads that record through `sgio.read_material_from_json(...)`, builds
one `CauchyContinuumModel`, and writes it back with
`sgio.write_material_to_json(...)`.

`material.json` is kept in the directory only as a legacy flat snapshot. It is
not the canonical example input anymore.

## Result

After running the script, you get `material_out.json` written with the same
standard grouped schema as the input.

Run it with:

```bash
uv run python examples/load_cauchy_material_from_json/run.py
```

## List of all files

- `run.py`
- `sections.json`
- `material_out.json`
- `material.json` (legacy flat snapshot, not the canonical input)
