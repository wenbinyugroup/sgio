# Read VABS Dehomogenization Output (Local Stress Fields)

## Problem Description

After running VABS dehomogenization analysis, read the element-level stress output, map it onto the cross-section mesh, and export the result to Gmsh for visualization.

## Solution

```{literalinclude} ../../../examples/read_vabs_output_d/read_vabs_output_d.py
:language: python
```

`analysis='d'` selects dehomogenization output. `extension='ele'` reads element-level data files (`.ELE`). `getState('esm')` retrieves the stress tensor in material coordinates. The six components are added to the mesh as cell data arrays.

## Result

A Gmsh `.msh` file is written with the stress components (`S11`, `S12`, ..., `S33`) as cell data. Open it with:

```bash
gmsh cs_box_t_vabs41_local.msh
```

```{figure} ../../../examples/read_vabs_output_d/cs_box_t_vabs41_ele_sm11.msh.png
:align: center
```

## File List

- [read_vabs_output_d.py](../../../examples/read_vabs_output_d/read_vabs_output_d.py): Main Python script
- [cs_box_t_vabs41.sg](../../../examples/read_vabs_output_d/cs_box_t_vabs41.sg): VABS cross-section input file
- [cs_box_t_vabs41.sg.ELE](../../../examples/read_vabs_output_d/cs_box_t_vabs41.sg.ELE): VABS dehomogenization element output
