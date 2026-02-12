"""VABS (Variational Asymptotic Beam Sectional Analysis) format I/O.

This module provides functions for reading and writing VABS format files,
including input files, output files, and mesh data.

Main Functions
--------------
- read_buffer: Read VABS input from file buffer
- write_buffer: Write VABS input to file buffer  
- read_output_buffer: Read VABS output from file buffer

Internal Functions
------------------
- _readOutputElementStrainStressCase: Parse element strain/stress data
- _readOutputFailureIndexCase: Parse failure index data
"""

from __future__ import annotations

from ._output import (
    _readOutputElementStrainStressCase,
    _readOutputFailureIndexCase,
)
from .main import (
    read_buffer,
    read_output_buffer,
    write_buffer,
)
from .adapter import (
    VABSReader,
    VABSWriter,
)

__all__ = [
    'read_buffer',
    'write_buffer',
    'read_output_buffer',
    'VABSReader',
    'VABSWriter',
]
