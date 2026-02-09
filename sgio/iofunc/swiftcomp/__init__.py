"""SwiftComp format I/O.

This module provides functions for reading and writing SwiftComp format files,
including input files, output files, and mesh data.

Main Functions
--------------
- read_input_buffer: Read SwiftComp input from file buffer
- write_buffer: Write SwiftComp input to file buffer
- read_output_buffer: Read SwiftComp output from file buffer

Internal Functions
------------------
- _read_output_node_disp_case: Parse node displacement data
- _read_output_node_strain_stress_case_global_gmsh: Parse node strain/stress in Gmsh format
"""

from __future__ import annotations

from ._global import *

from ._output import (
    _read_output_node_disp_case,
    _read_output_node_strain_stress_case_global_gmsh,
)

from ._swiftcomp import (
    read_input_buffer,
    read_output_buffer,
    write_buffer,
)
from .adapter import (
    SwiftCompReader,
    SwiftCompWriter,
)

__all__ = [
    'read_input_buffer',
    'write_buffer',
    'read_output_buffer',
    'SwiftCompReader',
    'SwiftCompWriter',
]

