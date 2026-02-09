"""VABS format adapter classes.

This module provides object-oriented adapters implementing the BaseFormatReader
and BaseFormatWriter abstract base classes for VABS format I/O operations.
"""

from __future__ import annotations

from typing import Any, Optional
import io

from ..base import BaseFormatReader, BaseFormatWriter
from sgio.core.sg import StructureGene
import sgio.model as smdl

from .main import (
    read_buffer,
    read_output_buffer,
    write_buffer,
)


class VABSReader(BaseFormatReader):
    """VABS format reader adapter.
    
    Implements the BaseFormatReader interface for reading VABS input and output files.
    
    Examples
    --------
    >>> reader = VABSReader()
    >>> with open('beam.vabs', 'r') as f:
    ...     sg = reader.read_input(f, format_version='4.0')
    >>> with open('beam.out.K', 'r') as f:
    ...     model = reader.read_output(f, analysis='h', sg=sg)
    """
    
    def __init__(self):
        """Initialize VABS reader."""
        super().__init__('vabs')
    
    def read_input(
        self,
        file_path_or_buffer,
        format_version: str = '4.0',
        **kwargs
    ) -> StructureGene:
        """Read VABS input file.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to read from.
        format_version : str, optional
            Format version, by default '4.0'.
        **kwargs
            Additional keyword arguments.
            
        Returns
        -------
        StructureGene
            Parsed structure gene object.
        """
        if isinstance(file_path_or_buffer, str):
            with open(file_path_or_buffer, 'r') as f:
                return read_buffer(f, format_version=format_version)
        else:
            return read_buffer(file_path_or_buffer, format_version=format_version)
    
    def read_output(
        self,
        file_path_or_buffer,
        analysis: str = 'h',
        sg: Optional[StructureGene] = None,
        extension: str = '',
        model_type: str = 'BM1',
        tool_version: str = '',
        ncase: int = 1,
        nelem: int = 0,
        **kwargs
    ) -> Any:
        """Read VABS output file.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to read from.
        analysis : str, optional
            Analysis type ('h', 'd', 'l', 'f', 'fe', 'fi'), by default 'h'.
        sg : StructureGene, optional
            Associated structure gene object.
        extension : str, optional
            File extension ('', 'u', 'ele'), by default ''.
        model_type : str, optional
            Model type ('BM1', 'BM2'), by default 'BM1'.
        tool_version : str, optional
            Tool version string.
        ncase : int, optional
            Number of load cases, by default 1.
        nelem : int, optional
            Number of elements, by default 0.
        **kwargs
            Additional keyword arguments.
            
        Returns
        -------
        Model or list of dict
            Parsed output data (Model object for homogenization, dictionaries for other analyses).
        """
        if isinstance(file_path_or_buffer, str):
            with open(file_path_or_buffer, 'r') as f:
                return read_output_buffer(
                    f, analysis=analysis, sg=sg, extension=extension,
                    model_type=model_type, tool_version=tool_version,
                    ncase=ncase, nelem=nelem, **kwargs
                )
        else:
            return read_output_buffer(
                file_path_or_buffer, analysis=analysis, sg=sg, extension=extension,
                model_type=model_type, tool_version=tool_version,
                ncase=ncase, nelem=nelem, **kwargs
            )
    
    def validate(self, file_path_or_buffer) -> bool:
        """Validate if file is in VABS format.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to validate.
            
        Returns
        -------
        bool
            True if file appears to be VABS format, False otherwise.
        """
        try:
            if isinstance(file_path_or_buffer, str):
                with open(file_path_or_buffer, 'r') as f:
                    # Read first few lines to check VABS format markers
                    lines = [f.readline() for _ in range(5)]
            else:
                pos = file_path_or_buffer.tell()
                lines = [file_path_or_buffer.readline() for _ in range(5)]
                file_path_or_buffer.seek(pos)
            
            # VABS format typically has:
            # Line 1: format_flag nlayer (two integers)
            # Line 2: model_flag damping_flag thermal_flag
            # Comments use '!'
            if len(lines) < 2:
                return False
            
            # Check if first line has two integers
            try:
                parts = lines[0].split()
                if len(parts) >= 2:
                    int(parts[0])
                    int(parts[1])
                    return True
            except (ValueError, IndexError):
                pass
            
            return False
            
        except Exception:
            return False


class VABSWriter(BaseFormatWriter):
    """VABS format writer adapter.
    
    Implements the BaseFormatWriter interface for writing VABS input files.
    
    Examples
    --------
    >>> writer = VABSWriter()
    >>> with open('beam.vabs', 'w') as f:
    ...     writer.write_input(f, sg, analysis='h')
    """
    
    def __init__(self):
        """Initialize VABS writer."""
        super().__init__('vabs')
    
    def write_input(
        self,
        file_path_or_buffer,
        sg: StructureGene,
        analysis: str = 'h',
        sg_fmt: int = 1,
        model: int = 0,
        model_space: str = '',
        prop_ref_y: str = 'x',
        macro_responses: list[smdl.StateCase] = None,
        sfi: str = '8d',
        sff: str = '20.12e',
        version: Optional[str] = None,
        **kwargs
    ) -> None:
        """Write VABS input file.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to write to.
        sg : StructureGene
            Structure gene object to write.
        analysis : str, optional
            Analysis type ('h', 'd', 'l', 'f', 'fe', 'fi'), by default 'h'.
        sg_fmt : int, optional
            Format flag, by default 1.
        model : int, optional
            Model identifier, by default 0.
        model_space : str, optional
            Model coordinate space, by default ''.
        prop_ref_y : str, optional
            Reference axis for property orientation, by default 'x'.
        macro_responses : list of StateCase, optional
            Macro-level responses for global analysis.
        sfi : str, optional
            Integer format string, by default '8d'.
        sff : str, optional
            Float format string, by default '20.12e'.
        version : str, optional
            Format version.
        **kwargs
            Additional keyword arguments.
        """
        if macro_responses is None:
            macro_responses = []
        
        if isinstance(file_path_or_buffer, str):
            with open(file_path_or_buffer, 'w') as f:
                write_buffer(
                    sg, f, analysis=analysis, sg_fmt=sg_fmt, model=model,
                    model_space=model_space, prop_ref_y=prop_ref_y,
                    macro_responses=macro_responses,
                    sfi=sfi, sff=sff, version=version, **kwargs
                )
        else:
            write_buffer(
                sg, file_path_or_buffer, analysis=analysis, sg_fmt=sg_fmt, model=model,
                model_space=model_space, prop_ref_y=prop_ref_y,
                macro_responses=macro_responses,
                sfi=sfi, sff=sff, version=version, **kwargs
            )
    
    def write_output(
        self,
        file_path_or_buffer,
        data: Any,
        **kwargs
    ) -> None:
        """Write VABS output file.
        
        Note: VABS output writing is not typically supported.
        This method is provided for interface completeness.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to write to.
        data : Any
            Data to write.
        **kwargs
            Additional keyword arguments.
            
        Raises
        ------
        NotImplementedError
            VABS output writing is not supported.
        """
        raise NotImplementedError("VABS output writing is not supported")
    
    def validate(self, sg: StructureGene) -> bool:
        """Validate structure gene for VABS format writing.
        
        Parameters
        ----------
        sg : StructureGene
            Structure gene to validate.
            
        Returns
        -------
        bool
            True if structure gene is valid for VABS format, False otherwise.
        """
        # Basic validation checks
        if sg is None:
            return False
        
        # Check required attributes
        if not hasattr(sg, 'mesh') or sg.mesh is None:
            return False
        
        if not hasattr(sg, 'materials') or not sg.materials:
            return False
        
        if not hasattr(sg, 'mocombos') or not sg.mocombos:
            return False
        
        return True
