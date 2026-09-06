# Read and Write SG Data

Every format goes through one in-memory object. {func}`sgio.read` loads a
solver or mesh file into a {class}`sgio.StructureGene`; {func}`sgio.write`
emits one.

```{mermaid}
flowchart LR
    subgraph IN ["Input"]
        direction TB
        VABS_I["VABS<br/>.sg"]
        SC_I["SwiftComp<br/>.sg"]
        ABQ_I["Abaqus<br/>.inp"]
        GMSH_I["Gmsh bundle<br/>.msh + .json"]
    end

    SG(["StructureGene"])

    subgraph OUT ["Output"]
        direction TB
        VABS_O["VABS<br/>.sg"]
        SC_O["SwiftComp<br/>.sg"]
        ABQ_O["Abaqus<br/>.inp"]
        GMSH_O["Gmsh<br/>.msh"]
        VTK_O["VTK / VTU<br/>.vtk .vtu"]
    end

    VABS_I -- "read" --> SG
    SC_I -- "read" --> SG
    ABQ_I -- "read" --> SG
    GMSH_I -- "read_sg_from_gmsh_bundle" --> SG

    SG -- "write" --> VABS_O
    SG -- "write" --> SC_O
    SG -- "write" --> ABQ_O
    SG -- "write" --> GMSH_O
    SG -- "write" --> VTK_O
```

VTK and VTU are write-only, mesh-only export targets. A bare `.msh` carries no
material data, so Gmsh input is read as a bundle — see {doc}`gmsh`.

{func}`sgio.convert` chains a read and a write in one call; see {doc}`convert`.

## Read

```python
import sgio

sg = sgio.read(
    'airfoil.sg',
    file_format='vabs',
    model_type='BM2',
    format_version='4.1',
)
```

`file_format` and `model_type` identifiers are listed in {doc}`/ref/formats`.
`sgdim` may be omitted when the format implies it — VABS is always 2D — and is
required for formats that do not, such as a 3D Abaqus solid:

```python
sg = sgio.read('cube.inp', file_format='abaqus', model_type='SD1', sgdim=3)
```

## Write

```python
import sgio

sgio.write(sg, 'cross_section.sg', file_format='vabs', format_version='4.1')
```

Node and element IDs are renumbered automatically when the target format
requires it, with a warning.

Pass `mesh_only=True` to write geometry without materials or analysis
configuration — useful for visualization targets:

```python
sgio.write(sg, 'visualization.msh', file_format='gmsh', mesh_only=True)
```

Full signatures are in {ref}`ref_io`.

## See Also

- {doc}`sg` — what the `StructureGene` holds
- {doc}`convert` — format conversion, API and CLI
- {doc}`output` — reading solver output
- {doc}`/ref/formats` — format, model-type, and conversion tables
