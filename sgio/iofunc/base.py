"""Base classes and interfaces for IO operations.

This module defines abstract base classes for format readers and writers,
providing a consistent interface across different file formats.

The IR object accepted/produced by adapters is intentionally typed broadly
(``Any``) to span ``StructureGene`` (SG-specific solvers), ``FEModel``
(generic FE solvers, future), and ``SGMesh`` (mesh-only formats). See
``dev-notes/architecture/io.md`` §3.1.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, TextIO, Union


class BaseFormatReader(ABC):
    """Abstract base class for format-specific readers.
    
    This class defines the interface that all format readers should implement.
    Each format (VABS, SwiftComp, Gmsh, Abaqus) should provide implementations
    of these methods.
    
    Attributes
    ----------
    format_name : str
        Name of the format (e.g., 'vabs', 'swiftcomp', 'gmsh', 'abaqus')
    """

    def __init__(self, format_name: str):
        """Initialize the format reader.

        Parameters
        ----------
        format_name : str
            Name of the format
        """
        self.format_name = format_name
    
    @abstractmethod
    def read_input(
        self,
        source: Union[str, TextIO],
        **kwargs: Any
    ) -> Any:
        """Read input file and create IR object.

        Parameters
        ----------
        source : str or TextIO
            File path or file object to read from
        **kwargs : dict
            Format-specific keyword arguments

        Returns
        -------
        StructureGene | FEModel | SGMesh
            The parsed IR object. The concrete type depends on the adapter:
            SG-specific solvers return ``StructureGene``; generic FE solvers
            return ``FEModel``; mesh-only formats return ``SGMesh``.
            
        Raises
        ------
        ValueError
            If the format version is not supported
        IOError
            If the file cannot be read
        """
        pass
    
    @abstractmethod
    def read_output(
        self,
        source: Union[str, TextIO],
        analysis: str = 'h',
        **kwargs: Any
    ) -> Any:
        """Read output file and parse results.
        
        Parameters
        ----------
        source : str or TextIO
            File path or file object to read from
        analysis : str
            Analysis type ('h' for homogenization, 'd' for dehomogenization, etc.)
        **kwargs : dict
            Format-specific keyword arguments
            
        Returns
        -------
        Any
            Parsed output data (type depends on analysis and format)
            
        Raises
        ------
        ValueError
            If the analysis type is not supported
        IOError
            If the file cannot be read
        """
        pass


class BaseFormatWriter(ABC):
    """Abstract base class for format-specific writers.
    
    This class defines the interface that all format writers should implement.
    Each format should provide implementations of these methods.
    
    Attributes
    ----------
    format_name : str
        Name of the format
    default_version : str
        Default format version to use
    """
    
    def __init__(self, format_name: str, default_version: Optional[str] = None):
        """Initialize the format writer.
        
        Parameters
        ----------
        format_name : str
            Name of the format
        default_version : str, optional
            Default version to use for writing
        """
        self.format_name = format_name
        self.default_version = default_version
    
    @abstractmethod
    def write_input(
        self,
        destination: Union[str, TextIO],
        model: Any,
        **kwargs: Any
    ) -> None:
        """Write IR object to input file.

        The IR object can be ``StructureGene``, ``FEModel``, ``StructuralModel``
        or ``SGMesh`` depending on the adapter. Each adapter is responsible
        for extracting the fields it needs; fields the format cannot represent
        are dropped silently (or routed to ``extras``).

        Parameters
        ----------
        destination : str or TextIO
            File path or file object to write to
        model : Any
            IR object to write (``StructureGene`` / ``FEModel`` / ``SGMesh``)
        **kwargs : dict
            Format-specific keyword arguments

        Raises
        ------
        ValueError
            If the IR object is invalid
        IOError
            If the file cannot be written
        """
        pass


class FormatRegistry:
    """Registry for managing available format readers and writers.
    
    This class implements a singleton pattern for registering and retrieving
    format-specific readers and writers.
    
    Examples
    --------
    >>> registry = FormatRegistry()
    >>> registry.register_reader('vabs', VABSReader())
    >>> reader = registry.get_reader('vabs')
    """
    
    _instance: Optional['FormatRegistry'] = None

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._readers = {}
            cls._instance._writers = {}
            cls._instance._aliases = {}
        return cls._instance

    def register_alias(self, alias: str, target: str) -> None:
        """Register an alias for a format name.

        Aliases let callers use short or alternate spellings
        (e.g. ``'sc'`` for ``'swiftcomp'``).

        Parameters
        ----------
        alias : str
            Alias name (lowercase).
        target : str
            Canonical format name (lowercase).
        """
        self._aliases[alias.lower()] = target.lower()

    def normalize(self, format_name: str) -> str:
        """Resolve a possibly-aliased format name to its canonical form."""
        name = format_name.lower()
        return self._aliases.get(name, name)

    def register_reader(self, format_name: str, reader: BaseFormatReader) -> None:
        """Register a format reader.
        
        Parameters
        ----------
        format_name : str
            Name of the format (lowercase)
        reader : BaseFormatReader
            Reader instance to register
        """
        self._readers[format_name.lower()] = reader

    def register_writer(self, format_name: str, writer: BaseFormatWriter) -> None:
        """Register a format writer.
        
        Parameters
        ----------
        format_name : str
            Name of the format (lowercase)
        writer : BaseFormatWriter
            Writer instance to register
        """
        self._writers[format_name.lower()] = writer
    
    def get_reader(self, format_name: str) -> Optional[BaseFormatReader]:
        """Get a registered reader for the format.
        
        Parameters
        ----------
        format_name : str
            Name of the format
            
        Returns
        -------
        BaseFormatReader or None
            The registered reader, or None if not found
        """
        return self._readers.get(self.normalize(format_name))

    def get_writer(self, format_name: str) -> Optional[BaseFormatWriter]:
        """Get a registered writer for the format.
        
        Parameters
        ----------
        format_name : str
            Name of the format
            
        Returns
        -------
        BaseFormatWriter or None
            The registered writer, or None if not found
        """
        return self._writers.get(self.normalize(format_name))

    def list_formats(self) -> dict[str, dict[str, bool]]:
        """List all registered formats.
        
        Returns
        -------
        dict
            Dictionary with format names as keys and dict with 'reader' and 'writer'
            booleans indicating availability
        """
        all_formats = set(self._readers.keys()) | set(self._writers.keys())
        return {
            fmt: {
                'reader': fmt in self._readers,
                'writer': fmt in self._writers,
            }
            for fmt in sorted(all_formats)
        }


# Convenience function for accessing the global registry
def get_format_registry() -> FormatRegistry:
    """Get the global format registry instance.
    
    Returns
    -------
    FormatRegistry
        The singleton format registry
    """
    return FormatRegistry()
