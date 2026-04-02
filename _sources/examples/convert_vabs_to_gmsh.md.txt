# Convert VABS Cross-Section Mesh to Gmsh

## Problem Description

Given a VABS cross-section file, export the mesh to Gmsh format for geometry inspection or visualization without running a full format conversion that includes materials.

## Solution

```{literalinclude} ../../../examples/convert_vabs_to_gmsh/convert_mesh_data_vabs2gmsh.py
:language: python
```

The `mesh_only=True` flag skips material data so the output is a pure mesh file. `model_type='BM2'` is required to correctly interpret the VABS file layout.

## Result

A Gmsh `.msh` file is written. Open it with:

```bash
gmsh cs_box_t_vabs41.msh
```

or inspect it in ParaView.

## File List

- [convert_mesh_data_vabs2gmsh.py](../../../examples/convert_vabs_to_gmsh/convert_mesh_data_vabs2gmsh.py): Main Python script
