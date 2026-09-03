"""Gmsh input parser."""

from __future__ import annotations

import struct
from typing import Any, TextIO

from meshio._exceptions import ReadError

from . import _gmsh22
from . import _gmsh40
from . import _gmsh41
from ._common import _fast_forward_to_end_block
from .keywords import COMMENT_BLOCK, MESH_FORMAT_BLOCK, DEFAULT_FORMAT_VERSION

# Exact ``$MeshFormat`` version strings. Note that MSH 4.0 files declare
# themselves as "4", not "4.0", so bare "4" must resolve to the 4.0 reader.
_READERS = {
    "2": _gmsh22,
    "2.2": _gmsh22,
    "4": _gmsh40,
    "4.0": _gmsh40,
    "4.1": _gmsh41,
}

# Fallback for unknown minor versions: parse with the newest reader of that
# major version rather than the oldest.
_MAJOR_READERS = {
    "2": _gmsh22,
    "4": _gmsh41,
}


def parse_input_buffer(
    file: TextIO,
    format_version: str = DEFAULT_FORMAT_VERSION,
) -> dict[str, Any]:
    """Parse a Gmsh input buffer into a raw intermediate payload.

    Parameters
    ----------
    file : TextIO
        Open Gmsh input buffer in binary mode.
    format_version : str, optional
        Caller-requested format version. Gmsh input is auto-detected from the
        file header; this value is stored for traceability only.

    Returns
    -------
    dict[str, Any]
        Raw parsed payload containing file-header metadata and the parsed mesh.
    """
    line = file.readline().decode().strip()

    while line == COMMENT_BLOCK:
        _fast_forward_to_end_block(file, "Comments")
        line = file.readline().decode().strip()

    if line != MESH_FORMAT_BLOCK:
        raise ReadError(f"Expected {MESH_FORMAT_BLOCK}, got {repr(line)}")

    detected_format_version, data_size, is_ascii = _read_header(file)
    reader = _resolve_reader(detected_format_version)
    mesh = reader.read_buffer(file, is_ascii, data_size)

    return {
        "requested_format_version": format_version,
        "format_version": detected_format_version,
        "data_size": data_size,
        "is_ascii": is_ascii,
        "mesh": mesh,
    }


def _read_header(file: TextIO) -> tuple[str, int, bool]:
    """Read the Gmsh ``$MeshFormat`` header block."""
    line = file.readline().decode()
    tokens = list(filter(None, line.split()))
    format_version = tokens[0]
    if tokens[1] not in ["0", "1"]:
        raise ReadError("Invalid file-type in header")

    is_ascii = tokens[1] == "0"
    data_size = int(tokens[2])
    if not is_ascii:
        # The next bytes are the integer 1 used as the endianness probe.
        one = file.read(struct.calcsize("i"))
        if struct.unpack("i", one)[0] != 1:
            raise ReadError("Endianness mismatch")

    _fast_forward_to_end_block(file, "MeshFormat")
    return format_version, data_size, is_ascii


def _resolve_reader(format_version: str):
    """Resolve a version string to the corresponding low-level reader module."""
    try:
        return _READERS[format_version]
    except KeyError:
        try:
            return _MAJOR_READERS[format_version.split(".")[0]]
        except KeyError as exc:
            raise ValueError(
                f"Need mesh format in {sorted(_READERS.keys())} (got {format_version})"
            ) from exc
