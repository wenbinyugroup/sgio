from __future__ import annotations

import logging
import struct

import numpy as np

from . import _gmsh22
# from . import _gmsh40
from . import _gmsh41
from ._common import _fast_forward_to_end_block
from sgio.iofunc._meshio import ReadError

logger = logging.getLogger(__name__)

# Some mesh files use "2" when it should be "2.2" and "4" when it should be "4.1"
_readers = {"2": _gmsh22, "2.2": _gmsh22, "4": _gmsh41, "4.1": _gmsh41}


def _read_header(f):
    """Read the mesh format block.

    Returns:
        fmt_version: str
        data_size: int
        is_ascii: bool
    """
    line = f.readline().decode()
    str_list = list(filter(None, line.split()))
    fmt_version = str_list[0]
    if str_list[1] not in ["0", "1"]:
        raise ReadError("Invalid file-type in header")
    is_ascii = str_list[1] == "0"
    data_size = int(str_list[2])
    if not is_ascii:
        # The next line is the integer 1 in bytes for endianness check
        one = f.read(struct.calcsize("i"))
        if struct.unpack("i", one)[0] != 1:
            raise ReadError("Endianness mismatch")
    _fast_forward_to_end_block(f, "MeshFormat")
    return fmt_version, data_size, is_ascii


def read_buffer(file, format_version="4.1", **kwargs):
    """Read a Gmsh mesh from a buffer.

    Parameters
    ----------
    file : file-like object
        The file buffer to read from (opened in binary mode).
    format_version : str
        The expected format version. If not specified, auto-detect from file.

    Returns
    -------
    mesh : meshio.Mesh
        The mesh data read from the file.
    """
    # The format is specified at:
    # <http://gmsh.info/doc/texinfo/gmsh.html#File-formats>

    line = file.readline().decode().strip()

    # Skip any $Comments/$EndComments sections
    while line == "$Comments":
        _fast_forward_to_end_block(file, "Comments")
        line = file.readline().decode().strip()

    if line != "$MeshFormat":
        raise ReadError(f"Expected $MeshFormat, got {repr(line)}")

    fmt_version, data_size, is_ascii = _read_header(file)

    try:
        reader = _readers[fmt_version]
    except KeyError:
        try:
            reader = _readers[fmt_version.split(".")[0]]
        except KeyError:
            raise ValueError(
                f"Need mesh format in {sorted(_readers.keys())} (got {fmt_version})"
            )

    return reader.read_buffer(file, is_ascii, data_size)


def write_buffer(
    file, mesh, format_version, float_fmt, sgdim,
    mesh_only, binary,
    **kwargs):
    """
    """
    logger.debug(locals())

    if format_version == "":
        format_version = "4.1"

    if format_version == "2.2":
        _gmsh22.write_buffer(file, mesh, float_fmt=float_fmt, binary=binary)
    # elif format_version == "4.0":
    #     _gmsh40.write_buffer(file, mesh, format_version=format_version)
    elif format_version == "4.1":
        # handle gmsh:dim_tags
        # mesh.point_data['gmsh:dim_tags'] = np.array([[sgdim, 0]])
        mesh.point_data['gmsh:dim_tags'] = np.array([[sgdim, 1] for i in range(len(mesh.points))])
        # mesh.cell_data['gmsh:geometrical'] = np.array([[i,] for i in range(len(mesh.cells))])
        mesh.cell_data['gmsh:geometrical'] = [[1,],] * len(mesh.cells)
        _gmsh41.write_buffer(file, mesh, float_fmt, mesh_only, binary)
