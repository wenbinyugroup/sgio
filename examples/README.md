# SGIO Examples

This directory contains example scripts demonstrating how to use the SGIO (Structure Gene I/O) package for various tasks.

---

## Quick Start

### Prerequisites

Make sure you have SGIO installed:
```bash
pip install sgio
# or if using uv in development
uv pip install -e .
```

### Running Examples

Navigate to the examples directory and run any example script:
```bash
cd examples
python read_vabs_input.py
```

---

## Example Categories

### Basic I/O Operations

#### Reading Files
- **`read_vabs_input.py`** - Read VABS input files
- **`read_vabs_output_h.py`** - Read VABS homogenized output (beam properties)
- **`read_vabs_output_d.py`** - Read VABS dehomogenization output (local stress/strain)

#### Writing and Converting Files
- **`convert_mesh_data_vabs2gmsh.py`** - Convert VABS mesh to Gmsh format for visualization

#### Model Creation
- **`create_beam_model.py`** - Create structural models programmatically using Pydantic classes
  - Demonstrates Euler-Bernoulli (BM1) and Timoshenko (BM2) beam models
  - Shows model validation and property access patterns
- **`load_cauchy_material_from_json/`** - Build a `CauchyContinuumModel` from serialized JSON material data
  - Highlights the renamed solid model API and assignment validation

### Format Conversion

#### Abaqus to VABS
- **`convert_abaqus_cs_to_vabs/`** - Convert Abaqus cross-section to VABS input
  - Demonstrates both API and CLI approaches
  - Includes sample Abaqus `.inp` file

#### Abaqus to SwiftComp
- **`convert_abaqus_sg3d_to_sc/`** - Convert 3D structure gene from Abaqus to SwiftComp
  - Shows 3D solid model conversion
  - Includes sample cube geometry

### Visualization
- **`plot_cs.py`** - Plot cross-section with beam properties overlay

---

## Example Structure

### Standalone Scripts
Simple Python scripts that can be run directly:
```python
import sgio

# Read a file
sg = sgio.read('file.sg', 'vabs')

# Process data
# ...

# Write output
sgio.write(sg, 'output.sg', 'vabs')
```

### Directory-Based Examples
More complex examples organized in subdirectories:
```
convert_abaqus_cs_to_vabs/
├── README.rst          # Detailed documentation
├── run.py              # Main script
├── sg2_airfoil.inp     # Input file
└── sg2_airfoil.sg      # Output file (generated)
```

---

## Common Patterns

### Pattern 1: Read and Inspect
```python
import sgio

# Read structure gene data
sg = sgio.read('cross_section.sg', 'vabs', model_type='BM2')

# Inspect the data
print(f"Number of nodes: {len(sg.mesh.points)}")
print(f"Number of elements: {len(sg.mesh.cells)}")
```

### Pattern 2: Convert Between Formats
```python
import sgio

# Method 1: One-step conversion
sgio.convert(
    'input.inp',      # Input file
    'output.sg',      # Output file
    'abaqus',         # Input format
    'vabs',           # Output format
    model_type='bm2'  # Timoshenko beam model
)

# Method 2: Two-step conversion (read then write)
sg = sgio.read('input.inp', 'abaqus', model_type='bm2')
sgio.write(sg, 'output.sg', 'vabs')
```

### Pattern 3: Read Output and Visualize
```python
import sgio

# Read mesh
sg = sgio.read('cross_section.sg', 'vabs')

# Read output state (stress/strain)
state_cases = sgio.readOutputState(
    'cross_section.sg',
    'vabs',
    analysis='d',
    extension='ele',
    sg=sg
)

# Add data to mesh for visualization
state_case = state_cases[0]
sgio.addCellDictDataToMesh(
    dict_data=state_case.getState('esm').data,
    name=['S11', 'S12', 'S13', 'S22', 'S23', 'S33'],
    mesh=sg.mesh
)

# Export for visualization
sgio.write(sg, 'output.msh', 'gmsh')
```

---

## Test Data

Example input files are located in:
- `examples/files/` - Sample data files
- `examples/convert_*/` - Example-specific data

For more comprehensive test data, see the test suite:
- `tests/fixtures/` - Organized test data by format
- `tests/files/` - Legacy test data (being migrated)

---

## Related Documentation

- **API Reference**: See `docs/source/ref/` for detailed API documentation
- **User Guide**: See `docs/source/guide/` for conceptual guides
- **Test Suite**: See `tests/README.md` for testing patterns and fixtures

---

## Command Line Interface (CLI)

Many operations can also be performed via CLI:

### Convert Files
```bash
sgio convert input.inp output.sg -ff abaqus -tf vabs -m bm2
```

### Common CLI Options
- `-ff, --from-format`: Input file format (vabs, swiftcomp, abaqus, gmsh)
- `-tf, --to-format`: Output file format
- `-m, --model`: Structural model (bm1, bm2, pl1, pl2, sd1)
- `--mesh-only`: Convert mesh data only (no material properties)

For complete CLI documentation:
```bash
sgio --help
sgio convert --help
```

---

## Tips

1. **File Paths**: Use absolute paths or paths relative to your working directory
2. **Model Types**: 
   - `bm1`: Euler-Bernoulli beam (classical beam theory)
   - `bm2`: Timoshenko beam (includes shear deformation)
   - `pl1`: Kirchhoff-Love plate
   - `pl2`: Reissner-Mindlin plate
   - `sd1`: Cauchy continuum (3D solid)
3. **Error Handling**: Check that input files exist before running conversions
4. **Visualization**: Use Gmsh or ParaView to visualize `.msh` output files

---

## Contributing Examples

When adding new examples:
1. Follow the existing naming conventions
2. Include docstrings and comments
3. Add a README if creating a directory-based example
4. Test your example before committing
5. Update this README with your new example

