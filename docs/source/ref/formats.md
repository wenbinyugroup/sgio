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
| `sg_manifest` | 1 | 1D, 2D, 3D | `*.sg.json` referencing one model file; see {doc}`sg_manifest` |
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

For a 1D or 2D SG embedded in 3D coordinates, `model_space` names the mesh axes
the SG lies along: `x`/`y`/`z` or `xy`/`yz`/`zx`. It is given when reading and
stored on the SG as `sg.model_space`; writers project coordinates from it. VABS
and SwiftComp inputs define it themselves (`yz` for 2D, `z` for 1D).

## Conversion Matrix

| From \ To | VABS | SwiftComp | Abaqus | Gmsh |
|---|---|---|---|---|
| VABS | ✓ | ✓ | ✓ | ✓ |
| SwiftComp | ✓ | ✓ | ✓ | ✓ |
| Abaqus | ✓ | ✓ | ✓ | ✓ |
| Gmsh | ✓* | ✓* | ✓* | ✓ |

\* Through an SG manifest, which supplies the materials; see
{doc}`sg_manifest`.

## Supported Analysis Cells

| Dimension | Cell types |
|---|---|
| 2D | `triangle`, `triangle6`, `quad`, `quad8`, `quad9` |
| 3D | solid cells matching the target SwiftComp model |

`vertex` and `line` entities may exist in the source file but are not analysis
elements; they are filtered out on export.
