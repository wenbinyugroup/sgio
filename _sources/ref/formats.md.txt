(ref_formats)=
# Formats and Model Types

Lookup tables for the identifiers passed to {func}`sgio.read`,
{func}`sgio.write`, and {func}`sgio.convert`.

## File Formats

| `file_format` | Versions | Dimension | Notes |
|---|---|---|---|
| `vabs` | 4.0, 4.1 | 2D | cross-sectional analysis; beam models only |
| `swiftcomp`, `sc` | 2.1, 2.2 | 1D, 2D, 3D | general structure gene analysis |
| `abaqus` | — | 2D, 3D | `.inp` import; materials, sets, `*Orientation` |
| `gmsh` | 2.2, 4.1 | 1D, 2D, 3D | mesh carrier; see {doc}`sg_on_gmsh` |
| `vtk`, `vtu` | — | any | write only; mesh-only export for ParaView |

Abaqus `*Orientation` support is limited to rectangular systems, defined by
direct six/nine-value coordinates or by an element distribution, applied to the
section's element set. Other Abaqus orientation systems raise `ValueError`
rather than being interpreted as rectangular.

## Structural Model Types

| `model_type` | Model | Applies to |
|---|---|---|
| `BM1` | Euler-Bernoulli beam | VABS, SwiftComp |
| `BM2` | Timoshenko beam | VABS, SwiftComp |
| `PL1` | Kirchhoff-Love plate/shell | SwiftComp |
| `PL2` | Reissner-Mindlin plate/shell | SwiftComp |
| `SD1` | Cauchy continuum (3D solid) | SwiftComp |

Theory background for each model is in {doc}`/guide/model/index`.

## Model Space

For a 2D section embedded in 3D coordinates, `model_space` names the plane the
section lies in: `xy`, `yz`, or `zx`. It controls how section coordinates are
projected into solver coordinates on write.

## Conversion Matrix

| From \ To | VABS | SwiftComp | Abaqus | Gmsh |
|---|---|---|---|---|
| VABS | ✓ | ✓ | ✓ | ✓ |
| SwiftComp | ✓ | ✓ | ✓ | ✓ |
| Abaqus | ✓ | ✓ | ✓ | ✓ |
| Gmsh | ✓* | ✓* | ✓* | ✓ |

\* Mesh data only unless the sidecar bundle supplies materials; see
{doc}`sg_on_gmsh`.

## Supported Analysis Cells

| Dimension | Cell types |
|---|---|
| 2D | `triangle`, `triangle6`, `quad`, `quad8`, `quad9` |
| 3D | solid cells matching the target SwiftComp model |

`vertex` and `line` entities may exist in the source file but are not analysis
elements; they are filtered out on export.
