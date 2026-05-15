"""Gmsh format constants used by parser and writer layers."""

from __future__ import annotations


COMMENT_BLOCK = "$Comments"
MESH_FORMAT_BLOCK = "$MeshFormat"
DEFAULT_FORMAT_VERSION = "4.1"
SUPPORTED_READ_VERSIONS = ("2", "2.2", "4", "4.1")
SUPPORTED_WRITE_VERSIONS = ("2.2", "4.1")
