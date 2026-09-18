# Convert a TexGen plain weave to SwiftComp solid and plate SGs

## Problem description

One microstructure can serve different macro models. The TexGen plain weave in
`plain_weave_3d.inp` is homogenized both as a 3D solid (`SD1`) and as a
Kirchhoff-Love plate (`PL1`), so it needs two SwiftComp 2.1 `.sg` files.

`sgio.convert(...)` could write each file, but it reads the input deck once
per call. This example reads the deck once and writes both files.

## Explaination of the solution

`run.py` does three things:

1. `sgio.read(...)` reads `plain_weave_3d.inp` with `sgdim=3`. It leaves out
   `model_type`: for an Abaqus deck the macro model can be given at write
   time, so the SG read stays model-neutral.
2. `sg.analysis_config.physics = 1` selects a thermoelastic analysis. The deck
   defines the thermal expansion of both materials.
3. `sgio.write(...)` runs once per macro model, with `model_type="SD1"` and
   `model_type="PL1"`. Each write uses its own model type without changing
   `sg`.

`omega` is not set by hand. While `sg.omega` is `None`, each write computes it
from the SG bounding box over the dimensions the SG shares with its macro
model:

| Model | Shared dimensions | omega |
|---|---|---|
| `SD1` | y1, y2, y3 | volume, 2 x 2 x 0.22 = 0.88 |
| `PL1` | y1, y2 | in-plane area, 2 x 2 = 4.0 |

To set omega by hand, pass `omega=` to `sgio.write(...)`.

Run the example:

```powershell
uv run python examples/convert_texgen_weave_to_sc_sd_pl/run.py
```

## Result

The script writes `plain_weave_3d_sc21_sd.sg` and `plain_weave_3d_sc21_pl.sg`.
Running SwiftComp 2.1 on them gives the `.k` files:

- `SD1`: the 6 x 6 effective stiffness matrix, e.g. C11 = 4.876e10 and
  C33 = 6.196e9.
- `PL1`: the A, B, D plate stiffness, e.g. A11 = 8.923e9, B11 = 8.923e8 and
  D11 = 1.007e8.

SwiftComp computes plate stiffness about the plane y3 = 0. The TexGen mesh
spans z = -0.01 to 0.21, so that plane lies 0.1 below the mid-plane, which is
why B11 = 0.1 x A11. For the stiffness about the mid-plane, shift the node
coordinates in the script before the `PL1` write, e.g.
`sg.mesh.points[:, 2] -= 0.1`.

## List of all files

- `README.md` - this walkthrough.
- `run.py` - reads the deck once and writes the `SD1` and `PL1` SGs.
- `plain_weave_3d.inp` - TexGen Abaqus voxel model.
- `plain_weave_3d.ori` - TexGen per-element orientation distribution.
- `plain_weave_3d_sc21_sd.sg` - generated SwiftComp 2.1 SG for `SD1`.
- `plain_weave_3d_sc21_pl.sg` - generated SwiftComp 2.1 SG for `PL1`.
- `plain_weave_3d_sc21_sd.sg.k` - SwiftComp homogenization result for `SD1`.
- `plain_weave_3d_sc21_pl.sg.k` - SwiftComp homogenization result for `PL1`.
