"""Gmsh format I/O.

This module provides functions for reading and writing Gmsh mesh format files.
Supports Gmsh versions 2.2 and 4.1 (ASCII and binary).

Main Functions
--------------
- read_buffer: Read Gmsh mesh from file buffer
- write_buffer: Write Gmsh mesh to file buffer

Utilities
---------
- write_element_node_data: Write element node data in Gmsh format
"""

from __future__ import annotations

from ._common import write_element_node_data
from ._gmsh import read_buffer, write_buffer
from .adapter import (
    GmshReader,
    GmshWriter,
)

__all__ = [
    'read_buffer',
    'write_buffer',
    'write_element_node_data',
    'GmshReader',
    'GmshWriter',
]
