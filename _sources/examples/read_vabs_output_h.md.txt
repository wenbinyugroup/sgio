# Read VABS Homogenized Output (Beam Properties)

## Problem Description

After running VABS homogenization, read the `.K` output file to extract effective beam properties such as axial stiffness, torsional stiffness, and bending stiffness for use in beam-level structural analysis.

## Solution

```{literalinclude} ../../../examples/read_vabs_output_h/read_vabs_output_h.py
:language: python
```

`model_type='BM2'` selects the Timoshenko beam model output layout. Use `model.get('<key>')` to retrieve individual properties by name (e.g. `'ea'`, `'gj'`, `'ei22'`, `'ei33'`).

## Result

The script returns scalar beam property values that can be used directly in beam-level models.

## File List

- [read_vabs_output_h.py](../../../examples/read_vabs_output_h/read_vabs_output_h.py): Main Python script
- [cs_box_t_vabs41.sg.K](../../../examples/read_vabs_output_h/cs_box_t_vabs41.sg.K): VABS homogenized beam properties output
