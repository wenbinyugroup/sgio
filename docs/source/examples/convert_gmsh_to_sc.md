# Convert Gmsh Mesh to SwiftComp

## Problem Description

Given a 3D tetrahedral mesh generated in Gmsh (`.msh` format) and a JSON material database, convert the mesh to a SwiftComp input file for 3D solid homogenization.

## Solution

```{literalinclude} ../../../examples/convert_gmsh_to_sc/run.py
:language: python
```

`sgio.read_materials_from_json()` loads the material definitions from `materials.json` and assigns them to the structure gene. `model_type='sd1'` selects the 3D solid model.

## Result

A SwiftComp 2.1 input file `sg33_cube_tetra4_min_gmsh41.sg` is written and ready for homogenization.

## File List

- [run.py](../../../examples/convert_gmsh_to_sc/run.py): Main Python script
- [sg33_cube_tetra4_min_gmsh41.msh](../../../examples/convert_gmsh_to_sc/sg33_cube_tetra4_min_gmsh41.msh): Gmsh mesh file
- [materials.json](../../../examples/convert_gmsh_to_sc/materials.json): Material database (JSON)
