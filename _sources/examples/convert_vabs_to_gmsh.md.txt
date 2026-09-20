<!-- Generated from examples/convert_vabs_to_gmsh/README.md. Do not edit; edit the README instead. -->

# Convert VABS Cross-Section Mesh to Gmsh

## Problem Description

Given a VABS cross-section file, export it as a Gmsh mesh for inspection,
visualization or Gmsh-based workflows, without losing the materials and SG
parameters the mesh cannot hold.

## Solution

```{literalinclude} ../../../examples/convert_vabs_to_gmsh/run.py
:language: python
```

{func}`sgio.write` with `'sg_manifest'` writes the Gmsh model file `main.msh`
and the SG manifest `main.sg.json` that references it. The manifest carries
`sgdim`, model type, model space, analysis configuration, materials and
sections; see {doc}`/ref/sg_manifest`.

## Result

`main.msh` opens in Gmsh or ParaView:

```bash
gmsh main.msh
```

`sgio.read('main.sg.json', 'sg_manifest')` reads the full structure gene back.

```{figure} ../../../examples/convert_vabs_to_gmsh/pyvista.png
:align: center
:width: 80%
```

## File List

- [run.py](../../../examples/convert_vabs_to_gmsh/run.py): Main Python script
- [cs_box_t_vabs41.sg](../../../examples/convert_vabs_to_gmsh/cs_box_t_vabs41.sg): VABS input
- [main.msh](../../../examples/convert_vabs_to_gmsh/main.msh): Generated Gmsh mesh
- [main.sg.json](../../../examples/convert_vabs_to_gmsh/main.sg.json): Generated SG manifest
- [pyvista.png](../../../examples/convert_vabs_to_gmsh/pyvista.png): PyVista mesh preview
