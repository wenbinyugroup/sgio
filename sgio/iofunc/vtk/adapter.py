"""Write-only VTK/VTU format adapter."""

from __future__ import annotations

from os import PathLike
from typing import Any

from ..base import BaseFormatWriter

from .mapper_out import map_model_to_write_payload
from .writer import write_input_payload


_SUPPORTED_FILE_FORMATS = {"vtk", "vtu"}


class VtkWriter(BaseFormatWriter):
    """Write ``SGMesh`` geometry and mesh-bound fields to VTK or VTU.

    This adapter deliberately has no companion reader. It exports only data
    represented by a mesh: points, cells, point data, and cell data.

    Parameters
    ----------
    file_format : {"vtk", "vtu"}
        meshio output format owned by this writer instance.
    """

    def __init__(self, file_format: str) -> None:
        """Initialize a writer for one supported VTK output format."""
        normalized_format = file_format.lower()
        if normalized_format not in _SUPPORTED_FILE_FORMATS:
            raise ValueError(
                f"Unsupported VTK output format {file_format!r}; "
                f"expected one of {sorted(_SUPPORTED_FILE_FORMATS)}."
            )
        super().__init__(normalized_format)
        self._file_format = normalized_format

    def write_input(
        self,
        destination: str | PathLike[str],
        model_obj: Any,
        *,
        binary: bool = True,
        **kwargs: Any,
    ) -> None:
        """Write one mesh-only VTK/VTU file.

        Parameters
        ----------
        destination : str or os.PathLike
            Filesystem output path. meshio's VTU writer does not support
            file-like objects.
        model_obj : StructureGene or SGMesh
            Object that owns the mesh to export.
        binary : bool, optional
            Write meshio's binary representation when supported.
        **kwargs : Any
            Accepted for the common writer interface and ignored.
        """
        if not isinstance(destination, (str, PathLike)):
            raise TypeError("VTK/VTU export requires a filesystem path, not a file-like object.")
        payload = map_model_to_write_payload(model_obj, file_format=self._file_format)
        write_input_payload(destination, payload, binary=binary)

    def validate(self, model_obj: Any) -> bool:
        """Return whether ``model_obj`` satisfies the mesh-only writer contract."""
        try:
            map_model_to_write_payload(model_obj, file_format=self._file_format)
        except (TypeError, ValueError):
            return False
        return True
