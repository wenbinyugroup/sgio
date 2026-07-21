# Convert a Gmsh Laminate Bundle to VABS

## Problem Description

Convert an external Gmsh section mesh of a thin composite ply into a VABS input
file.

This is the orthotropic counterpart of {doc}`convert_gmsh_to_vabs`. That example
carries a single isotropic material, so its mesh needs neither a per-element
local coordinate system nor a fiber rotation. A real composite layer needs both:

- `element_local_csys` — the local material frame on each element, used by VABS
  to compute the per-element `theta_1` (layer plane angle).
- `additional_rotation_2` — a per-element scalar that, for a Gmsh section in the
  `xy` plane, maps to the layer-level VABS `theta_3` (fiber direction angle).

## Solution

The bundle consists of:

- `laminate_simple.msh` — a single curved ply meshed in the Gmsh `xy` plane,
  carrying `$ElementData "element_local_csys"` (the per-element material frame)
  and `$ElementData "additional_rotation_2"` (30° fiber rotation on every
  element).
- `sections.json` — one orthotropic carbon-fiber material `mat_1`, bound to the
  ply physical group by its `label` / `id`.
- `config.json` — Euler-Bernoulli homogenization setup (`model = 1`).

```{literalinclude} ../../../examples/convert_gmsh_laminate_to_vabs/run.py
:language: python
```

{func}`sgio.read_sg_from_gmsh_bundle` reads the bundle, and {func}`sgio.write`
emits VABS input with `model_space='xy'`. The writer then:

1. Projects nodes from the Gmsh `xy` plane onto the VABS `yz` plane
   (`gmsh_x → x2`, `gmsh_y → x3`, VABS `x1 = 0`).
2. Picks `additional_rotation_2` from `cell_data` as the per-layer `theta_3`.
   The mapping depends on `model_space`: `xy → rotation_2`, `yz → rotation_3`,
   `zx → rotation_1`. All elements sharing one `property_id` must carry the same
   rotation value, since VABS allows only one `theta_3` per layer.
3. Translates `element_local_csys` into the per-element `theta_1` column of the
   VABS property block.

## Result

`laminate_simple.sg` is written, ready for VABS. Its single layer points at
material `mat_1` with `theta_3 = 30°`.

```bash
uv run python examples/convert_gmsh_laminate_to_vabs/run.py
```

## File List

- [run.py](../../../examples/convert_gmsh_laminate_to_vabs/run.py): Main Python script
- [laminate_simple.msh](../../../examples/convert_gmsh_laminate_to_vabs/laminate_simple.msh): Gmsh ply mesh with local csys and rotation data
- [sections.json](../../../examples/convert_gmsh_laminate_to_vabs/sections.json): Orthotropic material definition
- [config.json](../../../examples/convert_gmsh_laminate_to_vabs/config.json): Analysis configuration
- [laminate_simple.sg](../../../examples/convert_gmsh_laminate_to_vabs/laminate_simple.sg): Generated VABS input
