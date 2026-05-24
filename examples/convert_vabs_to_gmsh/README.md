# Convert VABS To Gmsh Bundle

## Problem description

This example exports a VABS cross-section file as a standards-compliant
SG-on-Gmsh bundle.

## Explaination of the solution

The script reads `cs_box_t_vabs41.sg`, writes the mesh-bound file `main.msh`,
and then writes:

- `sections.json`
- `config.json`

with the helper in `examples/_bundle_helpers.py`.

This follows the new rule that:

- `main.msh` contains mesh-bound SG data
- section/material payloads are externalized to `sections.json`
- analysis settings are externalized to `config.json`

No legacy `$SGLayerDef` or `$SGConfig` blocks are used.

## Result

After running the script, you get a SG-on-Gmsh bundle in the example
directory.

Run it with:

```bash
uv run python examples/convert_vabs_to_gmsh/run.py
```

## List of all files

- `run.py`
- `cs_box_t_vabs41.sg`
- `main.msh`
- `sections.json`
- `config.json`
- `_bundle_helpers.py`
- `cs_box_t_vabs41.msh` (legacy snapshot kept in the directory, not the new canonical output)
