(custom_mesh_conversion)=
# Converting from Custom Format

This page shows a complete, production-ready example of converting mesh data
from a custom format to StructureGene.

## Overview

This example demonstrates:

- Reading mesh data from a custom format
- Mapping original node IDs to array indices
- Grouping elements by type
- Creating mocombos from unique material/angle combinations
- Validation before writing
- Error handling

## Example Custom Format

Assume your custom format has this structure:

```python
{
    'nodes': {
        node_id: [x, y, z],
        ...
    },
    'elements': [
        {
            'id': element_id,
            'type': 'TRIA3' | 'QUAD4' | 'TETRA4' | 'HEXA8',
            'connectivity': [node_id1, node_id2, ...],
            'material': material_name,
            'angle': rotation_angle
        },
        ...
    ],
    'materials': {
        material_name: {
            'E': youngs_modulus,
            'nu': poisson_ratio,
            'rho': density
        },
        ...
    }
}
```

## Complete Conversion Function

Here's a reusable conversion function with validation:

```python
import numpy as np
from meshio import Mesh, CellBlock
from sgio import StructureGene
from sgio.model import CauchyContinuumModel
import sgio


def convert_custom_to_sgio(mesh_data, sgdim=2, name='converted_mesh'):
    """Convert custom mesh format to StructureGene.

    Parameters
    ----------
    mesh_data : dict
        Dictionary with 'nodes', 'elements', and 'materials' keys
    sgdim : int
        Structure dimension (1, 2, or 3)
    name : str
        Name for the structure

    Returns
    -------
    StructureGene
        Populated StructureGene object ready for export

    Raises
    ------
    ValueError
        If mesh data is invalid or incomplete
    """
    # Validate input
    required_keys = ['nodes', 'elements', 'materials']
    for key in required_keys:
        if key not in mesh_data:
            raise ValueError(f"Missing required key: '{key}'")

    if not mesh_data['nodes']:
        raise ValueError("No nodes defined")
    if not mesh_data['elements']:
        raise ValueError("No elements defined")
    if not mesh_data['materials']:
        raise ValueError("No materials defined")

    # Create StructureGene
    sg = StructureGene(name=name, sgdim=sgdim, smdim=sgdim)
    print(f"Creating StructureGene: {name} (sgdim={sgdim})")

    # Convert materials
    print(f"\nConverting {len(mesh_data['materials'])} materials...")
    for mat_name, props in mesh_data['materials'].items():
        material = CauchyContinuumModel(
            name=mat_name,
            isotropy=2,  # Assume isotropic; adjust as needed
            e=props['E'],
            nu=props['nu'],
            density=props['rho']
        )
        sg.materials[mat_name] = material
        print(f"  + {mat_name}: E={props['E']/1e9:.1f} GPa")

    # Build node ID mapping: original_id -> array index
    node_ids = sorted(mesh_data['nodes'].keys())
    node_id_to_index = {nid: idx for idx, nid in enumerate(node_ids)}
    print(f"\nMapping {len(node_ids)} nodes (ID range: {min(node_ids)}-{max(node_ids)})")

    # Create points array
    points = np.array([mesh_data['nodes'][nid] for nid in node_ids])

    # Element type mapping from custom format to meshio
    type_map = {
        'TRIA3': 'triangle',
        'QUAD4': 'quad',
        'TETRA4': 'tetra',
        'HEXA8': 'hexahedron',
        'LINE2': 'line',
    }

    # Build mocombos: collect unique (material, angle) combinations
    print(f"\nProcessing {len(mesh_data['elements'])} elements...")
    mocombo_map = {}  # (material, angle) -> property_id
    next_property_id = 1

    for elem in mesh_data['elements']:
        key = (elem['material'], elem['angle'])
        if key not in mocombo_map:
            mocombo_map[key] = next_property_id
            sg.mocombos[next_property_id] = key
            next_property_id += 1

    print(f"Created {len(sg.mocombos)} material-orientation combinations:")
    for prop_id, (mat, angle) in sg.mocombos.items():
        print(f"  Property {prop_id}: {mat} @ {angle}°")

    # Group elements by type
    elements_by_type = {}
    for elem in mesh_data['elements']:
        elem_type = elem['type']
        if elem_type not in type_map:
            raise ValueError(f"Unsupported element type: {elem_type}")

        meshio_type = type_map[elem_type]
        if meshio_type not in elements_by_type:
            elements_by_type[meshio_type] = []
        elements_by_type[meshio_type].append(elem)

    print(f"\nElement types found:")
    for etype, elems in elements_by_type.items():
        print(f"  {etype}: {len(elems)} elements")

    # Create cells and cell_data
    cells = []
    property_ids = []
    element_ids = []

    for elem_type, elems in elements_by_type.items():
        connectivity = []
        props = []
        elem_ids = []

        for elem in elems:
            # CRITICAL: Map original node IDs to 0-based array indices
            try:
                conn = [node_id_to_index[nid] for nid in elem['connectivity']]
            except KeyError as e:
                raise ValueError(
                    f"Element {elem['id']} references undefined node ID: {e}"
                )
            connectivity.append(conn)

            # Get property_id for this material/angle combination
            prop_id = mocombo_map[(elem['material'], elem['angle'])]
            props.append(prop_id)
            elem_ids.append(elem['id'])

        # Create cell block
        cells.append(CellBlock(type=elem_type, data=np.array(connectivity)))
        property_ids.append(np.array(props))
        element_ids.append(np.array(elem_ids))

    # Assemble mesh
    sg.mesh = Mesh(
        points=points,
        cells=cells,
        cell_data={
            'property_id': property_ids,
            'element_id': element_ids
        },
        point_data={
            'node_id': node_ids  # Preserve original IDs
        }
    )

    print(f"\nStructureGene created successfully:")
    print(f"  Nodes: {sg.nnodes}")
    print(f"  Elements: {sg.nelems}")
    print(f"  Materials: {len(sg.materials)}")
    print(f"  Property combos: {len(sg.mocombos)}")

    return sg


def validate_structure_gene(sg):
    """Validate StructureGene before writing.

    Parameters
    ----------
    sg : StructureGene
        Structure to validate

    Returns
    -------
    bool
        True if valid, False otherwise
    """
    print("\n" + "="*60)
    print("Validating StructureGene")
    print("="*60)

    is_valid = True

    # Check basic configuration
    if sg.sgdim not in [1, 2, 3]:
        print(f"✗ Invalid sgdim: {sg.sgdim}")
        is_valid = False
    else:
        print(f"✓ sgdim = {sg.sgdim}")

    # Check mesh exists
    if sg.mesh is None:
        print(f"✗ No mesh defined")
        is_valid = False
    else:
        print(f"✓ Mesh: {sg.nnodes} nodes, {sg.nelems} elements")

    # Check materials
    if not sg.materials:
        print(f"✗ No materials defined")
        is_valid = False
    else:
        print(f"✓ Materials defined: {list(sg.materials.keys())}")

    # Check mocombos
    if not sg.mocombos:
        print(f"✗ No mocombos defined")
        is_valid = False
    else:
        print(f"✓ {len(sg.mocombos)} mocombos defined")

    if not is_valid:
        return False

    # Check all property IDs reference valid mocombos
    print("\nChecking property IDs...")
    for i, prop_array in enumerate(sg.mesh.cell_data['property_id']):
        unique_props = np.unique(prop_array)
        for prop_id in unique_props:
            if prop_id not in sg.mocombos:
                print(f"✗ Block {i}: undefined property_id {prop_id}")
                is_valid = False

    if is_valid:
        print("✓ All property IDs valid")

    # Check all mocombos reference valid materials
    print("\nChecking material references...")
    for prop_id, (mat_name, angle) in sg.mocombos.items():
        if mat_name not in sg.materials:
            print(f"✗ Property {prop_id} references undefined material '{mat_name}'")
            is_valid = False

    if is_valid:
        print("✓ All material references valid")

    print("="*60)
    if is_valid:
        print("✓ Validation PASSED")
    else:
        print("✗ Validation FAILED")
    print("="*60)

    return is_valid
```

## Usage Example

Here's how to use the conversion function:

```python
# Simulate reading your custom format
# In practice, replace this with actual file parsing
mesh_data = {
    'nodes': {
        100: [0.0, 0.0, 0.0],
        101: [1.0, 0.0, 0.0],
        102: [1.0, 1.0, 0.0],
        103: [0.0, 1.0, 0.0],
        104: [0.5, 0.5, 0.0],
    },
    'elements': [
        {'id': 1000, 'type': 'TRIA3', 'connectivity': [100, 101, 104],
         'material': 'Steel', 'angle': 0.0},
        {'id': 1001, 'type': 'TRIA3', 'connectivity': [101, 102, 104],
         'material': 'Steel', 'angle': 0.0},
        {'id': 1002, 'type': 'TRIA3', 'connectivity': [102, 103, 104],
         'material': 'Aluminum', 'angle': 0.0},
        {'id': 1003, 'type': 'TRIA3', 'connectivity': [103, 100, 104],
         'material': 'Aluminum', 'angle': 0.0},
    ],
    'materials': {
        'Steel': {'E': 200e9, 'nu': 0.3, 'rho': 7850},
        'Aluminum': {'E': 70e9, 'nu': 0.33, 'rho': 2700},
    }
}

# Convert
try:
    sg = convert_custom_to_sgio(
        mesh_data=mesh_data,
        sgdim=2,
        name='my_structure'
    )

    # Validate
    if validate_structure_gene(sg):
        # Write to file
        sgio.write(
            sg=sg,
            fn='my_structure.sc',
            file_format='swiftcomp',
            format_version='2.1',
            model_type='PL1'
        )
        print("\n✓ Successfully written to my_structure.sc")
    else:
        print("\n✗ Validation failed - not writing file")

except Exception as e:
    print(f"\n✗ Conversion failed: {e}")
```

### Expected Output

```text
Creating StructureGene: my_structure (sgdim=2)

Converting 2 materials...
  + Steel: E=200.0 GPa
  + Aluminum: E=70.0 GPa

Mapping 5 nodes (ID range: 100-104)

Processing 4 elements...
Created 2 material-orientation combinations:
  Property 1: Steel @ 0.0°
  Property 2: Aluminum @ 0.0°

Element types found:
  triangle: 4 elements

StructureGene created successfully:
  Nodes: 5
  Elements: 4
  Materials: 2
  Property combos: 2

============================================================
Validating StructureGene
============================================================
✓ sgdim = 2
✓ Mesh: 5 nodes, 4 elements
✓ Materials defined: ['Steel', 'Aluminum']
✓ 2 mocombos defined

Checking property IDs...
✓ All property IDs valid

Checking material references...
✓ All material references valid
============================================================
✓ Validation PASSED
============================================================

✓ Successfully written to my_structure.sc
```

## Handling Different Material Types

If your materials have different symmetries, adjust the isotropy:

```python
def convert_material(mat_data):
    """Convert material data with symmetry detection."""
    mat_name = mat_data['name']

    # Check if orthotropic
    if 'E1' in mat_data and 'E2' in mat_data:
        return CauchyContinuumModel(
            name=mat_name,
            isotropy=0,  # Orthotropic
            e=[mat_data['E1'], mat_data['E2'], mat_data['E3']],
            g=[mat_data['G12'], mat_data['G13'], mat_data['G23']],
            nu=[mat_data['nu12'], mat_data['nu13'], mat_data['nu23']],
            density=mat_data['rho']
        )
    # Isotropic
    else:
        return CauchyContinuumModel(
            name=mat_name,
            isotropy=2,  # Isotropic
            e=mat_data['E'],
            nu=mat_data['nu'],
            density=mat_data['rho']
        )
```

## Next Steps

- For troubleshooting common issues, see {ref}`custom_mesh_troubleshooting`
- For data structure details, see {ref}`custom_mesh_data_structures`
- For a simpler starting point, see {ref}`custom_mesh_quickstart`

