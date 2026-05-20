"""
Example: Creating StructureGene from Custom Mesh Data
======================================================

This example demonstrates how to create a StructureGene object from custom
mesh data and write it to VABS/SwiftComp format.

This is useful when your mesh format is not directly supported by sgio.
"""

import numpy as np
from meshio import Mesh, CellBlock
from sgio import StructureGene
from sgio.model import CauchyContinuumModel
import sgio


def example_simple_triangle_mesh():
    """Example 1: Simple triangular plate mesh."""
    print("=" * 70)
    print("Example 1: Simple Triangular Plate Mesh")
    print("=" * 70)
    
    # Step 1: Create StructureGene with configuration
    sg = StructureGene(
        name='triangle_plate',
        sgdim=2,  # 2D plate analysis
        smdim=2
    )
    
    # Step 2: Define materials
    steel = CauchyContinuumModel(
        name='Steel',
        isotropy=2,  # Isotropic
        e=200e9,
        nu=0.3,
        density=7850
    )
    sg.materials['Steel'] = steel
    
    # Step 3: Define material-orientation combinations
    sg.mocombos = {
        1: ('Steel', 0.0),  # Property ID 1: Steel at 0 degrees
    }
    
    # Step 4: Create mesh
    # Define 4 nodes forming a square
    points = np.array([
        [0.0, 0.0, 0.0],  # Node 0
        [1.0, 0.0, 0.0],  # Node 1
        [1.0, 1.0, 0.0],  # Node 2
        [0.0, 1.0, 0.0],  # Node 3
    ])
    
    # Define 2 triangular elements (splitting the square diagonally)
    cells = [
        CellBlock(
            type='triangle',
            data=np.array([
                [0, 1, 2],  # Triangle 1: bottom-right
                [0, 2, 3],  # Triangle 2: top-left
            ])
        )
    ]
    
    # Assign properties to elements
    cell_data = {
        'property_id': [
            np.array([1, 1])  # Both elements use mocombo 1 (Steel at 0°)
        ]
    }
    
    # Assemble mesh
    sg.mesh = Mesh(
        points=points,
        cells=cells,
        cell_data=cell_data
    )
    
    # Step 5: Print summary
    print(f"\nStructure: {sg.name}")
    print(f"  Dimension: {sg.sgdim}D")
    print(f"  Nodes: {sg.nnodes}")
    print(f"  Elements: {sg.nelems}")
    print(f"  Materials: {len(sg.materials)}")
    
    # Step 6: Write to SwiftComp format
    output_file = 'triangle_plate.sc'
    sgio.write(
        sg=sg,
        fn=output_file,
        file_format='swiftcomp',
        format_version='2.1',
        model_type='PL1'  # 2D plate, classical model
    )
    print(f"\n✓ Written to {output_file}")


def example_composite_laminate():
    """Example 2: Composite laminate with multiple materials and orientations."""
    print("\n" + "=" * 70)
    print("Example 2: Composite Laminate with Multiple Orientations")
    print("=" * 70)
    
    # Create StructureGene
    sg = StructureGene(
        name='composite_laminate',
        sgdim=2,
        smdim=2
    )
    
    # Define orthotropic carbon fiber material
    carbon = CauchyContinuumModel(
        name='CarbonFiber',
        isotropy=0,  # Orthotropic
        e=[135e9, 10e9, 10e9],      # E1, E2, E3 (Pa)
        g=[5e9, 5e9, 5e9],           # G12, G13, G23 (Pa)
        nu=[0.3, 0.3, 0.45],         # nu12, nu13, nu23
        density=1600
    )
    sg.materials['CarbonFiber'] = carbon
    
    # Define material-orientation combinations for layup [0/45/-45/90]
    sg.mocombos = {
        1: ('CarbonFiber', 0.0),     # 0° ply
        2: ('CarbonFiber', 45.0),    # +45° ply
        3: ('CarbonFiber', -45.0),   # -45° ply
        4: ('CarbonFiber', 90.0),    # 90° ply
    }
    
    # Create a 2x2 mesh with quad elements (4 elements total)
    points = np.array([
        [0.0, 0.0, 0.0],  # 0
        [0.5, 0.0, 0.0],  # 1
        [1.0, 0.0, 0.0],  # 2
        [0.0, 0.5, 0.0],  # 3
        [0.5, 0.5, 0.0],  # 4
        [1.0, 0.5, 0.0],  # 5
        [0.0, 1.0, 0.0],  # 6
        [0.5, 1.0, 0.0],  # 7
        [1.0, 1.0, 0.0],  # 8
    ])
    
    cells = [
        CellBlock(
            type='quad',
            data=np.array([
                [0, 1, 4, 3],  # Element 0: bottom-left
                [1, 2, 5, 4],  # Element 1: bottom-right
                [3, 4, 7, 6],  # Element 2: top-left
                [4, 5, 8, 7],  # Element 3: top-right
            ])
        )
    ]
    
    # Assign different orientations to different elements
    cell_data = {
        'property_id': [
            np.array([1, 2, 3, 4])  # Each element uses different orientation
        ]
    }
    
    sg.mesh = Mesh(points=points, cells=cells, cell_data=cell_data)
    
    # Print summary
    print(f"\nStructure: {sg.name}")
    print(f"  Nodes: {sg.nnodes}")
    print(f"  Elements: {sg.nelems}")
    print(f"  Material orientations:")
    for prop_id, (mat_name, angle) in sg.mocombos.items():
        print(f"    Property {prop_id}: {mat_name} @ {angle}°")
    
    # Write to file
    output_file = 'composite_laminate.sc'
    sgio.write(
        sg=sg,
        fn=output_file,
        file_format='swiftcomp',
        format_version='2.1',
        model_type='PL1'
    )
    print(f"\n✓ Written to {output_file}")


def example_custom_format_conversion():
    """Example 3: Converting from a custom mesh format."""
    print("\n" + "=" * 70)
    print("Example 3: Converting from Custom Format")
    print("=" * 70)
    
    # Simulate reading from a custom format
    # In practice, this would be your actual file parsing code
    custom_mesh_data = {
        'nodes': {
            100: [0.0, 0.0, 0.0],
            101: [1.0, 0.0, 0.0],
            102: [1.0, 1.0, 0.0],
            103: [0.0, 1.0, 0.0],
            104: [0.5, 0.5, 0.0],
        },
        'elements': [
            {'id': 1000, 'type': 'TRIA3', 'nodes': [100, 101, 104], 
             'material': 'Aluminum', 'angle': 0.0},
            {'id': 1001, 'type': 'TRIA3', 'nodes': [101, 102, 104], 
             'material': 'Aluminum', 'angle': 0.0},
            {'id': 1002, 'type': 'TRIA3', 'nodes': [102, 103, 104], 
             'material': 'Steel', 'angle': 0.0},
            {'id': 1003, 'type': 'TRIA3', 'nodes': [103, 100, 104], 
             'material': 'Steel', 'angle': 0.0},
        ],
        'materials': {
            'Aluminum': {'E': 70e9, 'nu': 0.33, 'rho': 2700},
            'Steel': {'E': 200e9, 'nu': 0.3, 'rho': 7850},
        }
    }
    
    # Convert to StructureGene
    sg = convert_custom_format(custom_mesh_data, sgdim=2)
    
    # Print summary with validation
    print(f"\nStructure: {sg.name}")
    print(f"  Nodes: {sg.nnodes}")
    print(f"  Elements: {sg.nelems}")
    print(f"  Materials: {len(sg.materials)}")
    
    print(f"\nMaterials defined:")
    for mat_name, mat in sg.materials.items():
        print(f"  {mat_name}: E={mat.e/1e9:.0f} GPa, nu={mat.nu}, rho={mat.density} kg/m³")
    
    print(f"\nProperty combinations:")
    for prop_id, (mat_name, angle) in sg.mocombos.items():
        print(f"  {prop_id}: {mat_name} @ {angle}°")
    
    # Validate: Check that all property IDs are defined
    print(f"\nValidation:")
    is_valid = True
    for i, prop_array in enumerate(sg.mesh.cell_data['property_id']):
        for elem_idx, prop_id in enumerate(prop_array):
            if prop_id not in sg.mocombos:
                print(f"  ✗ ERROR: Element {elem_idx} in block {i} uses undefined property {prop_id}")
                is_valid = False
    
    if is_valid:
        print(f"  ✓ All property IDs are valid")
        
        # Check that all materials in mocombos are defined
        for prop_id, (mat_name, angle) in sg.mocombos.items():
            if mat_name not in sg.materials:
                print(f"  ✗ ERROR: Property {prop_id} references undefined material '{mat_name}'")
                is_valid = False
    
    if is_valid:
        print(f"  ✓ All materials are defined")
        
        # Write to file
        output_file = 'custom_converted.sc'
        sgio.write(
            sg=sg,
            fn=output_file,
            file_format='swiftcomp',
            format_version='2.1',
            model_type='PL1'
        )
        print(f"\n✓ Written to {output_file}")
    else:
        print(f"\n✗ Validation failed - cannot write file")


def convert_custom_format(mesh_data, sgdim=2):
    """Convert custom mesh format to StructureGene.
    
    Parameters
    ----------
    mesh_data : dict
        Dictionary with 'nodes', 'elements', and 'materials' keys
    sgdim : int
        Structure dimension (1, 2, or 3)
        
    Returns
    -------
    StructureGene
        Populated structure gene object
    """
    # Create StructureGene
    sg = StructureGene(name='converted_mesh', sgdim=sgdim, smdim=sgdim)
    
    # Convert materials
    for mat_name, props in mesh_data['materials'].items():
        material = CauchyContinuumModel(
            name=mat_name,
            isotropy=2,  # Assume isotropic
            e=props['E'],
            nu=props['nu'],
            density=props['rho']
        )
        sg.materials[mat_name] = material
    
    # Build node ID mapping: original_id -> array index
    node_ids = sorted(mesh_data['nodes'].keys())
    node_id_to_index = {nid: idx for idx, nid in enumerate(node_ids)}
    
    # Create points array
    points = np.array([mesh_data['nodes'][nid] for nid in node_ids])
    
    # Element type mapping
    type_map = {
        'TRIA3': 'triangle',
        'QUAD4': 'quad',
        'TETRA4': 'tetra',
        'HEXA8': 'hexahedron',
    }
    
    # Build mocombos: map (material, angle) -> property_id
    mocombo_map = {}
    next_property_id = 1
    
    for elem in mesh_data['elements']:
        key = (elem['material'], elem['angle'])
        if key not in mocombo_map:
            mocombo_map[key] = next_property_id
            sg.mocombos[next_property_id] = key
            next_property_id += 1
    
    # Group elements by type
    elements_by_type = {}
    for elem in mesh_data['elements']:
        elem_type = type_map[elem['type']]
        if elem_type not in elements_by_type:
            elements_by_type[elem_type] = []
        elements_by_type[elem_type].append(elem)
    
    # Create cells and cell_data
    cells = []
    property_ids = []
    element_ids = []
    
    for elem_type, elems in elements_by_type.items():
        connectivity = []
        props = []
        elem_ids = []
        
        for elem in elems:
            # IMPORTANT: Convert original node IDs to 0-based array indices
            conn = [node_id_to_index[nid] for nid in elem['nodes']]
            connectivity.append(conn)
            
            # Get property_id for this material/angle combination
            prop_id = mocombo_map[(elem['material'], elem['angle'])]
            props.append(prop_id)
            elem_ids.append(elem['id'])
        
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
            'node_id': node_ids  # Preserve original node IDs
        }
    )
    
    return sg


def example_3d_tetrahedral_mesh():
    """Example 4: 3D solid with tetrahedral elements."""
    print("\n" + "=" * 70)
    print("Example 4: 3D Tetrahedral Solid Mesh")
    print("=" * 70)
    
    # Create StructureGene
    sg = StructureGene(
        name='cube_tetra',
        sgdim=3,  # 3D solid
        smdim=3
    )
    
    # Define isotropic material
    concrete = CauchyContinuumModel(
        name='Concrete',
        isotropy=2,
        e=30e9,
        nu=0.2,
        density=2400
    )
    sg.materials['Concrete'] = concrete
    sg.mocombos = {1: ('Concrete', 0.0)}
    
    # Create unit cube mesh with tetrahedral elements
    # 8 corner nodes
    points = np.array([
        [0.0, 0.0, 0.0],  # 0
        [1.0, 0.0, 0.0],  # 1
        [1.0, 1.0, 0.0],  # 2
        [0.0, 1.0, 0.0],  # 3
        [0.0, 0.0, 1.0],  # 4
        [1.0, 0.0, 1.0],  # 5
        [1.0, 1.0, 1.0],  # 6
        [0.0, 1.0, 1.0],  # 7
    ])
    
    # Divide cube into 5 tetrahedra
    # (This is one possible decomposition)
    cells = [
        CellBlock(
            type='tetra',
            data=np.array([
                [0, 1, 2, 4],  # Tetra 1
                [1, 2, 5, 6],  # Tetra 2
                [2, 4, 6, 7],  # Tetra 3
                [0, 2, 3, 4],  # Tetra 4
                [2, 3, 4, 7],  # Tetra 5
            ])
        )
    ]
    
    cell_data = {
        'property_id': [np.array([1, 1, 1, 1, 1])]  # All use property 1
    }
    
    sg.mesh = Mesh(points=points, cells=cells, cell_data=cell_data)
    
    # Print summary
    print(f"\nStructure: {sg.name}")
    print(f"  Dimension: {sg.sgdim}D")
    print(f"  Nodes: {sg.nnodes}")
    print(f"  Elements: {sg.nelems}")
    print(f"  Element type: tetrahedron")
    print(f"  Material: {list(sg.materials.keys())[0]}")
    
    # Write to SwiftComp
    output_file = 'cube_tetra.sc'
    sgio.write(
        sg=sg,
        fn=output_file,
        file_format='swiftcomp',
        format_version='2.1',
        model_type='SD1'  # 3D solid, classical model
    )
    print(f"\n✓ Written to {output_file}")


if __name__ == '__main__':
    # Run all examples
    example_simple_triangle_mesh()
    example_composite_laminate()
    example_custom_format_conversion()
    example_3d_tetrahedral_mesh()
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
