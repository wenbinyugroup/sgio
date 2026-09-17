# Convert Abaqus Cross-Section With An SG Manifest

## Problem description

An Abaqus `.inp` file carries the mesh, materials and composite sections of a
beam cross-section, but not the SG parameters: it cannot state that the model is
a 2D SG, which beam model to use, or which plane the section is drawn in.
Store those parameters in a file instead of passing them as arguments, and
convert the cross-section to SwiftComp.

## Explaination of the solution

`sg2_box.sg.json` is an SG manifest. It references
`sg2_box_composite_section.inp` and adds `sgdim` (2), `model_type` (`BM1`) and
`model_space` (`xy`). `sgio.read(..., 'sg_manifest')` reads both files into one
`StructureGene`.

`sgio.write(..., 'sg_manifest', model_file='sg2_box.sc', model_file_format='swiftcomp')`
then writes the SwiftComp input and a second manifest, `sg2_box_sc.sg.json`.
SwiftComp input already holds the materials, sections and model space, so that
manifest only records the model file, its format version, `sgdim` and
`model_type`. Reading it back checks the SwiftComp header against the manifest.

## Result

After running the script, you get `sg2_box.sc` and `sg2_box_sc.sg.json`; the
script prints the structure gene read from each manifest.

Run it with:

```bash
uv run python examples/convert_abaqus_cs_with_sg_manifest/run.py
```

## List of all files

- `run.py`
- `sg2_box_composite_section.inp`
- `sg2_box.sg.json`
- `sg2_box.sc`
- `sg2_box_sc.sg.json`
