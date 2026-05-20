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
from .material_json import (
    read_material_from_json,
    read_materials_from_json,
    write_material_to_json,
)
from .material_writers import (
    build_material_id_map,
    write_material_combos,
    write_material,
    write_materials,
    write_displacement_rotation,
    write_load,
)
from .response_writers import (
    write_section_response_displacement,
    write_section_response_load,
    write_section_response_rotation,
)

__all__ = [
    'read_material_rotation_combinations',
    'read_materials',
    'read_material',
    'read_elastic_property',
    'read_thermal_property',
    'read_material_from_json',
    'read_materials_from_json',
    'build_material_id_map',
    'write_material_combos',
    'write_material',
    'write_materials',
    'write_material_to_json',
    'write_displacement_rotation',
    'write_load',
    'write_section_response_displacement',
    'write_section_response_load',
    'write_section_response_rotation',
]
