# Convert a TexGen Weave to SwiftComp

## Problem Description

TexGen writes a textile model as an Abaqus input deck: a voxel mesh, one
element set per yarn, and a per-element fiber orientation kept in a separate
`.ori` file. Convert that deck into a SwiftComp Structure Gene for 3D solid
homogenization.

The committed `32 x 32 x 8` voxel model contains 8,192 C3D8R elements. TexGen
also places six periodic-constraint driver nodes in the deck, which are not
analysis elements.

## Solution

The `.inp` states neither the SG dimension nor the model type, so there are
two ways to supply them, one script each; both write the same file.

### Method 1: API arguments

`sgdim=3, model_type='SD1'` with `file_format_in='abaqus'`.

```{literalinclude} ../../../examples/convert_texgen_weave_to_sc/run_1_api.py
:language: python
```

### Method 2: SG manifest

`plain_weave_3d.sg.json` references the same `.inp` and holds those parameters,
so the conversion needs no SG arguments. See {doc}`/ref/sg_manifest`.

```{literalinclude} ../../../examples/convert_texgen_weave_to_sc/plain_weave_3d.sg.json
:language: json
```

```{literalinclude} ../../../examples/convert_texgen_weave_to_sc/run_2_manifest.py
:language: python
```

Three things the deck carries are read without extra arguments:

- the fiber orientations, which live in `plain_weave_3d.ori` and are reached
  through the `*Distribution, Input=` parameter, resolved relative to the
  `.inp` file's folder;
- the `*Expansion` thermal expansion data of both materials;
- `omega`, which is not in the deck at all — it is computed from the SG
  bounding box, a volume here because a 3D SG shares all three dimensions with
  the `SD1` model. See the omega table in {doc}`/ref/formats`; pass
  `--omega` (or `omega=` in Python) to give it by hand.

{func}`sgio.plot_sg_pyvista` then renders the converted SG, overlaying each
element's local axes so the yarn directions can be inspected.

## Thermoelastic Variant

Because the deck defines `*Expansion`, the same model converts for a
thermoelastic analysis by selecting the physics — no other change:

```bash
sgio convert plain_weave_3d.inp plain_weave_3d.sg -ff abaqus -tf sc -d 3 -m SD1 -p thermoelastic
```

The materials then carry their CTE into the SwiftComp input. See
{doc}`/guide/convert`.

## Result

`plain_weave_3d_sc21.sg` is written and ready for homogenization, alongside
`pyvista.html`. Open the HTML file in a browser to inspect the matrix and yarn
regions with their local coordinate axes.

Running the example needs the optional visualization dependency:

```bash
uv sync --extra pyvista-html
uv run python examples/convert_texgen_weave_to_sc/run_1_api.py
uv run python examples/convert_texgen_weave_to_sc/run_2_manifest.py
```

## File List

- [run_1_api.py](../../../examples/convert_texgen_weave_to_sc/run_1_api.py): conversion with SG arguments, plus rendering
- [run_2_manifest.py](../../../examples/convert_texgen_weave_to_sc/run_2_manifest.py): the same conversion through the SG manifest
- [plain_weave_3d.inp](../../../examples/convert_texgen_weave_to_sc/plain_weave_3d.inp): TexGen Abaqus voxel model
- [plain_weave_3d.ori](../../../examples/convert_texgen_weave_to_sc/plain_weave_3d.ori): per-element orientation distribution
- [plain_weave_3d.sg.json](../../../examples/convert_texgen_weave_to_sc/plain_weave_3d.sg.json): SG manifest referencing the deck
- [plain_weave_3d_sc21.sg](../../../examples/convert_texgen_weave_to_sc/plain_weave_3d_sc21.sg): generated SwiftComp 2.1 Structure Gene
