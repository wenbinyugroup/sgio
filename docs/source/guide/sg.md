# The Structure Gene

{class}`sgio.StructureGene` is the in-memory object every format is read into
and written from. It composes a finite-element core with SG-specific analysis
settings.

```{mermaid}
flowchart TB
    SG["<b>StructureGene</b><br/><i>sgdim, smdim, spdim</i>"]

    CFG["<b>SGAnalysisConfig</b><br/>analysis, physics, model<br/>geo_correct, do_damping<br/>force_flag, steer_flag"]
    FE["<b>FEModel</b><br/>name, extras"]

    MESH["<b>SGMesh</b><br/>points, cells<br/>point_data, cell_data<br/>point_sets, cell_sets"]
    MAT["<b>materials</b><br/>dict[name, MaterialModel]"]
    SEC["<b>sections</b><br/>dict[name, Section]"]
    ORI["<b>orientations</b><br/>dict[name, Orientation]"]

    SG --> CFG
    SG --> FE
    FE --> MESH
    FE --> SEC
    FE --> MAT
    FE --> ORI

    SEC -. "material" .-> MAT
    SEC -. "property_id" .-> MESH
```

A {class}`sgio.Section` is the join: it names one material, carries an
orientation angle, and binds to the mesh elements tagged with its
`property_id`. That chain — element to section to material — is what turns a
mesh into an analysis model.

## What Makes a Correct SG

A file is not a correct Structure Gene just because `sgio` can read or write
it. A correct SG carries enough information for the target solver to interpret
the geometry, the mesh topology, the material regions, the material properties,
and the structural model assumptions.

Six things must be present.

### 1. Geometry and mesh

Nodal coordinates, element connectivities, a consistent geometry dimension
(`sgdim`), and element types the target solver supports. VABS cross-sections
are 2D section meshes; SwiftComp may be 1D, 2D, or 3D.

Isolated nodes, unsupported element types, or mixed dimensions make the
converted SG incomplete.

### 2. Material-region assignment

Every analysis element belongs to one region, each region ID maps to one
section, and each section maps to one material and one orientation definition.

Without this mapping `sgio` may still produce a file, but the result is a mesh
container, not an analysis model.

### 3. Material definitions

Every material name referenced by a section must exist, and the material model
must contain the properties the target solver requires — isotropic elastic
constants, orthotropic engineering constants, density, or thermal data as the
solver setup needs.

### 4. Section orientation

Laminated and anisotropic regions need an in-plane orientation per material
region, stored through sections. For isotropic regions the angle may be zero
everywhere; for composites, omitting orientation usually makes the model
physically wrong even when conversion succeeds.

Per-element local frames live in `mesh.cell_data['element_local_csys']`. See
{doc}`/ref/sg_on_gmsh` for the field layout.

### 5. Structural model selection

The SG must match the intended model — `BM1`, `BM2`, `PL1`, `PL2`, or `SD1`.
This selection controls how the same mesh is interpreted. A valid mesh with the
wrong model type is still the wrong SG. See {doc}`model/index`.

### 6. Section plane

For a 2D section embedded in 3D coordinates, `model_space` tells `sgio` which
plane (`xy`, `yz`, `zx`) the coordinates lie in. A wrong plane produces a
geometrically inconsistent SG even when every node and element is present.

### Checklist

- mesh dimension matches the intended solver model
- all analysis elements have valid region IDs
- every region ID resolves to a material section
- every referenced material is defined
- orientation data present where anisotropy matters
- section plane / model space explicitly correct

## Format Notes

- **Gmsh** is primarily a mesh carrier. It needs region IDs and external
  material definitions to become a correct SG — see {doc}`gmsh`.
- **VABS** requires a 2D section mesh and a beam model (`BM1` or `BM2`).
- **SwiftComp** accepts 1D/2D/3D SGs, but still requires consistent region and
  material data.
