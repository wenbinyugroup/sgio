(sg-manifest-spec)=
# SG Manifest

Normative specification of the SG manifest (`*.sg.json`), the primary on-disk
form of a structure gene in `sgio`.

No single file format fully describes an SG: an Abaqus `.inp` or Gmsh `.msh`
carries no `sgdim`, model type or model space, a `.msh` carries no materials,
and a SwiftComp input does not state its own `smdim`. A manifest holds these
SG-level parameters and references exactly one **model file** that holds the
rest.

```python
import sgio

sg = sgio.read('section.sg.json', 'sg_manifest')
sgio.convert('section.sg.json', 'section.sg', 'sg_manifest', 'vabs')

# Writes section.msh and section.sg.json
sgio.write(
    sg, 'section.sg.json', 'sg_manifest',
    model_file='section.msh', model_file_format='gmsh',
)
```

## Schema (version 1)

```json
{
  "sg_manifest_version": 1,
  "model_file": {"path": "section.msh", "format": "gmsh"},
  "sgdim": 2,
  "model_type": "BM2",
  "model_space": "xy",
  "initial_twist": 0.0,
  "initial_curvature": [0.0, 0.0],
  "oblique": [1.0, 0.0],
  "config": {"analysis": 0, "physics": 0},
  "materials": [
    {"name": "carbon", "model": "sd1", "isotropy": 1, "elastic": {"e1": 1.4e11}}
  ],
  "sections": [
    {"name": "ply_0", "id": 1, "material": "carbon", "orientation": 0.0},
    {"name": "ply_45", "id": 2, "material": "carbon", "orientation": 45.0}
  ]
}
```

| Field | Rule |
|---|---|
| `sg_manifest_version` | required; unknown versions are rejected |
| `model_file.path` | required; relative to the manifest directory |
| `model_file.format` | required; `abaqus`, `gmsh`, `swiftcomp` or `vabs` |
| `model_file.format_version` | required for `swiftcomp` and `vabs`; not allowed for other formats, whose version is read from the file |
| `sgdim` | required; never inferred from element dimension |
| `model_type` | required; the same string the API takes (`SD1`, `PL1`, `BM2`, ...) |
| `model_space` | mesh axes of a 1D/2D SG (`x`/`y`/`z`, `xy`/`yz`/`zx`); required for `sgdim` 1 and 2 unless the model file format defines it; not allowed for `sgdim` 3 |
| `initial_twist`, `initial_curvature`, `oblique` | optional beam/shell geometry |
| `config` | optional `SGAnalysisConfig` fields, except `model` (given by `model_type`) |
| `materials` | grouped material records, each with a unique `name` |
| `sections` | records with `name` and/or `id`, a declared `material`, and an optional `orientation` in degrees (0 when omitted) |

Unknown fields are rejected.

## One Authority per Field

Each model file format owns the data it can express; the manifest must not
repeat an owned field.

| Model file format | Owns (not allowed in the manifest) |
|---|---|
| `abaqus` | `materials`, `sections` |
| `gmsh` | nothing |
| `swiftcomp`, `vabs` | `materials`, `sections`, `config`, `model_space`, beam/shell geometry |

`sgdim` and `model_type` are always manifest fields. When the model file also
encodes them (SwiftComp and VABS headers), reading checks that they agree.
Arguments passed to {func}`sgio.read` must agree with the manifest as well.

## Sections and Mesh Elements

For a Gmsh model file, sections bind mesh physical groups to materials:

```text
element -> entity -> physical tag -> physical name -> section -> material
```

A section record matches a physical group by `name`, falling back to `id` (the
physical tag) when the name is absent or unmatched. Elements whose physical
group matches no section — an auxiliary `boundary` group, for example — are not
SG elements. The mesh-level field layout is in {doc}`sg_on_gmsh`.

## Writing

`sgio.write(..., 'sg_manifest', model_file=..., model_file_format=...)` writes
the model file first, then the manifest without the owned fields. Model files
can be written as `gmsh`, `swiftcomp` or `vabs`; `sgio` has no Abaqus writer.
The manifest records the `swiftcomp`/`vabs` format version actually written.
