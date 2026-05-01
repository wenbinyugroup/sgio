# Convert SG Data

One of the main capabilities of SGIO is to convert SG data between different
formats. This can be done using the {func}`sgio.convert` function (API) or the
`sgio convert` command (CLI).

## Overview

SGIO supports conversion between:

- **VABS** ↔ **SwiftComp** ↔ **Abaqus** ↔ **Gmsh**
- Mesh-only conversions for visualization
- Format version conversions, such as VABS 4.0 → 4.1

## Basic Usage

### API Method

```python
import sgio

sgio.convert(
    file_name_in='input.inp',
    file_name_out='output.sg',
    file_format_in='abaqus',
    file_format_out='vabs',
    model_type='BM2'
)
```

### CLI Method

```bash
sgio convert input.inp output.sg -ff abaqus -tf vabs -m BM2
```

### Common Parameters

- `file_name_in`: Input file path
- `file_name_out`: Output file path
- `file_format_in`: Input format (`vabs`, `swiftcomp`, `abaqus`, `gmsh`)
- `file_format_out`: Output format
- `model_type`: Structural model (`BM1`, `BM2`, `PL1`, `PL2`, `SD1`)
- `mesh_only`: Convert mesh data only (default: `False`)
- `renum_node`: Renumber nodes (default: `False`)
- `renum_elem`: Renumber elements (default: `False`)


