# Prepare a Gmsh Mesh for SG Conversion

A `.msh` file that `sgio` can read is not automatically a `.msh` file that
becomes a physically correct SG. This page covers what to author in Gmsh, and
what has to be supplied around it.

The field-level contract is specified in {doc}`/ref/sg_on_gmsh`.

## What the Mesh Must Carry

- nodal coordinates
- analysis element types the target solver supports
- physical groups on the analysis cells, one per material region
- a mesh dimension matching the target SG

Material definitions, orientation angles, model choice, and solver flags are
**not** authored in Gmsh — they are supplied through `sgio` or the sidecar
files of the SG-on-Gmsh bundle.

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

## 3. Supply Materials and Orientation

A bare `.msh` carries no materials, ply angles, model selection, or solver
flags, so `sgio.read(..., file_format='gmsh')` refuses it:

```text
IncompleteModelDataError: ... carries mesh data only. Building a structure
gene also needs section/material data; read the Gmsh bundle with
sgio.read_sg_from_gmsh_bundle(main_msh, sections_json, config_json).
```

The mesh must travel with two sidecar files. Together the three make an
**SG-on-Gmsh bundle**:

```{mermaid}
flowchart LR
    MSH["main.msh<br/><i>nodes, elements<br/>physical groups<br/>element_local_csys</i>"]
    SEC["sections.json<br/><i>materials, orientations</i>"]
    CFG["config.json<br/><i>analysis configuration</i>"]
    SG(["StructureGene"])
    OUT["VABS / SwiftComp<br/>input"]

    MSH --> SG
    SEC --> SG
    CFG --> SG
    SG -- "sgio.write" --> OUT
```

`sections.json` is required; `config.json` is optional and defaults apply
without it. The field-level contract is in {doc}`/ref/sg_on_gmsh`.

```python
import sgio

sg = sgio.read_sg_from_gmsh_bundle(
    main_msh='section.msh',
    sections_json='sections.json',
    config_json='config.json',
    model_type='BM2',
)
sgio.write(sg, 'section.sg', file_format='vabs', model_space='yz')
```

A minimal `sections.json` — one entry per physical group, matched by `name`:

```json
[
  {
    "name": "skin",
    "model": "sd1",
    "isotropy": 0,
    "density": 1000.0,
    "elastic": {"e1": 50.0e9, "nu12": 0.25}
  }
]
```

When a mesh was written by `sgio` it already carries region tags and
`element_local_csys`, so the round trip needs no extra authoring beyond the
sidecars it was exported with.

See {doc}`/examples/convert_gmsh_to_vabs` and
{doc}`/examples/convert_gmsh_to_sc`.

## 4. Set the Section Plane

A 2D section embedded in 3D coordinates needs `model_space` to say which plane
it lies in. {func}`sgio.convert` takes the bundle sidecars too, so the whole
conversion is one call:

```python
sgio.convert(
    file_name_in='section.msh',
    file_name_out='section.sg',
    file_format_in='gmsh',
    file_format_out='vabs',
    sections_json='sections.json',
    config_json='config.json',
    sgdim=2,
    model_type='BM2',
    model_space='xy',
)
```

```{note}
The `sgio convert` CLI has no flag for the sidecar files, so Gmsh **input**
must go through the Python API. The CLI handles Gmsh as an output format
normally.
```

## Choosing a Source of Truth

When geometry comes from external CAD, decide which file owns the SG-specific
data.

| Strategy | Use when |
|---|---|
| **Solver input is canonical** — CAD + Gmsh for the mesh, `sgio` generates the final VABS/SwiftComp file and that file is kept | simplest and most robust; most workflows |
| **Bundle is canonical** — `.msh` plus `sections.json` / `config.json` kept together and version-controlled as a unit | mesh generation stays external and you want a Gmsh-centered source of truth |

Either way the mesh alone is never the source of truth: materials, orientation,
model choice, and solver flags live outside it.

## Checklist

- mesh dimension matches the intended SG dimension
- analysis element types supported by the target solver
- physical groups defined on analysis cells
- every physical group has a matching record in `sections.json`
- 2D section plane known and passed through `model_space`
- `model_type` matches the intended structural model

## Typical Failure Modes

| Symptom | Likely cause |
|---|---|
| All regions collapse into one material | no physical groups; groups on geometry entities but not on analysis cells; `sections.json` names do not match the physical group names |
| Section orientation is wrong | wrong `model_space` |
| Mesh looks fine in Gmsh, solver input unusable | unsupported cell types; mixed boundary and analysis entities; wrong `sgdim` / `model_type` |

## See Also

- {doc}`sg` — what a correct SG must contain
- {doc}`/ref/sg_on_gmsh` — the normative bundle contract
- {doc}`convert` — conversion API and CLI
