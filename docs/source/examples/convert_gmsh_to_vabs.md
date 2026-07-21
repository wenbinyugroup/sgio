# Convert a Gmsh Bundle to VABS

## Problem Description

An external CAD + Gmsh workflow produces a 2D section mesh. Convert it into a
VABS input file, with materials and analysis settings supplied alongside the
mesh.

## Solution

The example uses the **SG-on-Gmsh bundle** convention, which keeps the three
concerns in separate files (see {doc}`/guide/sg_on_gmsh_spec`):

- `sg21_box_quad4_min_gmsh41.msh` — the section mesh and its physical groups
- `sections.json` — section and material payloads
- `config.json` — the analysis configuration

```{literalinclude} ../../../examples/convert_gmsh_to_vabs/run.py
:language: python
```

{func}`sgio.read_sg_from_gmsh_bundle` reads the complete bundle into a
{class}`sgio.StructureGene`, which {func}`sgio.write` then emits as VABS input.
This is the recommended path for external CAD + Gmsh workflows.

## Result

`sg21_box_quad4_min_gmsh41.sg` is written, ready for VABS.

```bash
uv run python examples/convert_gmsh_to_vabs/run.py
```

## File List

- [run.py](../../../examples/convert_gmsh_to_vabs/run.py): Main Python script
- [sg21_box_quad4_min_gmsh41.msh](../../../examples/convert_gmsh_to_vabs/sg21_box_quad4_min_gmsh41.msh): Gmsh section mesh
- [sections.json](../../../examples/convert_gmsh_to_vabs/sections.json): Section and material definitions
- [config.json](../../../examples/convert_gmsh_to_vabs/config.json): Analysis configuration
- [sg21_box_quad4_min_gmsh41.sg](../../../examples/convert_gmsh_to_vabs/sg21_box_quad4_min_gmsh41.sg): Generated VABS input
