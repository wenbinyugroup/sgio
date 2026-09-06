# Core IR Layers (internal)

Internal note. Not part of the user documentation site.

The application/core IR is organized into four layers:

- `StructureGene` / `StructuralModel` — application-layer objects that compose
  the same FE core for different use cases.
- `SGAnalysisConfig` — SG-only analysis type, physics, model selection,
  damping, and related solver flags.
- `FEModel` — shared FE-level name, mesh reference, materials, and
  sections/orientations.
- `SGMesh` — nodal coordinates, element connectivities, sets, and attached data
  fields.

`StructuralModel` is the second minimal application-layer object. It wraps
`FEModel` plus lightweight containers for boundary conditions, loads, steps,
interactions, and coordinate systems.

## Compatibility proxies

`StructureGene` still exposes `mesh`, `materials`, `mocombos`, and the legacy
analysis fields `physics` / `model` through proxy properties backed by
`FEModel` and `SGAnalysisConfig`.

FE sections are the primary storage for SG material regions. `sg.mocombos`
remains a compatibility mapping view of
`{property_id: (material_name, orientation_angle)}`; new code should prefer
`sg.sections` / `sg.add_section(...)`.

See also [model_migration_compat.md](model_migration_compat.md).

## SG-on-Gmsh specification status

The published spec (`docs/source/ref/sg_on_gmsh.md`) freezes semantics and
ownership only. It does not require reader migration, writer migration, sidecar
bundle APIs, or round-trip tests to be complete. Later work must implement the
specification instead of redefining it.
