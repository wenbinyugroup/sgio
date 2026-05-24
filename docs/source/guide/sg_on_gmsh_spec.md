(sg-on-gmsh-spec)=
# SG-on-Gmsh Serialization Specification

This document is the single normative specification for SG-oriented Gmsh
serialization in `sgio`.

Any older document or implementation detail that describes
`$SGLayerDef`, `$SGConfig`, or `.msh`-level `property_id` as canonical is
legacy guidance only and is not normative.

## Scope

The SG-on-Gmsh bundle is composed of:

- `main.msh`
- `sections.json`
- `config.json`

The design goals are:

- lossless `vabs -> gmsh -> vabs` round-trip for supported data,
- lossless `gmsh -> vabs -> gmsh` round-trip for supported enriched meshes,
- support for SwiftComp-oriented SG data,
- strict separation between mesh data, SG semantics, and sidecar payloads.

## File Responsibilities

### `main.msh`

`main.msh` stores only data that are strongly bound to mesh topology,
geometry, or element-wise fields.

Canonical content:

- Gmsh geometry and topology:
  - `$PhysicalNames`
  - `$Entities`
  - `$Nodes`
  - `$Elements`
- stable node and element identifiers when round-trip requires them:
  - `$ElementData "node_id"`
  - `$ElementData "element_id"`
- per-element local coordinate data:
  - `$ElementData "element_local_csys"`
- per-element additional rotations:
  - `$ElementData "additional_rotation_1"`
  - `$ElementData "additional_rotation_2"`
  - `$ElementData "additional_rotation_3"`
- optional compatibility or inspection fields:
  - `$ElementData "property_ref_csys"`
  - `$ElementData "property_ref_axis_y1"`
  - `$ElementData "property_ref_axis_y2"`
  - `$ElementData "property_ref_axis_y3"`
- other node or element fields that are genuinely mesh-bound.

`main.msh` is not the canonical home of:

- section or material payloads,
- analysis configuration,
- `.msh`-level public `property_id`.

### `sections.json`

`sections.json` stores section-level payloads that are not mesh-topology data.

This file is a section catalog, not a second schema for flattening model
payloads. Its file-level structure may organize records using keys such as:

- `kind`
- `theory`
- `name`
- `id`
- `payload`

However, `payload` itself must directly reuse the serialization semantics of
the underlying Python model. The payload field names must not be renamed into a
parallel JSON schema.

The current specification requires direct support for payloads corresponding to:

- `sgio.model.solid.CauchyContinuumModel`
- `sgio.model.beam.EulerBernoulliBeamModel`
- `sgio.model.beam.TimoshenkoBeamModel`
- `sgio.model.shell.KirchhoffLovePlateShellModel`
- `sgio.model.shell.ReissnerMindlinPlateShellModel`

Interpretation rules:

- `name` is the preferred external identity.
- `id` is the fallback identity when no usable name is available.
- physical names in `main.msh` may refer to either a material section or a
  structure section.

### `config.json`

`config.json` stores SG analysis configuration that is not strongly bound to
mesh topology.

Its canonical semantics are defined directly by
`sgio.core.sg_analysis_config.SGAnalysisConfig`.

The file-level organization must directly serialize that payload at the
top level. The configuration field names and nesting must follow the formal
serialization of `SGAnalysisConfig`, not a separately invented JSON naming
scheme.

Expected contents include, but are not limited to:

- `analysis`
- `physics`
- `model`
- `geo_correct`
- `do_damping`
- `is_temp_nonuniform`
- `force_flag`
- `steer_flag`

## Canonical Ownership

The canonical source of truth for each semantic concern is:

| Concern | Canonical owner |
|---|---|
| section identity | `main.msh` via `$PhysicalNames` + `$Entities` + `$Elements` |
| section name | `main.msh` via `$PhysicalNames` |
| section payload | `sections.json` |
| analysis config | `config.json` |
| element local coordinate system | `$ElementData "element_local_csys"` |
| per-element additional rotations | `$ElementData "additional_rotation_1/2/3"` |
| compatibility local-csys alias | `$ElementData "property_ref_csys"` |
| compatibility axis vectors | `$ElementData "property_ref_axis_y1/y2/y3"` |

## Canonical Semantic Chain

The canonical mesh-to-section semantic chain is:

`element -> entity -> physical tag -> physical name -> section`

Implications:

- section semantics are driven by physical entity assignment,
- physical name is the preferred external linkage token,
- element ownership is inferred from the entity referenced by `$Elements`,
- `.msh`-level `property_id` is not part of the public serialization contract.

## Compatibility and Legacy Status

### `property_id`

`property_id` is fully hidden from the external contract.

Rules:

- it may still exist as an internal derived implementation detail,
- it must not be required by the normative `.msh` contract,
- it must not appear in new sidecar schemas,
- it must not appear in public API contracts or normative documentation,
- it must not be presented as user-facing canonical identity.

### Local coordinate compatibility fields

`element_local_csys` is the canonical field name.

Compatibility fields remain recognized during migration:

- `property_ref_csys`
- `property_ref_axis_y1`
- `property_ref_axis_y2`
- `property_ref_axis_y3`

Compatibility status:

- `property_ref_csys` is a readable and writable compatibility alias during the
  migration period, but not the canonical name.
- `property_ref_axis_y1/y2/y3` are non-canonical compatibility and inspection
  fields. They do not own the only authoritative meaning.

Reader priority is defined as:

1. `element_local_csys`
2. `property_ref_csys`
3. reconstruction from `property_ref_axis_y1/y2/y3`
4. default orientation

### Additional rotation fields

The canonical additional rotation representation is three separate
per-element `$ElementData` fields:

- `additional_rotation_1`
- `additional_rotation_2`
- `additional_rotation_3`

Each field stores one scalar per element.

This specification freezes:

- field names,
- storage location in `main.msh`,
- per-element ownership.

Exact unit, positive direction, and composition order remain implementation
details to be refined later, but they must not collapse back into a single
`additional_rotation` field.

### Legacy blocks

The following blocks are legacy:

- `$SGLayerDef`
- `$SGConfig`

Legacy rules:

- new normative writers must stop treating them as canonical outputs,
- transition readers may still consume them for backward compatibility,
- migration paths must map their information into `sections.json` and
  `config.json`.

## File-Level Organization

### `sections.json` minimum organization layer

The minimum organization layer is:

```json
{
  "sections": [
    {
      "kind": "material",
      "theory": "cauchy_continuum",
      "name": "matrix",
      "id": 101,
      "payload": {}
    }
  ]
}
```

Constraints:

- `payload` reuses the corresponding model serialization directly.
- `name` is optional only when the workflow truly cannot provide one.
- `id` is optional only when name-based linking is sufficient.
- if both are present, name matching has higher priority than id matching.

### `config.json` minimum organization layer

The minimum organization layer is:

```json
{
  "analysis": 0,
  "physics": 0,
  "model": 0,
  "geo_correct": false,
  "do_damping": 0,
  "is_temp_nonuniform": 0,
  "force_flag": 0,
  "steer_flag": 0
}
```

Constraint:

- the top-level object must remain directly mappable to `SGAnalysisConfig`.

## Required and Optional Data by Input Scenario

### VABS 2D cross-section

Required:

- 2D analysis cells in `main.msh`
- physical entity assignment for section identity
- section payloads in `sections.json`
- analysis configuration in `config.json`

Optional:

- `element_local_csys`
- `additional_rotation_1/2/3`
- compatibility axis fields
- stable `node_id` and `element_id` if round-trip preservation is required

### SwiftComp 2D

Required:

- 2D analysis cells in `main.msh`
- physical entity assignment for section identity
- section payloads in `sections.json`
- `config.json` matching the intended SwiftComp analysis path

Optional:

- `element_local_csys`
- `additional_rotation_1/2/3`
- compatibility axis fields
- stable `node_id` and `element_id`

### SwiftComp 3D

Required:

- 3D analysis cells in `main.msh`
- volume-oriented physical entity assignment for section identity
- section payloads in `sections.json`
- `config.json` matching the intended 3D SG analysis path

Optional:

- `element_local_csys`
- `additional_rotation_1/2/3`
- compatibility axis fields
- stable `node_id` and `element_id`

## Matching Rules

When resolving physical names to section records:

1. match by `name` when a usable name exists,
2. fall back to `id` only when name is absent or cannot be matched.

This rule applies to both:

- material sections,
- structure sections.

## Implementation Boundary Frozen by Phase 1

Phase 1 freezes semantics and ownership only.

It does not yet require:

- reader migration to be fully implemented,
- writer migration to be fully implemented,
- sidecar bundle APIs to be complete,
- round-trip tests to be complete.

Those changes belong to later phases and must implement this specification
instead of redefining it.
