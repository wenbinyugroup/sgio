(ref_formats)=
# Formats and Model Types

Lookup tables for the identifiers passed to {func}`sgio.read`,
{func}`sgio.write`, and {func}`sgio.convert`.

## File Formats

| `file_format` | Versions | Dimension | Notes |
|---|---|---|---|
| `vabs` | 4.0, 4.1 | 2D | cross-sectional analysis; beam models only |
| `swiftcomp`, `sc` | 2.1, 2.2 | 1D, 2D, 3D | general structure gene analysis |
| `abaqus` | — | 2D, 3D | `.inp` import; materials, sets, `*Orientation`, `*Expansion` |
| `gmsh` | 2.2, 4.1 | 1D, 2D, 3D | mesh carrier; see {doc}`sg_on_gmsh` |
| `sg_manifest` | 1 | 1D, 2D, 3D | `*.sg.json` referencing one model file; see {doc}`sg_manifest` |
| `vtk`, `vtu` | — | any | write only; mesh-only export for ParaView |

Abaqus `*Orientation` support is limited to rectangular systems, defined by
direct six/nine-value coordinates or by an element distribution, applied to the
section's element set. Other Abaqus orientation systems raise `ValueError`
rather than being interpreted as rectangular.

An element distribution may keep its rows in an external file through
`*Distribution, Input=`, as TexGen decks do. The file is resolved relative to
the `.inp` file's own folder.

Abaqus `*Expansion` is read as the material's coefficient of thermal
expansion: the default (isotropic) form and `type=ORTHO`. `type=ANISO` raises
`ValueError` — Abaqus orders its shear terms differently from the internal
Voigt vector, so it is rejected rather than silently reordered. A material
without `*Expansion` simply has no CTE, which only matters for a thermoelastic
analysis.

A layup angle is read from a composite section's ply rows. An ordinary
`*Solid Section` / `*Shell Section` data line holds thickness, not an angle, so
those sections use 0 degrees.

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

## Omega

A SwiftComp input ends with `omega`, the SG's measure over the dimensions it
shares with the macro structural model. SwiftComp divides by it to average the
SG, so a wrong value scales every effective property.

`sgio` computes it from the SG bounding box when `sg.omega` is `None`, which is
the default. The number of shared dimensions is `sgdim + smdim - 3`, and they
are the SG's first coordinates — SwiftComp describes a 3D SG with
$y_1, y_2, y_3$, a 2D SG with $y_2, y_3$ and a 1D SG with $y_3$, while the
macro model spans $y_1, y_2, y_3$ (3D), $y_1, y_2$ (plate/shell) or $y_1$
(beam).

| SG \ Model | `SD1` | `PL1`, `PL2` | `BM1`, `BM2` |
|---|---|---|---|
| 3D | volume | in-plane area | length along the beam axis |
| 2D | area | in-plane length | 1.0 |
| 1D | length | 1.0 | not applicable |

The computed value is only the fallback. The value written is, in order of
precedence:

1. the `omega` argument of {func}`sgio.write`, {func}`sgio.convert`, or
   `--omega` of `sgio convert`;
2. `sg.omega`, set by the `omega` argument of {func}`sgio.read`, by reading a
   SwiftComp input (which carries its own omega), or by assignment;
3. the bounding box, as above.

`omega` must be positive, and it applies to SwiftComp output only; passing it
when writing another format raises `ValueError`. A SG that is degenerate along
a shared dimension raises `ValueError` too, as it would make SwiftComp divide
by zero.

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
