# Structure Gene (SG) Data

One of the main tasks of sgio is to convert data between different formats.
This allows users to create SGs with arbitrary complexity using their own
tools. To do this properly, the key is to make sure that all necessary data are
provided.

Current SG IR is organized into four layers:

- `StructureGene`
  - SG-specific dimensions, periodic mesh metadata, and SG-only geometry data.
- `SGAnalysisConfig`
  - Analysis type, physics, model selection, damping, and related solver flags.
- `FEModel`
  - FE-level name, mesh reference, materials, and FE sections/orientations.
- `SGMesh`
  - Nodal coordinates, element connectivities, sets, and attached data fields.

For backward compatibility, `StructureGene` still exposes `mesh`, `materials`,
`mocombos`, and legacy analysis fields like `physics` / `model` through proxy
properties backed by `FEModel` and `SGAnalysisConfig`.

Starting from the phase-4 refactor, FE sections are the primary storage for SG
material regions. `sg.mocombos` remains available as a compatibility mapping
view of `{property_id: (material_name, orientation_angle)}`, while new code
should prefer `sg.sections` / `sg.add_section(...)`.
