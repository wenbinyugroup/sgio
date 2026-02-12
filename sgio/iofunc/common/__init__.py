"""Common utilities for IO functions shared across different formats.

This module provides shared functionality for reading and writing various
file formats (VABS, SwiftComp, etc.) to reduce code duplication and improve
maintainability.
"""

from __future__ import annotations

from .material_readers import (
    read_material_rotation_combinations,
    read_materials,
    read_material,
    read_elastic_property,
    read_thermal_property,
)
from .material_writers import (
    write_material_combos,
    write_material,
    write_materials,
    write_displacement_rotation,
    write_load,
)

__all__ = [
    'read_material_rotation_combinations',
    'read_materials',
    'read_material',
    'read_elastic_property',
    'read_thermal_property',
    'write_material_combos',
    'write_material',
    'write_materials',
    'write_displacement_rotation',
    'write_load',
]
