"""Abaqus format adapter classes.

This module provides object-oriented adapters implementing the BaseFormatReader
and BaseFormatWriter abstract base classes for Abaqus format I/O operations.
"""

from __future__ import annotations

from typing import Any

from ..base import BaseFormatReader, BaseFormatWriter
from sgio.core.sg import StructureGene

from .mapper_in import map_input_to_structure_gene
from .parser import parse_input_file


class AbaqusReader(BaseFormatReader):
    """Abaqus format reader adapter.
    
    Implements the BaseFormatReader interface for reading Abaqus input files (.inp).
    
    Examples
    --------
    >>> reader = AbaqusReader()
    >>> sg = reader.read_input('model.inp', sgdim=2, model='PL1')
    """
    
    def __init__(self):
        """Initialize Abaqus reader."""
        super().__init__('abaqus')
    
    def read_input(
        self,
        file_path_or_buffer,
        sgdim: int = 2,
        model: int | str = 1,
        **kwargs
    ) -> StructureGene:
        """Read Abaqus input file.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file to read from.
            Note: Abaqus reader currently only supports file paths, not buffers.
        sgdim : int, optional
            Structure gene dimension, by default 2.
        model : int or str, optional
            Model type (1, 2, 3 or 'BM', 'PL', 'SD'), by default 1.
        **kwargs
            Additional keyword arguments.
            
        Returns
        -------
        StructureGene
            Parsed structure gene object.
        """
        if not isinstance(file_path_or_buffer, str):
            raise ValueError("Abaqus reader currently only supports file paths, not buffers")
        
        parsed = parse_input_file(file_path_or_buffer, sgdim=sgdim, model=model, **kwargs)
        return map_input_to_structure_gene(parsed)
    
    def read_output(
        self,
        file_path_or_buffer,
        **kwargs
    ) -> Any:
        """Read Abaqus output file.
        
        Note: Abaqus output reading is handled by Abaqus itself.
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
            Abaqus output reading is not supported.
        """
        raise NotImplementedError("Abaqus output reading is handled by Abaqus")


class AbaqusWriter(BaseFormatWriter):
    """Abaqus format writer adapter.
    
    Implements the BaseFormatWriter interface for writing Abaqus input files.
    
    Examples
    --------
    >>> writer = AbaqusWriter()
    >>> writer.write_input('model.inp', sg, sgdim=2)
    """
    
    def __init__(self):
        """Initialize Abaqus writer."""
        super().__init__('abaqus')
    
    def write_input(
        self,
        destination,
        model_obj,
        sgdim: int = 2,
        **kwargs
    ) -> None:
        """Write Abaqus input file.
        
        Note: Abaqus input writing is not currently implemented.
        This method is provided for interface completeness.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file to write to.
        sg : StructureGene
            Structure gene object to write.
        sgdim : int, optional
            Structure gene dimension, by default 2.
        **kwargs
            Additional keyword arguments.
            
        Raises
        ------
        NotImplementedError
            Abaqus input writing is not implemented.
        """
        raise NotImplementedError("Abaqus input writing is not currently implemented")
