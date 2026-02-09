"""Abaqus format I/O.

This module provides functions for reading Abaqus input (.inp) files.

Main Functions
--------------
- read: Read Abaqus input file and convert to StructureGene
"""

from __future__ import annotations

from ._abaqus import read
from .adapter import (
    AbaqusReader,
    AbaqusWriter,
)

__all__ = [
    'read',
    'AbaqusReader',
    'AbaqusWriter',
]

