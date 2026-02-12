# Material JSON Fixtures

This directory contains JSON test fixtures for material model testing. These fixtures provide sample material definitions covering various material types and properties for testing the `CauchyContinuumModel` JSON reading/writing functionality.

## Material Types

### Isotropic Materials
- **`steel_isotropic.json`** - Basic steel material with isotropic properties
  - Name: "Steel"
  - Isotropy: 0
  - E: 200 GPa, ν: 0.3
  - Density: 7850 kg/m³

### Orthotropic Materials
- **`carbon_fiber_orthotropic.json`** - Carbon fiber composite with orthotropic properties
  - Name: "Carbon Fiber"
  - Isotropy: 1
  - E1: 150 GPa, E2: 10 GPa, E3: 10 GPa
  - G12: 5 GPa, G13: 5 GPa, G23: 3 GPa
  - ν12: 0.3, ν13: 0.3, ν23: 0.4
  - Density: 1600 kg/m³

### Transverse Isotropic Materials
- **`ti_composite_transverse.json`** - Titanium composite with transverse isotropy
  - Name: "Ti-Composite"
  - Isotropy: 3
  - E1: 120 GPa, E2: 80 GPa
  - G12: 40 GPa
  - ν12: 0.28, ν23: 0.35
  - Density: 4500 kg/m³

### Anisotropic Materials
- **`custom_anisotropic.json`** - Custom material with explicit stiffness matrix
  - Name: "Custom Material"
  - Isotropy: 2
  - 6×6 stiffness matrix: 1 GPa diagonal
  - Density: 1000 kg/m³

### Special Properties

#### Strength Properties
- **`aluminum_strength.json`** - Aluminum with strength parameters
  - Tensile strength (x1t, x1c): 310 MPa
  - Failure criterion: 1

#### Thermal Properties
- **`steel_thermal.json`** - Steel with thermal properties
  - CTE: [12e-6, 12e-6, 12e-6, 0, 0, 0] 1/K
  - Specific heat: 500 J/(kg·K)

### Multiple Materials

#### Material Collections
- **`multiple_materials.json`** - Three basic isotropic materials (Steel, Aluminum, Titanium)
- **`mixed_isotropy.json`** - Materials with different isotropy types (0, 1, 3)
- **`varying_properties.json`** - Materials with different property sets (basic, strength, thermal)

### Edge Cases

#### Minimal/Empty
- **`empty.json`** - Minimal material with only default values
- **`empty_list.json`** - Empty array `[]`

#### Error Cases
- **`invalid_format.json`** - Invalid format (array instead of object)
- **`invalid_material.json`** - Invalid material parameters (negative E)
- **`not_list.json`** - Single object when list expected
- **`invalid_list.json`** - Array with one invalid material
- **`mixed_types.json`** - Array with mixed types (object, string, object)

## Usage in Tests

These fixtures are used by pytest fixtures defined in `../conftest.py`:

```python
def test_my_material(steel_isotropic_path):
    material = read_material_from_json(steel_isotropic_path)
    assert material.name == "Steel"
```

## Test Coverage

The fixtures provide comprehensive test coverage for:

1. **Material Types**: All isotropy levels (0, 1, 2, 3)
2. **Properties**: Basic elastic, strength, thermal, stiffness matrix
3. **Valid Cases**: Normal material definitions
4. **Error Cases**: Invalid formats, parameters, types
5. **Edge Cases**: Empty materials, minimal properties
6. **Collections**: Single materials, multiple materials, mixed collections

## Data Format

All materials follow the JSON schema expected by `CauchyContinuumModel`:

```json
{
  "name": "Material Name",
  "isotropy": 0|1|2|3,
  "density": number,
  "e": number,           // isotropic (alias for e1)
  "e1": number, "e2": number, "e3": number,
  "g12": number, "g13": number, "g23": number,
  "nu": number,          // isotropic (alias for nu12)
  "nu12": number, "nu13": number, "nu23": number,
  "stff": [[...]],      // 6×6 stiffness matrix
  "x1t": number, ...    // strength properties
  "cte": [...],         // thermal expansion
  "specific_heat": number,
  "failure_criterion": number
}
```

This comprehensive fixture set enables thorough testing of material JSON functionality while maintaining clear, reusable test data.