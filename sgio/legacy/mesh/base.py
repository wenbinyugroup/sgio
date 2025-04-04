"""
Base mesh class that extends meshio.Mesh with additional functionality.
"""
from typing import Dict, List, Optional, Union
import numpy as np
import meshio

class SGioMesh(meshio.Mesh):
    """Extended mesh class that inherits from meshio.Mesh.
    
    This class provides additional functionality and custom format support
    while maintaining compatibility with the original meshio.Mesh class.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._custom_data = {}  # Store any additional custom data
        
    @classmethod
    def read(cls, filename: str, file_format: Optional[str] = None, **kwargs) -> 'SGioMesh':
        """Read a mesh from a file.
        
        This method extends meshio's read functionality by:
        1. Supporting custom format implementations
        2. Providing format-specific options
        3. Maintaining backward compatibility
        
        Args:
            filename: Path to the mesh file
            file_format: Optional format specification. If None, will be inferred from filename
            **kwargs: Additional arguments passed to the format-specific reader
            
        Returns:
            SGioMesh: A new mesh instance
        """
        # First try to use custom format implementation if available
        if file_format:
            try:
                from .formats import get_format_reader
                reader = get_format_reader(file_format)
                if reader:
                    return reader(filename, **kwargs)
            except ImportError:
                pass
        
        # Fall back to meshio's default implementation
        mesh = meshio.read(filename, file_format, **kwargs)
        return cls(mesh.points, mesh.cells, 
                  point_data=mesh.point_data,
                  cell_data=mesh.cell_data,
                  field_data=mesh.field_data)
    
    def write(self, filename: str, file_format: Optional[str] = None, **kwargs):
        """Write the mesh to a file.
        
        This method extends meshio's write functionality by:
        1. Supporting custom format implementations
        2. Providing format-specific options
        3. Maintaining backward compatibility
        
        Args:
            filename: Path to write the mesh file
            file_format: Optional format specification. If None, will be inferred from filename
            **kwargs: Additional arguments passed to the format-specific writer
        """
        # First try to use custom format implementation if available
        if file_format:
            try:
                from .formats import get_format_writer
                writer = get_format_writer(file_format)
                if writer:
                    writer(self, filename, **kwargs)
                    return
            except ImportError:
                pass
        
        # Fall back to meshio's default implementation
        super().write(filename, file_format, **kwargs)
    
    def add_custom_data(self, key: str, value: any):
        """Add custom data to the mesh.
        
        Args:
            key: Identifier for the custom data
            value: The data to store
        """
        self._custom_data[key] = value
    
    def get_custom_data(self, key: str) -> any:
        """Retrieve custom data from the mesh.
        
        Args:
            key: Identifier for the custom data
            
        Returns:
            The stored data if it exists, None otherwise
        """
        return self._custom_data.get(key) 