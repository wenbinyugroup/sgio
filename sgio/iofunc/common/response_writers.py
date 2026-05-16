from __future__ import annotations

from typing import Sequence, TextIO

import sgio.utils.io as sui


def write_section_response_displacement(
    file: TextIO,
    displacement: Sequence[float],
    float_format: str = '16.6e',
) -> None:
    """Write sectional displacement data."""

    sui.writeFormatFloats(file, displacement, float_format)
    file.write('\n')


def write_section_response_rotation(
    file: TextIO,
    directional_cosine: Sequence[Sequence[float]],
    float_format: str = '16.6e',
) -> None:
    """Write sectional rotation data as a directional-cosine matrix."""

    sui.writeFormatFloatsMatrix(file, directional_cosine, float_format)
    file.write('\n')


def write_section_response_load(
    file: TextIO,
    load: Sequence[float],
    file_format: str,
    load_type: int = 0,
    distributed_loads: Sequence[Sequence[float]] | None = None,
    int_format: str = '8d',
    float_format: str = '16.6e',
) -> None:
    """Write sectional load data in VABS or SwiftComp-compatible layout."""

    if file_format.lower().startswith('v'):
        if len(load) == 4:
            sui.writeFormatFloats(file, load, float_format)
        elif len(load) == 6:
            sui.writeFormatFloats(file, [load[i] for i in [0, 3, 4, 5]], float_format)
            sui.writeFormatFloats(file, [load[i] for i in [1, 2]], float_format)
            file.write('\n')

            if distributed_loads is None:
                distributed_loads = [[0, 0, 0, 0, 0, 0]] * 4
            for values in distributed_loads:
                sui.writeFormatFloats(file, values, float_format)

    elif file_format.lower().startswith('s'):
        sui.writeFormatIntegers(file, [load_type], int_format)
        sui.writeFormatFloats(file, load, float_format)

    file.write('\n')


__all__ = [
    'write_section_response_displacement',
    'write_section_response_load',
    'write_section_response_rotation',
]
