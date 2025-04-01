"""
Intermediate layer between sgio and meshio for customizing mesh I/O functionality.
"""
from __future__ import annotations

import meshio
from meshio._files import is_buffer
from meshio._exceptions import ReadError
from meshio._helpers import _read_buffer as meshio_read_buffer
from meshio._helpers import _read_file as meshio_read_file
from meshio._helpers import write as meshio_write
from meshio._mesh import Mesh

def read(filename, file_format: str | None = None, **kwargs) -> Mesh:
    """Custom read function that can override specific meshio functionality.
    
    This function serves as an intermediate layer between your code and meshio.
    It allows you to override specific meshio functions while keeping the original
    package untouched.
    
    Args:
        filename: The file to read from
        file_format: Optional file format specification
        **kwargs: Additional arguments passed to the reader
    
    Returns:
        Mesh: The loaded mesh
    """
    if is_buffer(filename, "r"):
        return _read_buffer(filename, file_format, **kwargs)
    return _read_file(filename, file_format, **kwargs)

def _read_buffer(filename, file_format: str | None, **kwargs):
    """Custom buffer reader that can override specific meshio functionality.
    
    This function allows you to override the meshio buffer reader for specific
    file formats while falling back to the original meshio implementation for
    other formats.
    """
    if file_format is None:
        raise ReadError("File format must be given if buffer is used")
    
    # Override specific file formats here
    if file_format == "nastran":
        from .meshio.nastran._nastran import read_buffer
        return read_buffer(filename, **kwargs)
    
    # Fall back to original meshio implementation for other formats
    return meshio_read_buffer(filename, file_format, **kwargs)

def _read_file(filename, file_format: str | None, **kwargs):
    """Custom file reader that can override specific meshio functionality.
    
    This function allows you to override the meshio file reader for specific
    file formats while falling back to the original meshio implementation for
    other formats.
    """
    # Override specific file formats here
    if file_format == "nastran":
        from .meshio.nastran._nastran import read
        return read(filename, **kwargs)
    
    # Fall back to original meshio implementation for other formats
    return meshio_read_file(filename, file_format, **kwargs)

def write(filename, mesh: Mesh, file_format: str | None = None, **kwargs):
    """Custom write function that can override specific meshio functionality.
    
    This function serves as an intermediate layer between your code and meshio.
    It allows you to override specific meshio functions while keeping the original
    package untouched.
    
    Args:
        filename: The file to write to
        mesh: The mesh to write
        file_format: Optional file format specification
        **kwargs: Additional arguments passed to the writer
    """
    # Override specific file formats here
    if file_format == "nastran":
        from .meshio.nastran._nastran import write
        return write(filename, mesh, **kwargs)
    
    # Fall back to original meshio implementation for other formats
    return meshio_write(filename, mesh, file_format, **kwargs) 