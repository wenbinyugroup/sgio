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
