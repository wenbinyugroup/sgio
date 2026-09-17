# Convert an Abaqus Cross-Section with an SG Manifest

## Problem Description

An Abaqus `.inp` file carries the mesh, materials and composite sections of a
beam cross-section, but not the SG parameters: it cannot state that the model is
a 2D SG, which beam model to use, or which plane the section is drawn in. Store
those parameters in a file instead of passing them as arguments, and convert the
cross-section to SwiftComp.

## Solution

The script does the conversion in two equivalent ways and asserts that both
write the same `sg2_box.sc`: method 1 passes `sgdim`, `model_type` and
`model_space` as arguments of {func}`sgio.read`; method 2 keeps them in SG
manifests.

`sg2_box.sg.json` is an SG manifest (see {doc}`/ref/sg_manifest`) that
references the Abaqus input:

```{literalinclude} ../../../examples/convert_abaqus_cs_with_sg_manifest/sg2_box.sg.json
:language: json
```

```{literalinclude} ../../../examples/convert_abaqus_cs_with_sg_manifest/run.py
:language: python
```

{func}`sgio.read` with `'sg_manifest'` reads the manifest and the `.inp` into one
{class}`sgio.StructureGene`. {func}`sgio.write` with `'sg_manifest'` writes the
SwiftComp input and a new manifest. SwiftComp input already holds the materials,
sections and model space, so the new manifest records only the model file, its
format version, `sgdim` and `model_type`; reading it back checks the SwiftComp
header against it. Reading `sg2_box.sc` directly (method 1) still needs
`model_type`, because a SwiftComp input does not state it.

## Result

`sg2_box.sc` and its manifest `sg2_box_sc.sg.json` are written:

```{literalinclude} ../../../examples/convert_abaqus_cs_with_sg_manifest/sg2_box_sc.sg.json
:language: json
```

```bash
uv run python examples/convert_abaqus_cs_with_sg_manifest/run.py
```

## File List

- [run.py](../../../examples/convert_abaqus_cs_with_sg_manifest/run.py): Main Python script
- [sg2_box_composite_section.inp](../../../examples/convert_abaqus_cs_with_sg_manifest/sg2_box_composite_section.inp): Abaqus cross-section input
- [sg2_box.sg.json](../../../examples/convert_abaqus_cs_with_sg_manifest/sg2_box.sg.json): SG manifest for the Abaqus input
- [sg2_box.sc](../../../examples/convert_abaqus_cs_with_sg_manifest/sg2_box.sc): Generated SwiftComp input
- [sg2_box_sc.sg.json](../../../examples/convert_abaqus_cs_with_sg_manifest/sg2_box_sc.sg.json): Generated SG manifest for the SwiftComp input
