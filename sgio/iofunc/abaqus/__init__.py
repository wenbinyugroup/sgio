from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np

from ...core.mesh import SGMesh
from .._helpers import register_format

# Register the format
register_format(
    "abaqus",
    [".inp"],
    reader=read,
    writer=write
)

__all__ = ["read", "write"]


def read(filename: Union[str, Path], **kwargs) -> SGMesh:
    """Read an Abaqus input file.
    
    This is an example implementation that extends the meshio reader
    to handle SG-specific data.
    
    Args:
        filename: Path to the file to read
        **kwargs: Additional arguments to pass to the reader
        
    Returns:
        SGMesh object
    """
    from meshio.abaqus import read as meshio_read
    
    # Use meshio to read the basic mesh data
    meshio_mesh = meshio_read(filename, **kwargs)
    
    # Convert to SGMesh
    sg_mesh = SGMesh(
        points=meshio_mesh.points,
        cells=meshio_mesh.cells,
        point_data=meshio_mesh.point_data,
        cell_data=meshio_mesh.cell_data,
        field_data=meshio_mesh.field_data,
        point_sets=meshio_mesh.point_sets,
        cell_sets=meshio_mesh.cell_sets
    )
    
    # Parse the file to extract SG-specific data
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Example: Extract material properties
    current_material = None
    for line in lines:
        line = line.strip()
        if line.startswith('*Material'):
            # Extract material name
            current_material = line.split('=')[1].strip()
        elif line.startswith('*Elastic') and current_material:
            # Extract elastic properties
            parts = line.split(',')
            if len(parts) >= 2:
                youngs_modulus = float(parts[1])
                sg_mesh.add_material_property(current_material, 'youngs_modulus', youngs_modulus)
        elif line.startswith('*Density') and current_material:
            # Extract density
            parts = line.split(',')
            if len(parts) >= 2:
                density = float(parts[1])
                sg_mesh.add_material_property(current_material, 'density', density)
    
    # Example: Extract element-material assignments
    current_element_set = None
    for line in lines:
        line = line.strip()
        if line.startswith('*Elset'):
            # Extract element set name
            parts = line.split(',')
            if len(parts) >= 2:
                current_element_set = parts[1].strip()
        elif line.startswith('*Solid Section') and current_element_set:
            # Extract material assignment
            parts = line.split(',')
            if len(parts) >= 2:
                material = parts[1].strip()
                # Assign material to all elements in the set
                if current_element_set in sg_mesh.cell_sets:
                    for element_id in sg_mesh.cell_sets[current_element_set][0]:
                        sg_mesh.assign_material_to_element(element_id, material)
    
    return sg_mesh


def write(filename: Union[str, Path], mesh: SGMesh, **kwargs) -> None:
    """Write an Abaqus input file.
    
    This is an example implementation that extends the meshio writer
    to handle SG-specific data.
    
    Args:
        filename: Path to the file to write
        mesh: SGMesh object to write
        **kwargs: Additional arguments to pass to the writer
    """
    from meshio.abaqus import write as meshio_write
    
    # First, write the basic mesh data using meshio
    meshio_write(filename, mesh, **kwargs)
    
    # Then, append SG-specific data to the file
    with open(filename, 'a') as f:
        # Write material properties
        for material_id, properties in mesh.material_properties.items():
            f.write(f"*Material, name={material_id}\n")
            
            # Write elastic properties if available
            if 'youngs_modulus' in properties:
                f.write(f"*Elastic, {properties['youngs_modulus']}\n")
            
            # Write density if available
            if 'density' in properties:
                f.write(f"*Density, {properties['density']}\n")
        
        # Write element-material assignments
        # Group elements by material
        material_to_elements = {}
        for element_id, material_id in mesh.element_materials.items():
            if material_id not in material_to_elements:
                material_to_elements[material_id] = []
            material_to_elements[material_id].append(element_id)
        
        # Write element sets and material assignments
        for material_id, element_ids in material_to_elements.items():
            set_name = f"Set_{material_id}"
            f.write(f"*Elset, elset={set_name}\n")
            # Write element IDs in chunks of 16 (Abaqus format)
            for i in range(0, len(element_ids), 16):
                chunk = element_ids[i:i+16]
                f.write(f"{', '.join(map(str, chunk))}\n")
            
            # Write solid section with material assignment
            f.write(f"*Solid Section, elset={set_name}, material={material_id}\n")
            f.write("1.0\n")  # Default thickness 