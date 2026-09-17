# Convert a TexGen plain weave to SwiftComp

## Problem description

This example converts TexGen's Abaqus input deck to a SwiftComp Structure Gene
and produces an interactive PyVista HTML view of the converted model.

The committed `32 x 32 x 8` voxel model contains 8,192 C3D8R elements.
TexGen also places six periodic-constraint driver nodes in the Abaqus deck.

## Explaination of the solution

`run.py` uses the current SGIO public APIs:

1. `sgio.convert(...)` reads `plain_weave_3d.inp`, including the external
   orientation distribution in `plain_weave_3d.ori`, and writes a SwiftComp
   2.1 `.sg` file for a three-dimensional Cauchy continuum (`SD1`). The `.inp`
   does not state the SG dimension or model type, so they are supplied in two
   equivalent ways, and the script asserts that both write the same `.sg`:
   - **API arguments**: `sgdim=3, model_type="SD1"` with
     `file_format_in="abaqus"`.
   - **SG manifest**: `plain_weave_3d.sg.json` references `plain_weave_3d.inp`
     and holds the same parameters; convert it with
     `file_format_in="sg_manifest"` and no SG arguments.
2. `sgio.plot_sg_pyvista(...)` constructs a PyVista scene from the converted
   Structure Gene, colors its voxels with 45% opacity, overlays the
   element-local axes, and writes the scene directly to `pyvista.html`.

Install the optional visualization dependency and run the conversion:

```powershell
uv sync --extra pyvista-html
uv run python examples/convert_texgen_weave_to_sc/run.py
```

## Result

The conversion produces `plain_weave_3d_sc21.sg`. Open `pyvista.html` in a web
browser to inspect the matrix and yarn regions together with their local
coordinate axes.

## List of all files

- `README.md` - this walkthrough.
- `plain_weave_3d.inp` - TexGen Abaqus voxel model.
- `plain_weave_3d.ori` - TexGen per-element orientation distribution.
- `plain_weave_3d.sg.json` - SG manifest referencing the TexGen Abaqus model.
- `run.py` - SGIO conversion and PyVista rendering script.
- `plain_weave_3d_sc21.sg` - generated SwiftComp 2.1 Structure Gene.
- `pyvista.html` - generated interactive PyVista view.
