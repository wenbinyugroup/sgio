"""
Middle layer between sgio and meshio for customizing mesh I/O functionality.

Overall, this module is similar to meshio._helpers.py.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional, Union

from meshio import Mesh
from meshio._helpers import reader_map, _writer_map, extension_to_filetypes

from sgio.core.mesh import SGMesh

logger = logging.getLogger(__name__)

# Maps for SG-specific readers and writers
sgmesh_reader_map: dict[str, Callable] = {}
sgmesh_writer_map: dict[str, Callable] = {}

# Map of file extensions to format names
sgmesh_ext_to_filetypes: dict[str, list[str]] = {}



def register_sgmesh_format(
    format_name: str, extensions: list[str], reader, writer
) -> None:
    """
    """
    for ext in extensions:
        if ext not in sgmesh_ext_to_filetypes:
            sgmesh_ext_to_filetypes[ext] = []
        sgmesh_ext_to_filetypes[ext].append(format_name)

    if reader is not None:
        sgmesh_reader_map[format_name] = reader

    sgmesh_writer_map.update(writer)


def read_sgmesh_buffer(file, file_format:str|None, **kwargs) -> SGMesh | Mesh | None:
    """Read the mesh data from an SG file.

    Parameters
    ----------
    file : file-like object
        The file-like object to read.
    file_format : str, optional
        The format of the file to read.

    Returns
    -------
    mesh : SGMesh | Mesh
        The SG mesh data.
    """

    if file_format is None:
        raise ValueError("File format must be given if buffer is used")

    reader = None

    try:
        reader = sgmesh_reader_map[file_format]
    except KeyError:
        try:
            reader = reader_map[file_format]  # meshio reader
        except KeyError:
            raise ValueError(f"Unknown file format '{file_format}'")

    return reader(file, **kwargs)




def write_sgmesh_buffer(file, mesh:SGMesh, file_format:str|None, **kwargs) -> None:
    """Write the mesh data to an SG file.

    Parameters
    ----------
    file : file-like object
        The file-like object to write to.
    mesh : SGMesh
        The mesh data to write.
    file_format : str, optional
        The format of the file to write.
    """

    if file_format is None:
        raise ValueError("File format must be given if buffer is used")

