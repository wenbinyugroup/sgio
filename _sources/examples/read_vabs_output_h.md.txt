# Read VABS Homogenized Output (Beam Properties)

## Problem Description

After running VABS homogenization, read the `.K` output file to extract effective beam properties such as axial stiffness, torsional stiffness, and bending stiffness for use in beam-level structural analysis.

## Solution

```{literalinclude} ../../../examples/read_vabs_output_h/run.py
:language: python
```

`model_type='BM2'` selects the Timoshenko beam model output layout. For named
beam properties such as `ea`, `gj`, `ei22`, and `ei33`, use the direct model
attributes. Use the typed section-query methods only when you need matrix or
theory-bound quantities.

## Result

The script returns scalar beam property values that can be used directly in beam-level models.

## File List

- [run.py](../../../examples/read_vabs_output_h/run.py): Main Python script
- [cs_box_t_vabs41.sg.K](../../../examples/read_vabs_output_h/cs_box_t_vabs41.sg.K): VABS homogenized beam properties output
