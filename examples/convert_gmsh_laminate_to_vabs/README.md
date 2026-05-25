# Convert Gmsh Laminate Bundle To VABS

## Problem description

This example starts from an external Gmsh section mesh of a thin composite ply
and converts it to a VABS input file using the SG-on-Gmsh bundle convention.

It is the orthotropic counterpart of [`convert_gmsh_to_vabs`](../convert_gmsh_to_vabs/):
the existing example only carries one isotropic material, so its mesh needs
neither a per-element local coordinate system nor a fiber rotation field. A
real composite layer needs both:

- `element_local_csys` — the local material frame on each element, used by
  VABS to compute the per-element `theta_1` (layer plane angle).
- `additional_rotation_2` — a per-element scalar that, for a Gmsh section in
  the `xy` plane, maps to the layer-level VABS `theta_3` (fiber direction
  angle).

## Explaination of the solution

The example uses:

- `laminate_simple.msh` — a single curved ply meshed in the Gmsh `xy` plane.
  The mesh carries:
  - `$ElementData "element_local_csys"`: the per-element material frame.
  - `$ElementData "additional_rotation_2"`: 30° fiber rotation on every
    element.
- `sections.json` — one orthotropic carbon-fiber material `mat_1`, bound to the
  ply physical group by its `label` / `id`.
- `config.json` — Euler-Bernoulli homogenization setup (`model = 1`).

`run.py` reads the complete bundle with `sgio.read_sg_from_gmsh_bundle(...)`
and then writes the assembled `StructureGene` to VABS format with
`model_space='xy'`. The writer:

1. Projects nodes from the Gmsh `xy` plane onto the VABS `yz` plane
   (`gmsh_x → x2`, `gmsh_y → x3`, VABS `x1 = 0`).
2. Picks `additional_rotation_2` from `cell_data` as the per-layer
   `theta_3` (the mapping depends on `model_space`: `xy → rotation_2`,
   `yz → rotation_3`, `zx → rotation_1`). All elements that share one
   `property_id` must carry the same rotation value, since VABS allows only
   one `theta_3` per layer.
3. Translates `element_local_csys` into the per-element `theta_1` column of
   the VABS property block.

## Result

After running the script, you get `laminate_simple.sg` ready for VABS. The
single layer in the VABS file points at material `mat_1` with `theta_3 = 30°`.

Run it with:

```bash
uv run python examples/convert_gmsh_laminate_to_vabs/run.py
```

## List of all files

- `run.py`
- `laminate_simple.msh`
- `laminate_simple.sg`
- `sections.json`
- `config.json`
