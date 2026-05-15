"""VABS input parser.

This module is responsible only for parsing VABS input text into a raw
intermediate payload. It does not construct application-layer IR objects.
"""

from __future__ import annotations

from typing import Any, TextIO

from ._input import (
    _readHeader,
    _readMaterialRotationCombinations,
    _readMaterials,
    _readMesh,
)


def parse_input_buffer(file: TextIO, format_version: str) -> dict[str, Any]:
    """Parse a VABS input buffer into a raw intermediate payload.

    Parameters
    ----------
    file : TextIO
        Open VABS input buffer.
    format_version : str
        Caller-provided VABS format version.

    Returns
    -------
    dict[str, Any]
        Raw parsed payload containing header config, mesh, temporary
        material-angle combinations, and material reader state.
    """
    configs = _readHeader(file)
    mesh = _readMesh(
        file,
        sgdim=configs["sgdim"],
        nnode=configs["num_nodes"],
        nelem=configs["num_elements"],
        format_flag=configs["format"],
    )
    material_rotation_combinations = _readMaterialRotationCombinations(
        file,
        configs["num_mat_angle3_comb"],
    )
    materials, material_id_pairs = _readMaterials(file, configs["num_materials"])

    return {
        "format_version": format_version,
        "configs": configs,
        "mesh": mesh,
        "material_rotation_combinations": material_rotation_combinations,
        "materials": materials,
        "material_id_pairs": material_id_pairs,
    }
