# Read Solver Output

A two-scale MSG study runs in two directions. Homogenization condenses the SG
into effective properties for a macroscopic model; dehomogenization takes the
macroscopic response back down to local fields on the SG mesh. `sgio` reads the
output of each.

```{mermaid}
flowchart LR
    SG["Structure Gene<br/><i>mesh + materials</i>"]
    SOLVER["VABS / SwiftComp"]
    K["<b>.k</b> effective<br/>properties"]
    MACRO["Macroscopic<br/>beam / plate / solid<br/>analysis"]
    ELE["<b>.ELE .sn .snm</b><br/>local fields"]

    SG -- "sgio.write" --> SOLVER
    SOLVER -- "homogenization" --> K
    K -- "read_output_model" --> MACRO
    MACRO -- "macro loads" --> SOLVER
    SOLVER -- "dehomogenization" --> ELE
    ELE -- "read_output_state" --> SG
```

Each direction has its own entry point.

| Output | File | Function | Returns |
|---|---|---|---|
| Effective properties | `.k` / `.K` | {func}`sgio.read_output_model` | a structural model ({ref}`ref_model`) |
| Local state fields | `.ELE`, `.sn`, `.snm`, … | {func}`sgio.read_output_state` | a list of {class}`sgio.model.StateCase`, one per load case |

## Effective properties

```python
import sgio

model = sgio.read_output_model('cross_section.sg.K', 'vabs', model_type='BM2')
print(model.ea, model.gj, model.ei22, model.ei33)
```

`model_type` must match the model the solver ran — see {doc}`model/index`.
Named beam properties are direct attributes; use the typed section-query
methods only for matrix or theory-schema quantities.

See {doc}`/examples/read_vabs_output_h`.

## Local state fields

Local strain, stress, displacement, failure index, and strength ratio are read
against an SG that has already been loaded with {func}`sgio.read`, so the
fields can be attached to the mesh and exported for visualization.

```python
import sgio

sg = sgio.read(filename='cross_section.sg', file_format='vabs')
cases = sgio.read_output_state(
    filename='cross_section.sg',
    file_format='vabs',
    analysis='d',       # dehomogenization
    extension='ele',    # element-level data
    sg=sg,
    tool_version='4.1',
)
stress = cases[0].getState('esm').data
```

See {doc}`/examples/read_vabs_output_d` for the VABS walkthrough including
Gmsh export, and {doc}`/examples/read_sc_output_state` for SwiftComp.
