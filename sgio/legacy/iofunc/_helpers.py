from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Union

import numpy as np
from numpy.typing import ArrayLike

from meshio import read as meshio_read, write as meshio_write
from meshio import Mesh as MeshioMesh
from meshio._exceptions import ReadError as MeshioReadError, WriteError as MeshioWriteError

from ...core.mesh import SGMesh

# Maps for SG-specific readers and writers
sg_reader_map: Dict[str, Callable] = {}
sg_writer_map: Dict[str, Callable] = {}

# Map of file extensions to format names
extension_to_filetypes: Dict[str, List[str]] = {}

# Set of formats that have been overridden by SG-specific implementations
overridden_formats: set = set()


def register_format(
    format_name: str, 
    extensions: List[str], 
    reader: Optional[Callable] = None, 
    writer: Optional[Callable] = None
) -> None:
    """Register a new format or override an existing one.
    
    Args:
        format_name: Name of the format
        extensions: List of file extensions associated with this format
        reader: Function to read files in this format
        writer: Function to write files in this format
    """
    # Register extensions
    for ext in extensions:
        if ext not in extension_to_filetypes:
            extension_to_filetypes[ext] = []
        if format_name not in extension_to_filetypes[ext]:
            extension_to_filetypes[ext].append(format_name)
    
    # Register reader if provided
    if reader is not None:
        sg_reader_map[format_name] = reader
        overridden_formats.add(format_name)
    
    # Register writer if provided
    if writer is not None:
        sg_writer_map[format_name] = writer
        overridden_formats.add(format_name)


def deregister_format(format_name: str) -> None:
    """Deregister a format.
    
    Args:
        format_name: Name of the format to deregister
    """
    # Remove from extension mapping
    for ext in list(extension_to_filetypes.keys()):
        if format_name in extension_to_filetypes[ext]:
            extension_to_filetypes[ext].remove(format_name)
            if not extension_to_filetypes[ext]:
                del extension_to_filetypes[ext]
    
    # Remove from reader and writer maps
    if format_name in sg_reader_map:
        del sg_reader_map[format_name]
    
    if format_name in sg_writer_map:
        del sg_writer_map[format_name]
    
    # Remove from overridden formats
    if format_name in overridden_formats:
        overridden_formats.remove(format_name)


def _filetypes_from_path(path: Path) -> List[str]:
    """Determine possible file formats from the file path.
    
    Args:
        path: Path to the file
        
    Returns:
        List of possible format names
    """
    ext = ""
    out = []
    for suffix in reversed(path.suffixes):
        ext = (suffix + ext).lower()
        if ext in extension_to_filetypes:
            out.extend(extension_to_filetypes[ext])
    
    if not out:
        raise MeshioReadError(f"Could not deduce file format from path '{path}'.")
    
    return out


def read(filename: Union[str, Path], file_format: Optional[str] = None, **kwargs) -> SGMesh:
    """Read a mesh file and return an SGMesh object.
    
    Args:
        filename: Path to the file to read
        file_format: Optional format name. If not provided, it will be deduced from the file extension.
        **kwargs: Additional arguments to pass to the reader
        
    Returns:
        SGMesh object
    """
    if isinstance(filename, str):
        path = Path(filename)
    else:
        path = filename
    
    if not path.exists():
        raise MeshioReadError(f"File {path} not found.")
    
    # Determine file format if not provided
    if file_format is None:
        possible_formats = _filetypes_from_path(path)
        file_format = possible_formats[0]  # Use the first format
    
    # Check if we have a custom reader for this format
    if file_format in sg_reader_map:
        try:
            return sg_reader_map[file_format](path, **kwargs)
        except Exception as e:
            raise MeshioReadError(f"Error reading {path} with SG reader: {str(e)}")
    
    # Fall back to meshio reader
    try:
        meshio_mesh = meshio_read(path, file_format=file_format, **kwargs)
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
        return sg_mesh
    except Exception as e:
        raise MeshioReadError(f"Error reading {path} with meshio reader: {str(e)}")


def write(filename: Union[str, Path], mesh: Union[SGMesh, MeshioMesh], file_format: Optional[str] = None, **kwargs) -> None:
    """Write a mesh to a file.
    
    Args:
        filename: Path to the file to write
        mesh: SGMesh or meshio.Mesh object to write
        file_format: Optional format name. If not provided, it will be deduced from the file extension.
        **kwargs: Additional arguments to pass to the writer
    """
    if isinstance(filename, str):
        path = Path(filename)
    else:
        path = filename
    
    # Determine file format if not provided
    if file_format is None:
        possible_formats = _filetypes_from_path(path)
        file_format = possible_formats[0]  # Use the first format
    
    # Check if we have a custom writer for this format
    if file_format in sg_writer_map:
        try:
            return sg_writer_map[file_format](path, mesh, **kwargs)
        except Exception as e:
            raise MeshioWriteError(f"Error writing {path} with SG writer: {str(e)}")
    
    # Fall back to meshio writer
    try:
        # If it's an SGMesh, convert to meshio.Mesh for writing
        if isinstance(mesh, SGMesh):
            meshio_mesh = MeshioMesh(
                points=mesh.points,
                cells=mesh.cells,
                point_data=mesh.point_data,
                cell_data=mesh.cell_data,
                field_data=mesh.field_data,
                point_sets=mesh.point_sets,
                cell_sets=mesh.cell_sets
            )
            return meshio_write(path, meshio_mesh, file_format=file_format, **kwargs)
        else:
            return meshio_write(path, mesh, file_format=file_format, **kwargs)
    except Exception as e:
        raise MeshioWriteError(f"Error writing {path} with meshio writer: {str(e)}")


def write_points_cells(
    filename: Union[str, Path],
    points: ArrayLike,
    cells: Union[Dict[str, ArrayLike], List[tuple[str, ArrayLike]]],
    point_data: Optional[Dict[str, ArrayLike]] = None,
    cell_data: Optional[Dict[str, List[ArrayLike]]] = None,
    field_data: Optional[Dict[str, ArrayLike]] = None,
    point_sets: Optional[Dict[str, ArrayLike]] = None,
    cell_sets: Optional[Dict[str, List[ArrayLike]]] = None,
    file_format: Optional[str] = None,
    **kwargs
) -> None:
    """Write points and cells to a file.
    
    Args:
        filename: Path to the file to write
        points: Array of points
        cells: Dictionary or list of cell blocks
        point_data: Optional point data
        cell_data: Optional cell data
        field_data: Optional field data
        point_sets: Optional point sets
        cell_sets: Optional cell sets
        file_format: Optional format name
        **kwargs: Additional arguments to pass to the writer
    """
    points = np.asarray(points)
    mesh = SGMesh(
        points=points,
        cells=cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        point_sets=point_sets,
        cell_sets=cell_sets
    )
    write(filename, mesh, file_format=file_format, **kwargs)

