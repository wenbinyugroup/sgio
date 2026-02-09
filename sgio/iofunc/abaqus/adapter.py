"""Abaqus format adapter classes.

This module provides object-oriented adapters implementing the BaseFormatReader
and BaseFormatWriter abstract base classes for Abaqus format I/O operations.
"""

from __future__ import annotations

from typing import Any, Optional
import io

from ..base import BaseFormatReader, BaseFormatWriter
from sgio.core.sg import StructureGene

from ._abaqus import read


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
        
        return read(file_path_or_buffer, sgdim=sgdim, model=model, **kwargs)
    
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
    
    def validate(self, file_path_or_buffer) -> bool:
        """Validate if file is in Abaqus format.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file to validate.
            
        Returns
        -------
        bool
            True if file appears to be Abaqus format, False otherwise.
        """
        try:
            if isinstance(file_path_or_buffer, str):
                with open(file_path_or_buffer, 'r') as f:
                    # Read first few lines to check for Abaqus format markers
                    lines = [f.readline() for _ in range(10)]
            else:
                pos = file_path_or_buffer.tell()
                lines = [file_path_or_buffer.readline() for _ in range(10)]
                file_path_or_buffer.seek(pos)
            
            # Abaqus files typically have:
            # - *Heading or *HEADING keyword
            # - *Node, *Element, *Material keywords
            # - Comments start with **
            abaqus_keywords = ['*heading', '*node', '*element', '*material', '*part', '*assembly']
            
            for line in lines:
                line_lower = line.lower().strip()
                if any(keyword in line_lower for keyword in abaqus_keywords):
                    return True
                # Check for comment lines
                if line_lower.startswith('**'):
                    continue
            
            return False
            
        except Exception:
            return False


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
        file_path_or_buffer,
        sg: StructureGene,
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
    
    def write_output(
        self,
        file_path_or_buffer,
        data: Any,
        **kwargs
    ) -> None:
        """Write Abaqus output file.
        
        Note: Abaqus output writing is handled by Abaqus itself.
        This method is provided for interface completeness.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file to write to.
        data : Any
            Data to write.
        **kwargs
            Additional keyword arguments.
            
        Raises
        ------
        NotImplementedError
            Abaqus output writing is handled by Abaqus.
        """
        raise NotImplementedError("Abaqus output writing is handled by Abaqus")
    
    def validate(self, sg: StructureGene) -> bool:
        """Validate structure gene for Abaqus format writing.
        
        Parameters
        ----------
        sg : StructureGene
            Structure gene to validate.
            
        Returns
        -------
        bool
            True if structure gene is valid for Abaqus format, False otherwise.
        """
        # Basic validation checks
        if sg is None:
            return False
        
        # Check required attributes
        if not hasattr(sg, 'mesh') or sg.mesh is None:
            return False
        
        if not hasattr(sg, 'materials') or not sg.materials:
            return False
        
        return True
