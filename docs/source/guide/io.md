# Read and Write SG Data

This guide covers reading and writing Structure Gene (SG) data in various
formats.

## Read SG data

To read SG data from a file, use the {func}`sgio.read` function.

### Basic Usage

```python
import sgio

sg = sgio.read(
    filename='cross_section.sg',
    file_format='vabs',
    model_type='BM2',
)
```

### Parameters

- `filename` (`str`): Path to the SG file to be read
- `file_format` (`str`): Format of the SG file
  - `'vabs'` - VABS format
  - `'sc'` or `'swiftcomp'` - SwiftComp format
  - `'abaqus'` - Abaqus `.inp` format
  - `'gmsh'` - Gmsh mesh format
- `model_type` (`str`, optional): Type of structural model
  - `'BM1'` - Euler-Bernoulli beam (classical beam theory)
  - `'BM2'` - Timoshenko beam (includes shear deformation)
  - `'PL1'` - Kirchhoff-Love plate
  - `'PL2'` - Reissner-Mindlin plate
  - `'SD1'` - Cauchy continuum (3D solid)
- `sgdim` (`int`, optional): Dimension of the SG data (`1`, `2`, or `3`)
  - For VABS cross-sections, dimension is `2` and can be omitted
  - For 3D structure genes, dimension is `3`
- `format_version` (`str`, optional): Version of the file format, such as
  `'4.0'` or `'4.1'` for VABS

### Returns

The function returns a {class}`sgio.StructureGene` object.

### Examples

**Read VABS input file:**

```python
import sgio

# Read VABS 4.1 format file for Timoshenko beam
sg = sgio.read(
    filename='airfoil.sg',
    file_format='vabs',
    model_type='BM2',
    format_version='4.1'
)

print(f"Nodes: {len(sg.mesh.points)}")
print(f"Elements: {len(sg.mesh.cells)}")
```

**Read Abaqus input file:**

```python
import sgio

# Read Abaqus .inp file for 3D solid
sg = sgio.read(
    filename='cube.inp',
    file_format='abaqus',
    model_type='SD1',
    sgdim=3
)
```

## Write SG data

Use the {func}`sgio.write` function to write Structure Gene data to a file.

### Basic Usage

```python
import sgio

sgio.write(
    sg=sg,
    fn='output.sg',
    file_format='vabs',
)
```

### Parameters

- `sg` (`StructureGene`): Structure Gene object to write
- `fn` (`str`): Output file path
- `file_format` (`str`): Output format (`'vabs'`, `'swiftcomp'`, `'gmsh'`, etc.)
- `format_version` (`str`, optional): Version of the output format
- `analysis` (`str`, optional): Analysis type for VABS/SwiftComp
- `mesh_only` (`bool`, optional): Write only mesh data (default: `False`)

### Examples

**Write VABS input file:**

```python
import sgio

# Write to VABS 4.1 format
sgio.write(
    sg=sg,
    fn='cross_section.sg',
    file_format='vabs',
    format_version='4.1'
)
```

**Write to Gmsh for visualization:**

```python
import sgio

# Write mesh to Gmsh format
sgio.write(
    sg=sg,
    fn='visualization.msh',
    file_format='gmsh',
    mesh_only=True
)
```

**Write with automatic format compliance:**

```python
import sgio

# SGIO automatically ensures numbering meets format requirements
sgio.write(
    sg=sg,
    fn='output.sg',
    file_format='vabs'
)
# Node/element IDs are automatically renumbered if needed (with warning)
```

### Write Mesh Data Only

To write only mesh data without material properties:

```python
import sgio

sgio.write(
    sg=sg,
    fn='mesh_only.msh',
    file_format='gmsh',
    mesh_only=True
)
```

## Supported Data Formats

SGIO supports multiple file formats for Structure Gene data.

These formats support full Structure Gene data (mesh + materials + properties):

**VABS**

- Format identifier: `'vabs'`
- Versions: 4.0, 4.1
- Use for: Cross-sectional analysis (2D)
- Models: BM1 (Euler-Bernoulli), BM2 (Timoshenko)

**SwiftComp**

- Format identifier: `'swiftcomp'` or `'sc'`
- Versions: 2.1, 2.2
- Use for: General structure gene analysis (1D, 2D, 3D)
- Models: BM1, BM2, PL1, PL2, SD1

**Abaqus**

- Format identifier: `'abaqus'`
- File extension: `.inp`
- Use for: Import from Abaqus CAE
- Supports: Material properties, element sets, node sets

### Format Conversion Matrix

| From \\ To | VABS | SwiftComp | Abaqus | Gmsh |
|---|---|---|---|---|
| VABS | ✓ | ✓ | ✓ | ✓ |
| SwiftComp | ✓ | ✓ | ✓ | ✓ |
| Abaqus | ✓ | ✓ | ✓ | ✓ |
| Gmsh | ✓* | ✓* | ✓* | ✓ |

\* Mesh data only (materials must be added separately)

### See Also

- {doc}`convert` - Detailed guide on format conversion
- {doc}`io_model` - Reading analysis output (beam properties)
- {doc}`io_state` - Reading state data (stress/strain fields)
- {doc}`/examples/index` - Working code examples
