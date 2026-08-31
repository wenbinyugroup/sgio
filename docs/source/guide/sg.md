# Structure Gene (SG) Data

One of the main tasks of sgio is to convert data between different formats.
This allows users to create SGs with arbitrary complexity using their own
tools. To do this properly, the key is to make sure that all necessary data are
provided.

Current application/core IR is organized into four layers:

- `StructureGene` / `StructuralModel`
  - Application-layer objects that compose the same FE core for different use
    cases.
- `SGAnalysisConfig`
  - SG-only analysis type, physics, model selection, damping, and related
    solver flags.
- `FEModel`
  - Shared FE-level name, mesh reference, materials, and
    sections/orientations.
- `SGMesh`
  - Nodal coordinates, element connectivities, sets, and attached data fields.

For backward compatibility, `StructureGene` still exposes `mesh`, `materials`,
`mocombos`, and legacy analysis fields like `physics` / `model` through proxy
properties backed by `FEModel` and `SGAnalysisConfig`.

Starting from phase 7, `StructuralModel` provides the second minimal
application-layer object. It currently focuses on structural wrappers around
`FEModel` plus lightweight containers for boundary conditions, loads, steps,
interactions, and coordinate systems.

Starting from the phase-4 refactor, FE sections are the primary storage for SG
material regions. `sg.mocombos` remains available as a compatibility mapping
view of `{property_id: (material_name, orientation_angle)}`, while new code
should prefer `sg.sections` / `sg.add_section(...)`.

## What a "Correct" SG Model Must Contain

A file is not a "correct" SG model just because `sgio` can read it or write it.
A correct SG model must contain enough information for the target solver to
interpret:

- the geometry,
- the mesh topology,
- the material regions,
- the material properties,
- and the structural model assumptions.

In practice, the minimum useful SG model contains the following data.

### 1. Geometry and mesh

The model must contain:

- nodal coordinates,
- element connectivities,
- a consistent geometry dimension (`sgdim`),
- and element types supported by the target solver.

Examples:

- VABS cross-sections are 2D section meshes.
- SwiftComp may be 1D, 2D, or 3D depending on `sgdim` and `model_type`.

If isolated nodes, unsupported element types, or mixed dimensions are present,
the converted SG may be incomplete or unusable.

### 2. Material-region assignment

Every analysis element should belong to a material region.
In `sgio`, this is represented by section/material-region identifiers such as
`property_id`.

For a physically correct SG, this means:

- each analysis element has one region ID,
- each region ID maps to one section,
- and each section maps to one material and one orientation definition.

If this mapping is missing, `sgio` may still create a placeholder SG, but the
result is only a mesh container, not a reliable analysis model.

### 3. Material definitions

The SG must include material properties for all referenced regions.

At minimum:

- every material name referenced by a section must exist,
- and the material model must contain the properties required by the target
  solver.

Typical examples:

- isotropic elastic constants,
- orthotropic engineering constants,
- density or thermal data when the intended solver setup needs them.

### 4. Section orientation data

For laminated or anisotropic regions, the SG must also define the in-plane
orientation of each material region.

In `sgio`, this is stored through sections and exposed by the legacy
`sg.mocombos` view as:

- `property_id -> (material_name, orientation_angle)`

If all regions are isotropic, this angle may be zero everywhere.
For composites, omitting orientation data usually makes the model physically
wrong even if conversion succeeds.

For per-element local frames, `mesh.cell_data['property_ref_csys']` stores nine
values `(a1, a2, a3, b1, b2, b3, c1, c2, c3)`. The points define a local frame:
`c` is its origin, `a-c` is local `y1`, and `b-c` lies in the local `y1-y2`
plane. These values always share the same 3D source frame as `mesh.points`.
When a 2D solver file needs a different coordinate order, the output mapper
uses `model_space` on a private export mesh; it does not modify the SG held by
the caller.

### 5. Structural model selection

The SG must match the intended structural model.

Typical choices are:

- `BM1`: Euler-Bernoulli beam,
- `BM2`: Timoshenko beam,
- `PL1` / `PL2`: plate or shell,
- `SD1`: 3D solid.

This selection controls how the same mesh is interpreted by the solver.
An otherwise valid mesh can still be the wrong SG if the model type is wrong.

### 6. Plane or embedding of the section

For lower-dimensional models, coordinates must be embedded consistently in 3D
space.

For example, a 2D cross-section may lie in:

- `xy`,
- `yz`,
- or `zx`.

When writing solver input, `sgio` uses `model_space` to decide how the 2D
section coordinates are projected into solver coordinates.
If the plane is wrong, the generated SG is geometrically inconsistent even if
all nodes and elements are present.

## Minimum Checklist

Before calling a model "correct", check:

- the mesh dimension matches the intended solver model,
- all analysis elements have valid region IDs,
- every region ID resolves to a material section,
- every referenced material is defined,
- orientation data are present where anisotropy matters,
- and the section plane or model space is explicitly correct.

## Format-Specific Notes

- Gmsh is primarily a mesh carrier. To become a correct SG, it usually needs
  region IDs and external material definitions.
- VABS requires a 2D section mesh and beam-type model (`BM1` or `BM2`).
- SwiftComp accepts 1D/2D/3D SGs, but still requires consistent region and
  material data.

For Gmsh-specific requirements, see {doc}`gmsh_to_sg`.
