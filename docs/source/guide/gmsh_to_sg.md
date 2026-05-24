# Prepare a Gmsh Mesh for SG Conversion

```{important}
This page is a workflow guide, not the normative SG serialization contract.

The single normative specification is {doc}`sg_on_gmsh_spec`.

Any content on this page that describes `$SGLayerDef`, `$SGConfig`,
`property_ref_csys`, or `property_id` as canonical should be read as legacy or
transitional guidance until the implementation finishes migrating to the new
specification.
```

This page explains what a `.msh` file should contain if you want to convert it
correctly into a Structure Gene input for:

- `SwiftComp`
- `VABS`

The key distinction is:

- a mesh that is merely readable by `sgio`,
- versus a mesh that carries enough information to become a physically correct
  SG model.

## Minimum Requirements

To convert a Gmsh mesh into a useful SG model, the input should contain:

- nodal coordinates,
- supported analysis element types,
- element-wise material-region identifiers,
- consistent model dimension,
- and, outside the `.msh` file if needed, material definitions for all regions.

If region IDs or materials are missing, conversion may still produce an output
file, but the result is usually only a mesh-shaped placeholder.

## 1. Use the Correct Analysis Dimension

Choose the mesh dimension to match the target SG.

### For VABS

VABS input is a 2D cross-section model.
Your Gmsh mesh should therefore represent a section, not a full 3D volume.

Recommended settings:

- `sgdim=2`
- `model_type='BM1'` or `model_type='BM2'`

### For SwiftComp

SwiftComp supports multiple SG dimensions:

- `sgdim=1` for line-like models,
- `sgdim=2` for plate/shell or beam cross-sections,
- `sgdim=3` for solid RVEs or 3D structure genes.

Recommended examples:

- `model_type='BM1'` / `'BM2'` for beam cross-sections,
- `model_type='PL1'` / `'PL2'` for plates/shells,
- `model_type='SD1'` for 3D solids.

## 2. Ensure the Mesh Contains Supported Analysis Cells

The mesh should contain cells that the target solver can actually use.

### For VABS

Use section elements such as:

- triangle,
- triangle6,
- quad,
- quad8,
- quad9.

Boundary entities such as `vertex` and `line` may exist in the Gmsh file, but
they are not analysis elements for VABS.
`sgio` filters them out during VABS export.

### For SwiftComp

Use element types appropriate for the target SG dimension and solver model.
For example:

- 2D section meshes for beam or plate models,
- 3D solid elements for `SD1`.

Do not rely on lower-dimensional boundary entities to define material regions
for higher-dimensional analysis cells.

## 3. Define Physical Groups for Material Regions

This is the most important Gmsh-specific requirement.

A correct `.msh` file should define physical groups for the analysis elements.
Those physical tags become the region identifiers used by `sgio`.

Why this matters:

- `sgio` maps Gmsh physical tags to `property_id`,
- `property_id` is how SG regions are tracked,
- and region IDs are what later connect elements to materials and orientations.

If no physical groups are present:

- `sgio` may still read the mesh,
- but region IDs are incomplete or fallback-generated,
- and the converted SG is usually not semantically correct.

Recommended practice:

- create one physical group per material region,
- apply the physical group to the actual analysis cells,
- and use stable, meaningful names.

Examples of good physical-group names:

- `matrix`
- `skin_0deg`
- `web_glass`
- `foam_core`

## 3A. Minimal `.msh` Template

The following is a schematic Gmsh 4.1 ASCII template for a 2D cross-section
mesh with two material regions.

It is not meant to be a full real mesh file you can run as-is.
Its purpose is to show:

- which data belong in which block,
- where region tags are stored,
- and how node and element connectivity are arranged.

```text
$MeshFormat
4.1 0 8
$EndMeshFormat

$PhysicalNames
2
2 101 "skin"
2 102 "core"
$EndPhysicalNames

$Entities
4 4 2 0
1 0 0 0 0
2 1 0 0 0
3 1 1 0 0
4 0 1 0 0
1 0 0 0 1 0 0 0 2 1 -2
2 1 0 0 1 1 0 0 2 2 -3
3 0 1 0 1 1 0 0 2 4 -3
4 0 0 0 0 1 0 0 2 1 -4
1 0 0 0 0.5 1 0 1 101 4 1 2 3 4
2 0.5 0 0 1 1 0 1 102 4 1 2 3 4
$EndEntities

$Nodes
2 6 1 6
2 1 0 3
1
2
5
0.0 0.0 0.0
0.5 0.0 0.0
0.5 1.0 0.0
2 2 0 3
3
4
6
0.5 0.0 0.0
1.0 0.0 0.0
1.0 1.0 0.0
$EndNodes

$Elements
2 2 1 2
2 1 2 1
1 1 2 5
2 2 5 3
2 2 2 1
2 3 4 6
$EndElements
```

### How to read this template

#### `$PhysicalNames`

This block defines the names of physical groups:

- `2 101 "skin"` means: dimension `2`, physical tag `101`, name `skin`
- `2 102 "core"` means: dimension `2`, physical tag `102`, name `core`

For a 2D cross-section mesh, the important physical groups are usually
dimension-2 groups because the analysis cells are surface elements.

#### `$Entities`

This block defines geometric entities and attaches physical tags to them.

In the example:

- surface entity `1` carries physical tag `101`
- surface entity `2` carries physical tag `102`

This is the key place where region meaning is assigned.
Later, the element blocks in `$Elements` refer to these surface entity tags.

For SG conversion, the important rule is:

- in 2D, put material-region physical tags on surface entities
- in 3D, put material-region physical tags on volume entities

Point and curve entities may exist, but they are usually not where material
regions should be defined.

#### `$Nodes`

This block stores node IDs and coordinates.

The layout is:

1. one header line for the whole block
2. one header line per entity block
3. node tags for that entity block
4. coordinates for those node tags

In the example:

- nodes `1`, `2`, `5` belong to surface entity `1`
- nodes `3`, `4`, `6` belong to surface entity `2`

Important points:

- node tags do not need to be contiguous in the source file
- coordinates are always written as `x y z`
- for a 2D section in the `xy` plane, `z` is usually `0`

#### `$Elements`

This block stores analysis elements and their connectivities.

The layout is:

1. one header line for the whole block
2. one header line per entity block:
   `entityDim entityTag elementType numElementsInBlock`
3. one line per element:
   `elementTag node1 node2 ...`

In the example:

- `2 1 2 1` means:
  - entity dimension = `2`
  - entity tag = `1`
  - element type = `2` (`triangle`)
  - number of elements in this block = `1`
- the next line `1 1 2 5` means:
  - element tag = `1`
  - connectivity = nodes `1, 2, 5`

Because this element belongs to entity `1`, it inherits the physical meaning
of that entity, which is physical tag `101` and name `skin`.

This is exactly the chain `sgio` needs:

- physical group name and tag in `$PhysicalNames`
- physical tag attached to entity in `$Entities`
- element attached to entity in `$Elements`

### Ordering Rules

For stable conversion, keep the following consistent:

- node IDs in `$Nodes` must match the node IDs used in `$Elements`
- each element block in `$Elements` should contain elements of one entity and
  one element type
- use Gmsh's standard node ordering for each element type

Typical examples:

- triangle: `n1 n2 n3`
- triangle6: `n1 n2 n3 n4 n5 n6`
- quad: `n1 n2 n3 n4`

Do not invent your own connectivity ordering.
Use the ordering written by Gmsh itself.

### What changes for a 3D SwiftComp mesh

For a 3D solid mesh, the same idea applies, but the material-region physical
tags should be attached to volume entities instead of surface entities.

So the practical shift is:

- `$PhysicalNames`: use dimension `3` groups for material regions
- `$Entities`: assign those physical tags to volumes
- `$Elements`: use 3D solid element blocks attached to those volume entities

The mapping logic remains the same.

## 3B. How Element Local Coordinate Systems Are Stored

For anisotropic materials, layered sections, or any case where element
orientation matters, mesh topology alone is not enough.
You also need element local coordinate data.

Inside `sgio`, the canonical per-element local coordinate field is:

- `mesh.cell_data["property_ref_csys"]`

Its value is a 9-component payload per element:

- `(a1, a2, a3, b1, b2, b3, c1, c2, c3)`

where:

- `c` is the local origin,
- `a - c` defines local axis `y1`,
- `b - c` lies in the local `y1-y2` plane,
- and the local system is reconstructed as a right-handed basis.

This is the SGIO-internal representation used when writing `VABS` or
`SwiftComp`.

### How `vabs -> gmsh` is written by `sgio`

When `sgio` writes a Gmsh file from an existing SG, it preserves local
coordinate information in element data.

In practice, the `.msh` file written by `sgio` contains:

- `property_ref_csys`
  - a 9-component `$ElementData` field
- `property_ref_axis_y1`
  - a 3-component `$ElementData` field
- `property_ref_axis_y2`
  - a 3-component `$ElementData` field
- `property_ref_axis_y3`
  - a 3-component `$ElementData` field

The axis fields are mainly for inspection and visualization.
The canonical field for SG round-trip use is still `property_ref_csys`.

So, if a `.msh` file was produced by `sgio`, it already contains the element
local coordinate data needed for later conversion back to solver input.

### How `gmsh -> vabs` should be done

There are two different cases.

#### Case 1: the `.msh` file was written by `sgio`

This is the easy round-trip case.
The file already contains SG-specific element data and custom blocks, so:

```python
import sgio

sg = sgio.read(
    filename="section.msh",
    file_format="gmsh",
    sgdim=2,
    model_type="BM2",
)

sgio.write(
    sg=sg,
    filename="section.sg",
    file_format="vabs",
    format_version="4.1",
    model_type="BM2",
    model_space="xy",
)
```

or directly:

```python
import sgio

sgio.convert(
    file_name_in="section.msh",
    file_name_out="section.sg",
    file_format_in="gmsh",
    file_format_out="vabs",
    sgdim=2,
    model_type="BM2",
    model_space="xy",
)
```

This works because the `.msh` already carries:

- region IDs,
- SG layer definitions,
- SG analysis config,
- and element local coordinate data.

#### Case 2: the `.msh` file was created in external CAD + Gmsh

This is the common industrial workflow, but here the plain `.msh` file usually
does **not** contain full SG semantics.

Gmsh itself can give you:

- nodes,
- elements,
- physical groups,
- and geometry classification.

But it usually does **not** automatically provide:

- `property_ref_csys`,
- ply angles or region orientation,
- solver model selection,
- or constitutive material properties.

So the correct workflow is:

1. generate geometry in CAD,
2. mesh it in Gmsh,
3. define physical groups for analysis regions,
4. read the mesh into `sgio`,
5. attach missing SG data in Python,
6. then write to `VABS` or `SwiftComp`.

Example:

```python
import numpy as np
import sgio
from sgio.core.property_ref_csys import vabs_theta_to_property_ref_csys

sg = sgio.read(
    filename="section_from_gmsh.msh",
    file_format="gmsh",
    sgdim=2,
    model_type="BM2",
)

# Add constitutive materials
mat_skin = sgio.CauchyContinuumModel(name="skin")
mat_skin.set_isotropy(0)
mat_skin.set_elastic([50.0e9, 0.25])
sg.materials["skin"] = mat_skin

mat_core = sgio.CauchyContinuumModel(name="core")
mat_core.set_isotropy(0)
mat_core.set_elastic([5.0e9, 0.30])
sg.materials["core"] = mat_core

# Map region IDs to material names and region angles
sg.mocombos[101] = ("skin", 45.0)
sg.mocombos[102] = ("core", 0.0)

# Optional: attach element-wise local coordinate systems directly
for block_index, prop_ids in enumerate(sg.mesh.cell_data["property_id"]):
    block_csys = []
    for prop_id in prop_ids:
        theta = 45.0 if int(prop_id) == 101 else 0.0
        block_csys.append(vabs_theta_to_property_ref_csys(theta))
    sg.mesh.cell_data.setdefault("property_ref_csys", [])
    sg.mesh.cell_data["property_ref_csys"].append(np.asarray(block_csys, dtype=float))

sgio.write(
    sg=sg,
    filename="section_vabs.sg",
    file_format="vabs",
    format_version="4.1",
    model_type="BM2",
    model_space="xy",
)
```

If orientation is constant per material region, filling `sg.mocombos` is often
enough.
If orientation varies element by element, you should provide
`mesh.cell_data["property_ref_csys"]` explicitly.

## 3C. How to Preserve Full SG Information

If users build geometry in external CAD and only use Gmsh for meshing, the
important design decision is: what file is the source of truth for SG-specific
data?

### What a plain Gmsh file can preserve well

A `.msh` file is a good carrier for:

- mesh geometry,
- connectivity,
- physical region IDs,
- point data,
- element data,
- and SGIO custom blocks if the file was written by `sgio`.

### What a plain Gmsh file is usually not good at authoring

A plain external Gmsh workflow is usually not the best place to author:

- constitutive materials,
- laminate definitions,
- solver flags,
- beam/plate model assumptions,
- and rich SG metadata.

### Recommended strategies

#### Strategy 1: solver input is the canonical SG artifact

For many workflows, the cleanest approach is:

- use CAD + Gmsh only for geometry and mesh,
- then use `sgio` to generate the final `VABS` or `SwiftComp` input,
- and treat that solver input as the canonical SG file.

This is the simplest and most robust option.

#### Strategy 2: Gmsh + sidecar metadata

If you want Gmsh to remain the central mesh carrier, keep:

- one `.msh` file for geometry and region tags,
- one sidecar JSON/YAML file for materials, region angles, model type, and
  analysis config.

Then reconstruct the `StructureGene` in Python before writing solver input.

This is usually the best choice when geometry/mesh generation is external.

#### Strategy 3: let `sgio` re-export the enriched mesh

After you enrich the mesh with SG metadata in Python, you can write it back out
through `sgio` to a new `.msh`.

That SG-enriched `.msh` can preserve:

- physical groups,
- `$SGLayerDef`,
- `$SGConfig`,
- `property_ref_csys`,
- and local-axis element data.

This is the best option when you want a Gmsh-based file that can round-trip
inside the `sgio` ecosystem.

## 4. Provide Material Definitions for All Regions

A `.msh` file alone usually does not contain full constitutive material data.
So in most workflows, you must provide materials separately and ensure they
match the physical-group or section names.

At minimum:

- every material region used in the mesh must have a material definition,
- and the material definition must satisfy the target solver.

Typical workflow:

1. Build the mesh in Gmsh with physical groups.
2. Read the mesh into `sgio`.
3. Add materials to the `StructureGene`.
4. Convert or write to `SwiftComp` or `VABS`.

## 5. Set the Section Plane Explicitly for 2D Cross-Sections

If the mesh is a 2D section embedded in 3D coordinates, you must know which
plane it lies in.

Typical options:

- `xy`
- `yz`
- `zx`

When exporting to solver input, use `model_space` to tell `sgio` how to project
the section coordinates.

Example:

```python
import sgio

sgio.convert(
    file_name_in="section.msh",
    file_name_out="section.sg",
    file_format_in="gmsh",
    file_format_out="vabs",
    sgdim=2,
    model_type="BM2",
    model_space="xy",
)
```

CLI equivalent:

```bash
sgio convert section.msh section.sg -ff gmsh -tf vabs -d 2 -m bm2 -ms xy
```

If your section lies in the `yz` or `zx` plane, pass that plane explicitly.

## 6. Keep Region Semantics on Analysis Cells

A common modeling mistake is to partition geometry visually but forget to carry
region meaning onto the final analysis cells.

For conversion, what matters is not only the CAD partitioning, but that the
final mesh cells used for analysis have:

- the right physical tag,
- the right dimension,
- and the intended material-region meaning.

## 7. Understand What the `.msh` File Does Not Usually Store

A Gmsh mesh may describe geometry and region tags, but it usually does not
fully describe:

- elastic constants,
- thermal properties,
- damping data,
- laminate orientation angles,
- beam-model choice,
- or solver analysis flags.

These are SG-level data and often must be supplied through `sgio` after reading
the mesh.

## Recommended Checklist

Before converting Gmsh to `SwiftComp` or `VABS`, verify:

- the mesh dimension matches the intended SG dimension,
- analysis element types are supported by the target solver,
- physical groups are defined on analysis cells,
- every physical region has a corresponding material definition,
- 2D section plane is known and passed through `model_space`,
- and the chosen `model_type` matches the intended structural model.

## Typical Failure Modes

### The file converts, but all regions collapse into one material

Likely causes:

- no physical groups,
- physical groups assigned to geometry entities but not final analysis cells,
- or materials were never attached after reading the mesh.

### The VABS file is generated, but the section orientation is wrong

Likely cause:

- wrong `model_space`.

### The mesh looks fine in Gmsh, but the solver input is unusable

Likely causes:

- unsupported cell types for the target solver,
- mixed boundary and analysis entities,
- missing material definitions,
- or wrong `sgdim` / `model_type`.

## See Also

- {doc}`sg`
- {doc}`convert`
- {doc}`io`
