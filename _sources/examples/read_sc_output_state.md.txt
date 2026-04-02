# Read SwiftComp Dehomogenization Output (Local Stress Fields)

## Problem Description

After running SwiftComp dehomogenization analysis on a 3D solid structure gene, read the local state output files, map the stress data onto the mesh, and export to Gmsh for visualization.

## Solution

```{literalinclude} ../../../examples/read_sc_output_d/read_sc_output_d.py
:language: python
```

`analysis='d'` selects dehomogenization output. `extension=['sn', 'snm']` reads the SwiftComp local state files. `getState('s')` retrieves the Cauchy stress tensor. The six components are added to the mesh as cell data arrays named `S11`, `S12`, `S13`, `S22`, `S23`, `S33`.

## Result

A Gmsh `.msh` file is written with stress components as cell data. Open it with:

```{code-block} bash
gmsh sg31t_hex20_sc21.msh
```

## File List

- [read_sc_output_d.py](../../../examples/read_sc_output_d/read_sc_output_d.py): Main Python script
- [sg31t_hex20_sc21.sg](../../../examples/read_sc_output_d/sg31t_hex20_sc21.sg): SwiftComp 3D input file
- [sg31t_hex20_sc21.sg.sn](../../../examples/read_sc_output_d/sg31t_hex20_sc21.sg.sn): SwiftComp dehomogenization output (node data)
- [sg31t_hex20_sc21.sg.snm](../../../examples/read_sc_output_d/sg31t_hex20_sc21.sg.snm): SwiftComp dehomogenization output (material-frame node data)
