"""
Format registry for custom mesh format implementations.
"""
from typing import Dict, Optional, Callable, Type
from ..base import SGioMesh

# Registry for format-specific readers and writers
_format_readers: Dict[str, Callable] = {}
_format_writers: Dict[str, Callable] = {}

def register_format(format_name: str, reader: Optional[Callable] = None, writer: Optional[Callable] = None):
    """Register a custom format implementation.
    
    Args:
        format_name: Name of the format (e.g., 'abaqus', 'vtk')
        reader: Optional reader function for this format
        writer: Optional writer function for this format
    """
    if reader:
        _format_readers[format_name.lower()] = reader
    if writer:
        _format_writers[format_name.lower()] = writer

def get_format_reader(format_name: str) -> Optional[Callable]:
    """Get the reader function for a specific format.
    
    Args:
        format_name: Name of the format
        
    Returns:
        The reader function if registered, None otherwise
    """
    return _format_readers.get(format_name.lower())

def get_format_writer(format_name: str) -> Optional[Callable]:
    """Get the writer function for a specific format.
    
    Args:
        format_name: Name of the format
        
    Returns:
        The writer function if registered, None otherwise
    """
    return _format_writers.get(format_name.lower()) 