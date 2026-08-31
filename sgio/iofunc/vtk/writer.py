"""Low-level meshio-backed VTK/VTU writer."""

from __future__ import annotations

from os import PathLike
from typing import Any


def write_input_payload(
    destination: str | PathLike[str],
    payload: dict[str, Any],
    *,
    binary: bool = True,
) -> None:
    """Write a normalized VTK/VTU payload through meshio.

    Parameters
    ----------
    destination : str or os.PathLike
        Filesystem output path accepted by meshio.
    payload : dict[str, Any]
        Validated payload from :func:`map_model_to_write_payload`.
    binary : bool, optional
        Write meshio's binary representation when supported.
    """
    import meshio

    meshio.write(
        destination,
        payload["mesh"],
        file_format=payload["file_format"],
        binary=binary,
    )
