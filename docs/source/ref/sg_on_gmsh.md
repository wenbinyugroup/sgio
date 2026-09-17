(sg-on-gmsh-spec)=
# SG-on-Gmsh Serialization

Normative specification for SG-oriented Gmsh serialization in `sgio`.
For the authoring workflow, see {doc}`/guide/gmsh`.

## Files

| File | Holds |
|---|---|
| `*.msh` (model file) | mesh topology, geometry, element-wise fields |
| `*.sg.json` ({doc}`SG manifest <sg_manifest>`) | `sgdim`, model type, model space, analysis configuration, materials, sections |

Design goals: lossless `vabs -> gmsh -> vabs` and `gmsh -> vabs -> gmsh`
round-trips for supported data, SwiftComp-oriented SG data, and strict
separation between mesh data and SG semantics.

## The `.msh` Model File

Carries only data strongly bound to mesh topology, geometry, or element-wise
fields.

| Block | Content |
|---|---|
| `$PhysicalNames`, `$Entities`, `$Nodes`, `$Elements` | Gmsh geometry and topology |
| `$ElementData "node_id"`, `"element_id"` | stable identifiers, when round-trip requires them |
| `$ElementData "element_local_csys"` | per-element local coordinate system |
| `$ElementData "additional_rotation_1/2/3"` | per-element additional rotations |
| `$ElementData "property_ref_csys"`, `"property_ref_axis_y1/y2/y3"` | compatibility and inspection fields |

The `.msh` file is **not** the canonical home of materials, sections, analysis
configuration, or a `.msh`-level public `property_id`.

### Semantic chain

```text
element -> entity -> physical tag -> physical name -> section
```

Section semantics are driven by physical entity assignment; the physical name
is the preferred external linkage token. Element ownership is inferred from
the entity referenced in `$Elements`.

In 2D, material-region physical tags belong on surface entities; in 3D, on
volume entities. Point and curve entities may exist but do not define regions.

### Block layout

`$PhysicalNames` — one line per group, `dim tag "name"`:

```text
$PhysicalNames
2
2 101 "skin"
2 102 "core"
$EndPhysicalNames
```

`$Entities` — attaches physical tags to geometric entities. A surface entity
line ending in `1 101` carries physical tag `101`.

`$Nodes` — a block header, then per-entity blocks of node tags followed by
`x y z` coordinates. Tags need not be contiguous. For a 2D section in `xy`,
`z` is `0`.

`$Elements` — a block header, then per-entity blocks:

```text
entityDim entityTag elementType numElementsInBlock
elementTag node1 node2 ...
```

Each block holds elements of one entity and one element type. Node ordering
must follow Gmsh's standard ordering for the element type (`triangle`:
`n1 n2 n3`; `triangle6`: `n1..n6`; `quad`: `n1..n4`).

Node IDs in `$Nodes` must match those used in `$Elements`.

### Element local coordinate systems

`element_local_csys` is the canonical field. Each element carries nine
components `(a1, a2, a3, b1, b2, b3, c1, c2, c3)`, where `c` is the local
origin, `a - c` defines local axis `y1`, `b - c` lies in the local `y1-y2`
plane, and the basis is reconstructed right-handed. Values always share the
same 3D source frame as `mesh.points`.

Reader priority:

1. `element_local_csys`
2. `property_ref_csys` — readable/writable compatibility alias
3. reconstruction from `property_ref_axis_y1/y2/y3` — inspection fields
4. default orientation

### Additional rotations

Three separate per-element `$ElementData` fields, one scalar each:
`additional_rotation_1`, `additional_rotation_2`, `additional_rotation_3`.
Field names, storage location, and per-element ownership are frozen. Unit,
positive direction, and composition order remain implementation details, but
must not collapse back into a single `additional_rotation` field.

## Materials, Sections and Configuration

These live in the SG manifest; see {doc}`sg_manifest`. A manifest section
record matches a physical group by `name`, falling back to `id`.

## Canonical Ownership

| Concern | Canonical owner |
|---|---|
| section identity | `.msh`: `$PhysicalNames` + `$Entities` + `$Elements` |
| section name | `.msh`: `$PhysicalNames` |
| materials and section bindings | SG manifest: `materials`, `sections` |
| `sgdim`, model type, model space, analysis config | SG manifest |
| element local coordinate system | `$ElementData "element_local_csys"` |
| per-element additional rotations | `$ElementData "additional_rotation_1/2/3"` |

## Required Data by Scenario

| | VABS 2D | SwiftComp 2D | SwiftComp 3D |
|---|---|---|---|
| analysis cells in the `.msh` | 2D | 2D | 3D |
| physical entity assignment | surface | surface | volume |
| manifest `materials`, `sections` | required | required | required |
| manifest `model_space` | required | required | — |
| `element_local_csys` | optional | optional | optional |
| `additional_rotation_1/2/3` | optional | optional | optional |
| stable `node_id` / `element_id` | optional | optional | optional |

## Legacy Status

`property_id` is hidden from the external contract. It may exist as an internal
derived detail, but it is not required by the `.msh` contract, must not appear
in manifest schemas or public API contracts, and is not user-facing identity.

`$SGLayerDef` and `$SGConfig` are legacy blocks. Writers do not emit them and
reading an SG does not apply them: the manifest is the only source of section
bindings and configuration.
