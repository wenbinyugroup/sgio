from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ...model.solid import CauchyContinuumModel


def write_material_to_json(
    material: CauchyContinuumModel,
    file_path: str,
    *,
    exclude_none: bool = True,
    indent: Optional[int] = None,
) -> None:
    """Write a material model to JSON."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = material.model_dump(exclude_none=exclude_none)

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indent, ensure_ascii=False)


def read_material_from_json(file_path: str) -> dict[str, CauchyContinuumModel]:
    """Read a single material definition from JSON."""

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')

    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise TypeError(f'Expected JSON dictionary for single material, got {type(data).__name__}')

    material = CauchyContinuumModel(**data)
    if not material.name:
        raise ValueError('Material must have a non-empty name field')

    return {material.name: material}


def read_materials_from_json(file_path: str) -> dict[str, CauchyContinuumModel]:
    """Read a list of material definitions from JSON."""

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')

    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise TypeError(f'Expected JSON list for multiple materials, got {type(data).__name__}')

    materials: dict[str, CauchyContinuumModel] = {}
    for index, mat_data in enumerate(data):
        if not isinstance(mat_data, dict):
            raise TypeError(
                f'Material at index {index} is not a dictionary: {type(mat_data).__name__}'
            )

        material = CauchyContinuumModel(**mat_data)
        if not material.name:
            raise ValueError(f'Material at index {index} must have a non-empty name field')
        if material.name in materials:
            raise ValueError(f'Duplicate material name found: {material.name}')

        materials[material.name] = material

    return materials


__all__ = [
    'read_material_from_json',
    'read_materials_from_json',
    'write_material_to_json',
]
