# Convert Abaqus 3D SG To SwiftComp

## Problem description

This example starts from a 3D Abaqus mesh in `sg33_cube.inp` and converts it to
a SwiftComp 2.1 input file.

## Explaination of the solution

The `.inp` file does not state the SG dimension (`3`) or the model type
(`SD1`). There are two ways to supply them, one script each. Both write the
same `sg33_cube_sc21.sg`.

**Method 1 — API arguments** (`run_1_api.py`):

```python
sgio.convert(
    'sg33_cube.inp', 'sg33_cube_sc21.sg', 'abaqus', 'sc',
    sgdim=3, model_type='SD1', file_version_out='2.1',
)
```

**Method 2 — SG manifest** (`run_2_manifest.py`): `sg33_cube.sg.json`
references `sg33_cube.inp` and holds the same parameters:

```python
sgio.convert(
    'sg33_cube.sg.json', 'sg33_cube_sc21.sg', 'sg_manifest', 'sc',
    file_version_out='2.1',
)
```

A 3D SG has no `model_space`.

## Result

After running the script, you get `sg33_cube_sc21.sg`.

Run it with:

```bash
uv run python examples/convert_abaqus_sg3d_to_sc/run_1_api.py
uv run python examples/convert_abaqus_sg3d_to_sc/run_2_manifest.py
```

## List of all files

- `run_1_api.py`
- `run_2_manifest.py`
- `sg33_cube.inp`
- `sg33_cube.sg.json`
- `sg33_cube_sc21.sg`
- `sg33_cube_sc21.sg.ech`
- `sg33_cube_sc21.sg.k`
- `sg33_cube_sc21.sg.opt`
