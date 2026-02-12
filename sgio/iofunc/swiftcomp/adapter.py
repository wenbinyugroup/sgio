"""SwiftComp format adapter classes.

This module provides object-oriented adapters implementing the BaseFormatReader
and BaseFormatWriter abstract base classes for SwiftComp format I/O operations.
"""

from __future__ import annotations

from typing import Any, Optional
import io

from ..base import BaseFormatReader, BaseFormatWriter
from sgio.core.sg import StructureGene
import sgio.model as smdl

from ._swiftcomp import (
    read_input_buffer,
    read_output_buffer,
    write_buffer,
)


class SwiftCompReader(BaseFormatReader):
    """SwiftComp format reader adapter.
    
    Implements the BaseFormatReader interface for reading SwiftComp input and output files.
    
    Examples
    --------
    >>> reader = SwiftCompReader()
    >>> with open('beam.sc', 'r') as f:
    ...     sg = reader.read_input(f, format_version='2.0', model='BM')
    >>> with open('beam.sc.k', 'r') as f:
    ...     model = reader.read_output(f, analysis='h', sg=sg)
    """
    
    def __init__(self):
        """Initialize SwiftComp reader."""
        super().__init__('swiftcomp')
    
    def read_input(
        self,
        file_path_or_buffer,
        format_version: str = '2.0',
        model: int | str = 1,
        **kwargs
    ) -> StructureGene:
        """Read SwiftComp input file.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to read from.
        format_version : str, optional
            Format version, by default '2.0'.
        model : int or str, optional
            Model type (1, 2, 3 or 'BM', 'PL', 'SD'), by default 1.
        **kwargs
            Additional keyword arguments.
            
        Returns
        -------
        StructureGene
            Parsed structure gene object.
        """
        if isinstance(file_path_or_buffer, str):
            with open(file_path_or_buffer, 'r') as f:
                return read_input_buffer(f, format_version=format_version, model=model)
        else:
            return read_input_buffer(file_path_or_buffer, format_version=format_version, model=model)
    
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
        """Read SwiftComp output file.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to read from.
        analysis : str, optional
            Analysis type ('h', 'd', 'l', 'f', 'fe', 'fi'), by default 'h'.
        sg : StructureGene, optional
            Associated structure gene object.
        extension : str, optional
            File extension, by default ''.
        model_type : str, optional
            Model type ('BM1', 'BM2', 'PL1', 'SD1'), by default 'BM1'.
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
        """Validate if file is in SwiftComp format.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to validate.
            
        Returns
        -------
        bool
            True if file appears to be SwiftComp format, False otherwise.
        """
        try:
            if isinstance(file_path_or_buffer, str):
                with open(file_path_or_buffer, 'r') as f:
                    # Read first few lines to check SwiftComp format markers
                    lines = [f.readline() for _ in range(5)]
            else:
                pos = file_path_or_buffer.tell()
                lines = [file_path_or_buffer.readline() for _ in range(5)]
                file_path_or_buffer.seek(pos)
            
            # SwiftComp format typically has:
            # Line 1: format_version
            # Line 2: analysis_type
            # Comments use '#'
            if len(lines) < 2:
                return False
            
            # Check for SwiftComp-specific keywords or structure
            # Format version line may contain numbers
            try:
                # Look for '#' comments or specific SwiftComp keywords
                for line in lines:
                    if '#' in line or 'analysis' in line.lower():
                        return True
                    
                # Check if first line contains version number
                parts = lines[0].strip().split()
                if len(parts) > 0:
                    float(parts[0])  # SwiftComp starts with version number
                    return True
                    
            except (ValueError, IndexError):
                pass
            
            return False
            
        except Exception:
            return False


class SwiftCompWriter(BaseFormatWriter):
    """SwiftComp format writer adapter.
    
    Implements the BaseFormatWriter interface for writing SwiftComp input files.
    
    Examples
    --------
    >>> writer = SwiftCompWriter()
    >>> with open('beam.sc', 'w') as f:
    ...     writer.write_input(f, sg, analysis='h')
    """
    
    def __init__(self):
        """Initialize SwiftComp writer."""
        super().__init__('swiftcomp')
    
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
        """Write SwiftComp input file.
        
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
        """Write SwiftComp output file.
        
        Note: SwiftComp output writing is not typically supported.
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
            SwiftComp output writing is not supported.
        """
        raise NotImplementedError("SwiftComp output writing is not supported")
    
    def validate(self, sg: StructureGene) -> bool:
        """Validate structure gene for SwiftComp format writing.
        
        Parameters
        ----------
        sg : StructureGene
            Structure gene to validate.
            
        Returns
        -------
        bool
            True if structure gene is valid for SwiftComp format, False otherwise.
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
