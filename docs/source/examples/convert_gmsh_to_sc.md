# Convert Gmsh Mesh to SwiftComp

## Problem Description

Given a 3D tetrahedral mesh generated in Gmsh (`.msh` format), convert it to a
SwiftComp input file for 3D solid homogenization.

## Solution

The mesh alone does not carry materials or analysis settings, so the example
uses the **SG-on-Gmsh bundle** convention: the `.msh` file supplies the mesh and
physical groups, `sections.json` supplies the section/material payloads, and
`config.json` supplies the analysis configuration. See
{doc}`/guide/sg_on_gmsh_spec` for the bundle layout.

```{literalinclude} ../../../examples/convert_gmsh_to_sc/run.py
:language: python
```

{func}`sgio.read_sg_from_gmsh_bundle` assembles the three files into a single
{class}`sgio.StructureGene`, and `model_type='SD1'` selects the 3D solid model.
{func}`sgio.write` then emits SwiftComp 2.1 input.

## Result

A SwiftComp 2.1 input file `sg33_cube_tetra4_min_gmsh41.sg` is written and ready for homogenization.

## File List

- [run.py](../../../examples/convert_gmsh_to_sc/run.py): Main Python script
- [sg33_cube_tetra4_min_gmsh41.msh](../../../examples/convert_gmsh_to_sc/sg33_cube_tetra4_min_gmsh41.msh): Gmsh mesh file
- [sections.json](../../../examples/convert_gmsh_to_sc/sections.json): Section and material definitions
- [config.json](../../../examples/convert_gmsh_to_sc/config.json): Analysis configuration
