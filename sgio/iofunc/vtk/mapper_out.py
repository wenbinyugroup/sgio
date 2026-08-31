"""Map sgio mesh data into a VTK/VTU writer payload."""

from __future__ import annotations

from typing import Any

from sgio.core.mesh import SGMesh
from sgio.core.sg import StructureGene


_SUPPORTED_FILE_FORMATS = {"vtk", "vtu"}


def map_model_to_write_payload(model_obj: Any, *, file_format: str) -> dict[str, Any]:
    """Build a validated meshio payload for VTK/VTU export.

    Parameters
    ----------
    model_obj : StructureGene or SGMesh
        Source object. A ``StructureGene`` contributes only its mesh.
    file_format : {"vtk", "vtu"}
        Requested VTK output encoding.

    Returns
    -------
    dict[str, Any]
        Payload containing a meshio mesh and the selected file format.

    Raises
    ------
    TypeError
        If ``model_obj`` is neither a structure gene nor an ``SGMesh``.
    ValueError
        If the mesh is absent or contains data that this mesh-only contract
        cannot represent without loss.
    """
    normalized_format = file_format.lower()
    if normalized_format not in _SUPPORTED_FILE_FORMATS:
        raise ValueError(
            f"Unsupported VTK output format {file_format!r}; "
            f"expected one of {sorted(_SUPPORTED_FILE_FORMATS)}."
        )

    mesh = _extract_mesh(model_obj)
    _validate_mesh_contract(mesh)
    return {"file_format": normalized_format, "mesh": mesh.to_meshio()}


def _extract_mesh(model_obj: Any) -> SGMesh:
    """Extract the ``SGMesh`` accepted by the VTK/VTU writer."""
    if isinstance(model_obj, StructureGene):
        if model_obj.mesh is None:
            raise ValueError("StructureGene.mesh is required for VTK/VTU export.")
        return model_obj.mesh
    if isinstance(model_obj, SGMesh):
        return model_obj
    raise TypeError(
        "VTK/VTU export accepts a StructureGene or SGMesh; "
        f"got {type(model_obj).__name__}."
    )


def _validate_mesh_contract(mesh: SGMesh) -> None:
    """Reject SGMesh containers without a lossless VTK/VTU representation."""
    unsupported_containers = {
        "cell_point_data": mesh.cell_point_data,
        "point_sets": mesh.point_sets,
        "cell_sets": mesh.cell_sets,
    }
    for container_name, value in unsupported_containers.items():
        if value:
            raise ValueError(
                f"VTK/VTU mesh-only export does not support non-empty {container_name}. "
                "Use a Gmsh bundle or explicitly convert the data to point/cell fields."
            )
