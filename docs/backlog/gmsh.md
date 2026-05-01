# Gmsh Format Guide

SGIO uses the [Gmsh 4.1 `.msh` format](https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format)
as its portable mesh exchange format. This page explains the full `.msh`
structure that SGIO writes and reads, including two custom blocks—`$SGLayerDef`
and `$SGConfig`—that carry the layer definitions and solver flags that are not
part of standard Gmsh.

---

## File structure overview

A complete SGIO-flavoured `.msh` file looks like this:

```text
$MeshFormat … $EndMeshFormat
$PhysicalNames … $EndPhysicalNames     ← layer ID → human-readable name
$Entities   … $EndEntities
$Nodes      … $EndNodes
$Elements   … $EndElements
$ElementData "node_id"         … $EndElementData
$ElementData "element_id"      … $EndElementData
$ElementData "property_id"     … $EndElementData   ← element → layer mapping
$ElementData "property_ref_csys" … $EndElementData ← optional orientation
$SGLayerDef … $EndSGLayerDef           ← layer_id, material_id, fiber_angle
$SGConfig   … $EndSGConfig             ← solver flags (sgdim, model, …)
```

Gmsh silently ignores any `$…` block it does not recognise, so the file
remains fully compatible with the Gmsh GUI and other Gmsh-aware tools.

---

## Standard blocks

### `$PhysicalNames`

Each layer gets a physical group whose tag equals the `property_id` used in
`$ElementData property_id`. The group name takes the form `"layer_{id}"`:

```text
$PhysicalNames
2
2 1 "layer_1"
2 2 "layer_2"
$EndPhysicalNames
```

The dimension field (first column) equals the SG dimension (`sgdim`).

### `$ElementData property_id`

The element-to-layer mapping is stored as a per-element scalar field:

```text
$ElementData
1
"property_id"
1
0.0
3
0
1
<num_elements>
1  1
2  1
3  2
…
$EndElementData
```

This approach keeps the layer assignment flexible: multiple element types and
mesh entities can share the same layer without requiring topology changes.

### `$ElementData property_ref_csys`

When elements have a local reference coordinate system (e.g., for beam
cross-section orientations), SGIO writes a second `$ElementData` block:

```text
$ElementData
1
"property_ref_csys"
1
0.0
3
0
1
<num_elements>
1  0.0
2  45.0
…
$EndElementData
```

---

## Custom SGIO blocks

### `$SGLayerDef`

This block records the layer definitions: which material each layer references
and the fiber orientation angle.

```text
$SGLayerDef
! nlayers
2
! layer_id  material_id  fiber_angle
1  1  0.0
2  1  45.0
$EndSGLayerDef
```

| Field | Description |
|---|---|
| `layer_id` | Property ID (matches `$ElementData property_id` and `$PhysicalNames` tag) |
| `material_id` | Numeric material ID (matches the `"id"` field in the materials JSON) |
| `fiber_angle` | In-plane fiber orientation angle in degrees |

Lines beginning with `!` are comments and are ignored by the reader.

### `$SGConfig`

Solver flags that control how VABS or SwiftComp analyses the model.

```text
$SGConfig
! key  value
sgdim       2
model       1
do_damping  0
thermal     0
$EndSGConfig
```

| Key | Description |
|---|---|
| `sgdim` | SG geometry dimension (1, 2, or 3) |
| `model` | Macroscopic structural sub-model (0 = classical, 1 = refined/Timoshenko) |
| `do_damping` | Enable damping computation (0 or 1) |
| `thermal` | Physics flag (0 = elastic, 1 = thermoelastic) |

---

## Material properties file

Material elastic properties are **not** embedded in the `.msh` file. They live
in a companion JSON file (by convention `materials.json`) alongside the `.msh`.
Each material entry must include an `"id"` field that matches the
`material_id` values in `$SGLayerDef`.

```json
[
  {
    "id": 1,
    "name": "carbon_fiber",
    "isotropy": 1,
    "density": 1600.0,
    "e1": 135e9,
    "e2": 10e9,
    "e3": 10e9,
    "g12": 5e9,
    "g13": 5e9,
    "g23": 3.5e9,
    "nu12": 0.3,
    "nu13": 0.3,
    "nu23": 0.4
  }
]
```

---

## Converting to and from Gmsh

### VABS / SwiftComp → Gmsh

Use {func}`sgio.convert` to produce a self-contained `.msh` file:

```python
import sgio

sgio.convert(
    file_name_in='cross_section.sg',
    file_name_out='cross_section.msh',
    file_format_in='vabs',
    file_format_out='gmsh',
    file_version_in='4.1',
    file_version_out='4.1',
    model_type='BM2',
)
```

Equivalent CLI command:

```bash
sgio convert cross_section.sg cross_section.msh \
    -ff vabs -tf gmsh -fv 4.1 -tv 4.1 -m BM2
```

The converter:

1. Reads layer definitions from `sg.mocombos` and writes them to `$SGLayerDef`.
2. Writes solver flags (`sgdim`, `model`, `do_damping`, `thermal`) to `$SGConfig`.
3. Writes `$PhysicalNames` with `"layer_{id}"` names for each layer.
4. Writes the element-to-layer mapping in `$ElementData property_id`.

### Gmsh → VABS / SwiftComp

When reading back, SGIO restores the full model from the custom blocks:

```python
import sgio

# Read the .msh (layer defs and configs are restored automatically)
sg = sgio.read(
    filename='cross_section.msh',
    file_format='gmsh',
    sgdim=2,
    model_type='BM2',
)

# Load material properties from the companion JSON
sgio.read_materials_from_json(sg, 'materials.json')

# Write VABS input
sgio.write(sg, 'cross_section_out.sg', file_format='vabs', model_type='BM2')
```

Data restored from the `.msh`:

| Source block | Restored field |
|---|---|
| `$ElementData property_id` | `sg.mesh.cell_data['property_id']` |
| `$SGLayerDef` | `sg.mocombos` (`{layer_id: (material_name, angle)}`) |
| `$SGConfig sgdim` | `sg.sgdim` |
| `$SGConfig model` | `sg.model` |
| `$SGConfig do_damping` | `sg.do_damping` |
| `$SGConfig thermal` | `sg.physics` |

---

## Creating a Gmsh input file by hand

If you mesh your cross-section directly in Gmsh, you only need to create
physical groups and the companion `materials.json`. SGIO will derive sensible
defaults for `$SGLayerDef` from `$PhysicalNames` and `$ElementData property_id`.

### Minimum viable `.msh`

```text
$MeshFormat
4.1 0 8
$EndMeshFormat
$PhysicalNames
1
2 1 "matrix"
$EndPhysicalNames
$Entities
0 0 1 0
1  0 -0.5 -0.5  0 0.5 0.5  1 1  0
$EndEntities
$Nodes
…
$EndNodes
$Elements
…
$EndElements
```

Assign your material entities to the physical group in Gmsh:

```text
Physical Surface("matrix") = {1};
```

Then read with:

```python
sg = sgio.read('mesh.msh', 'gmsh', sgdim=2, model_type='BM2')
sgio.read_materials_from_json(sg, 'materials.json')
```

SGIO maps the physical group name `"matrix"` to `material_name_id_pairs` and
populates `mocombos` with a default fiber angle of `0.0`. If you need
non-zero fiber angles, add a `$SGLayerDef` block to the `.msh` or set
`sg.mocombos` programmatically before writing.

---

## Summary of data ownership

| Data | Location |
|---|---|
| Node coordinates and connectivity | `.msh` — `$Nodes` / `$Elements` |
| Element → layer assignment | `.msh` — `$ElementData property_id` |
| Layer → material + fiber angle | `.msh` — `$SGLayerDef` |
| Human-readable layer names | `.msh` — `$PhysicalNames` |
| Solver flags | `.msh` — `$SGConfig` |
| Material elastic properties | `materials.json` (separate file) |
