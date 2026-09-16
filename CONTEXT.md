# sgio

sgio reads, writes and converts structure genes (SG) and cross-sections between solver input
formats (VABS, SwiftComp) and general mesh formats (Abaqus, Gmsh).

## Language

### On-disk representation

**SG manifest**:
The JSON document that is the primary on-disk form of one structure gene: SG-level parameters,
sections, analysis config, and a reference to exactly one model file.
_Avoid_: sidecar, bundle, 外挂

**Model file**:
The single file an SG manifest references (`.inp`, `.msh`, `.sc`, `.dat`, ...), holding what
its format can express: a mesh, and possibly materials, sections or a full solver input.
_Avoid_: mesh file, host file, main file, main.msh

**Model space**:
The mapping from a model file's coordinate axes to the SG axes (e.g. `yz` for a cross-section
drawn in the y-z plane).
