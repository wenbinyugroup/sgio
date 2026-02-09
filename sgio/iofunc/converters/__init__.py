"""Conversion utilities for Structure Gene data.

This module provides functions for converting between different file formats
and converting mesh objects to Structure Gene objects.
"""

from __future__ import annotations

from .mesh_converter import mesh_to_sg
from .format_converter import convert

__all__ = [
    'mesh_to_sg',
    'convert',
]
