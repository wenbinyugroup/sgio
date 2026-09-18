"""SwiftComp input parser."""

from __future__ import annotations

from typing import Any, TextIO

from sgio.utils.io import fortran_float

from ._input import (
    _readHeader,
    _readMaterialRotationCombinations,
    _readMaterials,
    _readMesh,
)
from .keywords import resolve_model_dimension


def parse_input_buffer(
    file: TextIO,
    format_version: str,
    model: int | str,
) -> dict[str, Any]:
    """Parse a SwiftComp input buffer into a raw intermediate payload."""
    smdim = resolve_model_dimension(model)
    configs = _readHeader(file, format_version, smdim)
    mesh = _readMesh(
        file,
        sgdim=configs["sgdim"],
        nnode=configs["num_nodes"],
        nelem=configs["num_elements"],
        read_local_frame=configs.get("use_elem_local_orient", 0),
    )
    material_rotation_combinations = _readMaterialRotationCombinations(
        file,
        configs["num_mat_angle3_comb"],
    )
    materials, material_id_pairs = _readMaterials(
        file,
        configs["num_materials"],
        configs["physics"],
    )
    omega = _read_omega(file)

    return {
        "format_version": format_version,
        "model": model,
        "smdim": smdim,
        "configs": configs,
        "mesh": mesh,
        "material_rotation_combinations": material_rotation_combinations,
        "materials": materials,
        "material_id_pairs": material_id_pairs,
        "omega": omega,
    }


def _read_omega(file: TextIO) -> float:
    """Read omega, the last record of a SwiftComp input file."""
    for line in file:
        line = line.split('!')[0].strip()
        if line:
            return fortran_float(line.split()[0])
    raise ValueError("SwiftComp input ends before the omega record.")
