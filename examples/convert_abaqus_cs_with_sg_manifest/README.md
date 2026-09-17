# Convert Abaqus Cross-Section With An SG Manifest

## Problem description

An Abaqus `.inp` file carries the mesh, materials and composite sections of a
beam cross-section, but not the SG parameters: it cannot state that the model is
a 2D SG, which beam model to use, or which plane the section is drawn in.
Convert the cross-section to SwiftComp and read the result back, supplying those
parameters either as arguments or from a file.

## Explaination of the solution

The script does the same conversion in two equivalent ways and asserts that both
write the same `sg2_box.sc`.

**Method 1: API arguments.**
`sgio.read(..., 'abaqus', sgdim=2, model_type='BM1', model_space='xy')` reads the
`.inp` and `sgio.write(sg, 'sg2_box.sc', 'sc')` writes the SwiftComp input.
Reading it back with `sgio.read('sg2_box.sc', 'sc', model_type='BM1')` still
needs the model type, because a SwiftComp input does not state it.

**Method 2: SG manifests.**
`sg2_box.sg.json` references `sg2_box_composite_section.inp` and adds `sgdim`
(2), `model_type` (`BM1`) and `model_space` (`xy`).
`sgio.read(..., 'sg_manifest')` reads both files into one `StructureGene`.

`sgio.write(..., 'sg_manifest', model_file='sg2_box.sc', model_file_format='swiftcomp')`
then writes the SwiftComp input and a second manifest, `sg2_box_sc.sg.json`.
SwiftComp input already holds the materials, sections and model space, so that
manifest only records the model file, its format version, `sgdim` and
`model_type`. Reading it back needs no arguments and checks the SwiftComp header
against the manifest.

## Result

After running the script, you get `sg2_box.sc` and `sg2_box_sc.sg.json`; the
script prints the structure gene read back by each method.

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
