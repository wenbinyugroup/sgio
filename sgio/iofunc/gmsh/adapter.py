"""Gmsh format adapter classes.

This module provides object-oriented adapters implementing the BaseFormatReader
and BaseFormatWriter abstract base classes for Gmsh format I/O operations.
"""

from __future__ import annotations

from typing import Any, Optional
import io

from ..base import BaseFormatReader, BaseFormatWriter
from sgio.core.sg import StructureGene

from ._gmsh import (
    read_buffer,
    write_buffer,
)
from ..common import build_material_id_map
from ..utils import infer_section_dimension


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
                return read_buffer(f, format_version=format_version, **kwargs)
        else:
            return read_buffer(file_path_or_buffer, format_version=format_version, **kwargs)
    
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
    
    def validate(self, file_path_or_buffer) -> bool:
        """Validate if file is in Gmsh format.
        
        Parameters
        ----------
        file_path_or_buffer : str or file-like
            Path to file or file buffer to validate.
            
        Returns
        -------
        bool
            True if file appears to be Gmsh format, False otherwise.
        """
        try:
            if isinstance(file_path_or_buffer, str):
                with open(file_path_or_buffer, 'rb') as f:
                    # Read first line to check for Gmsh format marker
                    line = f.readline().decode().strip()
            else:
                pos = file_path_or_buffer.tell()
                line = file_path_or_buffer.readline()
                if isinstance(line, bytes):
                    line = line.decode().strip()
                else:
                    line = line.strip()
                file_path_or_buffer.seek(pos)
            
            # Gmsh files start with $MeshFormat or $Comments
            return line in ['$MeshFormat', '$Comments']
            
        except Exception:
            return False


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
        mesh, gmsh_kwargs = self._unpack_model(model_obj, sgdim, kwargs)

        if isinstance(destination, str):
            open_mode = 'wb' if binary else 'w'
            with open(destination, open_mode) as f:
                write_buffer(
                    f, mesh, format_version=format_version,
                    float_fmt=float_fmt,
                    mesh_only=mesh_only, binary=binary, **gmsh_kwargs
                )
        else:
            write_buffer(
                destination, mesh, format_version=format_version,
                float_fmt=float_fmt,
                mesh_only=mesh_only, binary=binary, **gmsh_kwargs
            )

    @staticmethod
    def _unpack_model(model_obj, sgdim, extra_kwargs):
        """Extract mesh + Gmsh-specific configs from a model object.

        Returns a ``(mesh, kwargs)`` tuple where ``kwargs`` is a merged
        dictionary forwarded to :func:`write_buffer`.
        """
        gmsh_kwargs = dict(extra_kwargs)

        # Bare mesh path: nothing to unpack.
        if not isinstance(model_obj, StructureGene):
            gmsh_kwargs.setdefault('sgdim', sgdim if sgdim is not None else 2)
            return model_obj, gmsh_kwargs

        sg = model_obj
        material_id_map = build_material_id_map(sg.materials) if sg.mocombos else {}
        resolved_sgdim = sgdim if sgdim is not None else infer_section_dimension(sg)
        sg_configs = {'sgdim': resolved_sgdim}
        if sg.smdim is not None:
            sg_configs['model'] = sg.analysis_config.model
        sg_configs['do_damping'] = sg.analysis_config.do_damping
        sg_configs['thermal'] = sg.analysis_config.physics

        gmsh_kwargs.setdefault('sgdim', resolved_sgdim)
        gmsh_kwargs.setdefault(
            'mocombos', sg.mocombos if sg.mocombos else None
        )
        gmsh_kwargs.setdefault('material_id_map', material_id_map)
        gmsh_kwargs.setdefault('sg_configs', sg_configs)
        return sg.mesh, gmsh_kwargs
    
    def write_output(
        self,
        file_path_or_buffer,
        data: Any,
        **kwargs
    ) -> None:
        """Write Gmsh output file.
        
        Note: Gmsh typically doesn't have separate output files.
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
            Gmsh output writing is not applicable.
        """
        raise NotImplementedError("Gmsh output writing is not applicable")
    
    def validate(self, mesh: Any) -> bool:
        """Validate mesh for Gmsh format writing.
        
        Parameters
        ----------
        mesh : meshio.Mesh
            Mesh to validate.
            
        Returns
        -------
        bool
            True if mesh is valid for Gmsh format, False otherwise.
        """
        # Basic validation checks
        if mesh is None:
            return False
        
        # Check if mesh has required attributes (meshio.Mesh structure)
        if not hasattr(mesh, 'points'):
            return False
        
        if not hasattr(mesh, 'cells'):
            return False
        
        return True
