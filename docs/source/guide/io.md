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
        GMSH_I["SG manifest<br/>.sg.json + .msh"]
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
    GMSH_I -- "read" --> SG

    SG -- "write" --> VABS_O
    SG -- "write" --> SC_O
    SG -- "write" --> ABQ_O
    SG -- "write" --> GMSH_O
    SG -- "write" --> VTK_O
```

VTK and VTU are write-only, mesh-only export targets. A bare `.msh` carries no
material data, so Gmsh input is read through an SG manifest — see {doc}`gmsh`.

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
`sgdim`, `model_type` and, for a 1D/2D SG, `model_space` may be omitted only
when the format implies them — a VABS file defines all three. Abaqus input
requires them:

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

A SwiftComp input also needs `omega`, the SG's measure over the dimensions it
shares with the macro model. It is computed from the SG bounding box unless
`sg.omega` is set; see the omega table in {doc}`/ref/formats`. To give it by
hand, pass `omega` to `sgio.read` (stored on the SG) or to `sgio.write` (used
for that write only, leaving `sg` unchanged):

```python
sgio.write(sg, 'weave.sc', file_format='sc', omega=44.54)
```

Writing is atomic: the target file is replaced only once the whole file has
been written, so a failure part way through leaves any existing file intact.

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
