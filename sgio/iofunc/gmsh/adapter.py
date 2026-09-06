"""Gmsh format adapter classes.

This module provides object-oriented adapters implementing the BaseFormatReader
and BaseFormatWriter abstract base classes for Gmsh format I/O operations.
"""

from __future__ import annotations

from typing import Any, Optional

from ..base import BaseFormatReader, BaseFormatWriter

from .mapper_in import map_input_to_mesh
from .mapper_out import map_model_to_write_payload
from .parser import parse_input_buffer
from .writer import write_input_payload


class GmshReader(BaseFormatReader):
    """Gmsh format reader adapter.
    
    Implements the BaseFormatReader interface for reading Gmsh mesh files (.msh).
    
    Examples
    --------
    >>> reader = GmshReader()
    >>> with open('mesh.msh', 'rb') as f:  # Note: binary mode
    ...     mesh = reader.read_input(f, format_version='4.1')
    """
    
    def __init__(self):
        """Initialize Gmsh reader."""
        super().__init__('gmsh')
    
    def read_input(
        self,
        file_path_or_buffer,
        format_version: str = '4.1',
        **kwargs
    ) -> Any:
        """Read Gmsh mesh file.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to read from.
            Note: File must be opened in binary mode ('rb').
        format_version : str, optional
            Format version ('2.2' or '4.1'), by default '4.1'.
        **kwargs
            Additional keyword arguments.
            
        Returns
        -------
        meshio.Mesh
            Parsed mesh object.
        """
        if isinstance(file_path_or_buffer, str):
            with open(file_path_or_buffer, 'rb') as f:
                parsed = parse_input_buffer(f, format_version=format_version)
        else:
            parsed = parse_input_buffer(file_path_or_buffer, format_version=format_version)
        return map_input_to_mesh(parsed)
    
    def read_output(
        self,
        file_path_or_buffer,
        **kwargs
    ) -> Any:
        """Read Gmsh output file.
        
        Note: Gmsh typically doesn't have separate output files.
        This method is provided for interface completeness.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to read from.
        **kwargs
            Additional keyword arguments.
            
        Raises
        ------
        NotImplementedError
            Gmsh output reading is not supported.
        """
        raise NotImplementedError("Gmsh output reading is not applicable")


class GmshWriter(BaseFormatWriter):
    """Gmsh format writer adapter.
    
    Implements the BaseFormatWriter interface for writing Gmsh mesh files.
    
    Examples
    --------
    >>> writer = GmshWriter()
    >>> with open('mesh.msh', 'wb') as f:  # Note: binary mode
    ...     writer.write_input(f, mesh, format_version='4.1')
    """
    
    def __init__(self):
        """Initialize Gmsh writer."""
        super().__init__('gmsh')
    
    def write_input(
        self,
        destination,
        model_obj,
        format_version: str = '4.1',
        float_fmt: str = '.16e',
        sgdim: Optional[int] = None,
        mesh_only: bool = True,
        binary: bool = True,
        **kwargs
    ) -> None:
        """Write Gmsh mesh file.

        Accepts either a bare mesh object (``SGMesh`` / ``meshio.Mesh``) or a
        ``StructureGene`` — for the latter the writer extracts mesh, mocombos
        and analysis configs itself.

        Parameters
        ----------
        destination : str or file-like
            Path to file or file buffer to write to. Binary mode required for
            file objects.
        model_obj : StructureGene or SGMesh or meshio.Mesh
            IR object to write.
        format_version : str, optional
            Format version ('2.2' or '4.1'), by default '4.1'.
        float_fmt : str, optional
            Float format string, by default '.16e'.
        sgdim : int, optional
            Structure gene dimension. If ``None``, inferred from the SG.
        mesh_only : bool, optional
            Write mesh data only, by default True.
        binary : bool, optional
            Write in binary format, by default True.
        """
        payload = map_model_to_write_payload(
            model_obj,
            format_version=format_version,
            float_fmt=float_fmt,
            sgdim=sgdim,
            mesh_only=mesh_only,
            binary=binary,
            **kwargs,
        )

        if isinstance(destination, str):
            open_mode = 'wb' if binary else 'w'
            with open(destination, open_mode) as f:
                write_input_payload(f, payload)
        else:
            write_input_payload(destination, payload)
