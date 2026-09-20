# Prepare a Gmsh Mesh for SG Conversion

A `.msh` file that `sgio` can read is not automatically a `.msh` file that
becomes a physically correct SG. This page covers what to author in Gmsh, and
what has to be supplied around it.

The field-level contract is specified in {doc}`/ref/sg_on_gmsh` and
{doc}`/ref/sg_manifest`.

## What the Mesh Must Carry

- nodal coordinates
- analysis element types the target solver supports
- physical groups on the analysis cells, one per material region
- a mesh dimension matching the target SG

Material definitions, orientation angles, model choice, and solver flags are
**not** authored in Gmsh — they are supplied by the SG manifest that
references the mesh.

## 1. Match the Analysis Dimension

VABS input is a 2D cross-section: mesh a section, not a volume, and use
`sgdim=2` with `model_type='BM1'` or `'BM2'`.

SwiftComp accepts `sgdim` of 1, 2, or 3 — pick `model_type` to match: `BM1` /
`BM2` for beam cross-sections, `PL1` / `PL2` for plates and shells, `SD1` for
3D solids.

Supported cell types per dimension are listed in {doc}`/ref/formats`.

## 2. Define Physical Groups for Material Regions

This is the most important Gmsh-specific requirement. Physical tags become the
region identifiers that connect elements to materials and orientations.

- one physical group per material region
- applied to the actual analysis cells, not only to boundary entities
- in 2D on surface entities, in 3D on volume entities
- stable, meaningful names: `matrix`, `skin_0deg`, `web_glass`, `foam_core`

Without physical groups the mesh still reads, but region IDs are incomplete and
the converted SG is not semantically correct.

A common failure is partitioning geometry in CAD without carrying the region
meaning onto the final analysis cells. What matters is the tag on the cells the
solver will use.

## 3. Supply Materials, Orientation and the Section Plane

A bare `.msh` carries no materials, ply angles, model selection, or solver
flags, so `sgio.read(..., file_format='gmsh')` refuses it:

```text
IncompleteModelDataError: ... carries mesh data only. Building a structure
gene also needs material and section data; read an SG manifest that
references the mesh (file_format='sg_manifest').
```

The mesh travels with an **SG manifest** (`*.sg.json`) that references it:

```{mermaid}
flowchart LR
    MAN["section.sg.json<br/><i>sgdim, model type, model space<br/>materials, sections, config</i>"]
    MSH["section.msh<br/><i>nodes, elements<br/>physical groups<br/>element_local_csys</i>"]
    SG(["StructureGene"])
    OUT["VABS / SwiftComp<br/>input"]

    MAN -- "model_file" --> MSH
    MAN --> SG
    MSH --> SG
    SG -- "sgio.write" --> OUT
```

A minimal manifest — one material, one section per physical group, matched by
`name`. A 2D section embedded in 3D coordinates needs `model_space` to say which
plane it lies in:

```json
{
  "sg_manifest_version": 1,
  "model_file": {"path": "section.msh", "format": "gmsh"},
  "sgdim": 2,
  "model_type": "BM2",
  "model_space": "xy",
  "materials": [
    {"name": "glass", "model": "sd1", "isotropy": 0, "elastic": {"e": 50.0e9, "nu": 0.25}}
  ],
  "sections": [
    {"name": "skin", "material": "glass", "orientation": 0.0}
  ]
}
```

The whole conversion is then one call, from Python or the CLI:

```python
import sgio

sgio.convert('section.sg.json', 'section.sg', 'sg_manifest', 'vabs')
```

```bash
sgio convert section.sg.json section.sg -ff sg_manifest -tf vabs
```

A structure gene read from any format can be written as a Gmsh mesh with its
manifest, so the round trip needs no hand authoring:

```python
sgio.write(sg, 'section.sg.json', 'sg_manifest',
           model_file='section.msh', model_file_format='gmsh')
```

The field-level contract is in {doc}`/ref/sg_manifest`. See
{doc}`/examples/convert_gmsh_to_vabs` and {doc}`/examples/convert_gmsh_to_sc`.

## Choosing a Source of Truth

When geometry comes from external CAD, decide which file owns the SG-specific
data.

| Strategy | Use when |
|---|---|
| **Solver input is canonical** — CAD + Gmsh for the mesh, `sgio` generates the final VABS/SwiftComp file and that file is kept | simplest and most robust; most workflows |
| **Manifest is canonical** — `.sg.json` plus its `.msh` kept together and version-controlled as a unit | mesh generation stays external and you want a Gmsh-centered source of truth |

Either way the mesh alone is never the source of truth: materials, orientation,
model choice, and solver flags live outside it.

## Checklist

- mesh dimension matches the intended SG dimension
- analysis element types supported by the target solver
- physical groups defined on analysis cells
- every analysis physical group has a matching manifest section
- 2D section plane known and set as the manifest `model_space`
- `model_type` matches the intended structural model

## Typical Failure Modes

| Symptom | Likely cause |
|---|---|
| All regions collapse into one material | no physical groups; groups on geometry entities but not on analysis cells; manifest section names do not match the physical group names |
| Section orientation is wrong | wrong `model_space` |
| Mesh looks fine in Gmsh, solver input unusable | unsupported cell types; mixed boundary and analysis entities; wrong `sgdim` / `model_type` |

## See Also

- {doc}`sg` — what a correct SG must contain
- {doc}`/ref/sg_manifest` — the SG manifest contract
- {doc}`/ref/sg_on_gmsh` — the `.msh` field layout
- {doc}`convert` — conversion API and CLI
