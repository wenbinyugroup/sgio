# Load Materials from JSON

This example demonstrates how to load different types of Cauchy continuum materials from JSON files.

## Material Types

The example includes JSON definitions for four different material symmetry types:

### 1. Isotropic Material (`isotropic_steel.json`)
- **Symmetry**: Isotropic (isotropy=0)
- **Material**: Structural Steel
- **Required Constants**: 2 (E, nu)
- **Properties**:
  - Young's modulus: 200 GPa
  - Poisson's ratio: 0.3
  - Density: 7850 kg/m³

### 2. Transverse Isotropic Material (`transverse_isotropic_fiber.json`)
- **Symmetry**: Transverse Isotropic (isotropy=3)
- **Material**: UD Carbon Fiber T300/5208
- **Required Constants**: 5 (E1, E2, G12, nu12, nu23)
- **Properties**:
  - Longitudinal modulus: 150 GPa
  - Transverse modulus: 10 GPa
  - Shear modulus: 5 GPa
  - Density: 1600 kg/m³

### 3. Orthotropic Material (`orthotropic_composite.json`)
- **Symmetry**: Orthotropic (isotropy=1)
- **Material**: Woven Glass/Epoxy
- **Required Constants**: 9 (E1, E2, E3, G12, G13, G23, nu12, nu13, nu23)
- **Properties**:
  - Three Young's moduli: 25, 24, 10 GPa
  - Three shear moduli: 4.0, 3.5, 3.0 GPa
  - Three Poisson's ratios: 0.16, 0.3, 0.35
  - Density: 1800 kg/m³

### 4. Anisotropic Material (`anisotropic_crystal.json`)
- **Symmetry**: Anisotropic (isotropy=2)
- **Material**: Monoclinic Crystal
- **Required Constants**: 21 (upper triangle of 6×6 stiffness matrix)
- **Input Format**: Array of 21 values in order:
  ```
  C11, C12, C13, C14, C15, C16,
       C22, C23, C24, C25, C26,
            C33, C34, C35, C36,
                 C44, C45, C46,
                      C55, C56,
                           C66
  ```
- **Density**: 3200 kg/m³

## Running the Example

From the repository root:

```bash
python examples/load_materials_from_json/run.py
```

Or from the virtual environment:

```bash
.venv/Scripts/python.exe examples/load_materials_from_json/run.py
```

## Example Output

The script will:
1. Load all four material definitions from JSON files
2. Display detailed properties for each material including:
   - Physical properties (density, temperature, specific heat)
   - Elastic constants appropriate for each symmetry type
   - Stiffness matrix components
   - Strength properties
   - Thermal expansion coefficients
3. Compare materials in a summary table
4. Demonstrate JSON serialization

## JSON Structure

All material JSON files follow the same basic structure:

```json
{
  "name": "Material Name",
  "isotropy": 0,
  "density": 7850.0,
  "temperature": 20.0,
  "e1": 200000000000.0,
  "nu12": 0.3,
  "x1t": 400000000.0,
  ...
  "cte": [1.2e-05, 1.2e-05, 1.2e-05, 0.0, 0.0, 0.0],
  "specific_heat": 490.0
}
```

### Key Fields

- `isotropy`: Material symmetry type (0=Isotropic, 1=Orthotropic, 2=Anisotropic, 3=Transverse Isotropic)
- `density`: Material density in kg/m³
- `e1, e2, e3`: Young's moduli in Pa
- `g12, g13, g23`: Shear moduli in Pa
- `nu12, nu13, nu23`: Poisson's ratios
- `anisotropic_constants`: Array of 21 values for anisotropic materials
- `x1t, x2t, x3t`: Tensile strengths in Pa
- `x1c, x2c, x3c`: Compressive strengths in Pa
- `x12, x13, x23`: Shear strengths in Pa
- `cte`: Thermal expansion coefficients (6 components)
- `specific_heat`: Specific heat capacity in J/(kg·K)

## Creating Custom Materials

To create your own material JSON:

1. Copy one of the existing JSON files as a template
2. Modify the properties for your material
3. Ensure you provide the correct number of elastic constants for the symmetry type:
   - Isotropic: `e1` and `nu12`
   - Transverse Isotropic: `e1`, `e2`, `g12`, `nu12`, `nu23`
   - Orthotropic: All 9 engineering constants
   - Anisotropic: `anisotropic_constants` array with 21 values
4. Load using `load_material(Path('your_material.json'))`

## Notes

- All moduli and strengths are in Pascals (Pa) in the JSON files
- The display script converts to GPa/MPa for readability
- The stiffness matrix is automatically computed from engineering constants
- For anisotropic materials, the stiffness matrix is built from the 21 constants ensuring symmetry
