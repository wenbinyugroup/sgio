from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from meshio.gmsh.common import (
    c_int,
    c_double,
    _fast_forward_over_blank_lines,
    _fast_forward_to_end_block,
    _gmsh_to_meshio_order,
    _gmsh_to_meshio_type,
    _meshio_to_gmsh_order,
    _meshio_to_gmsh_type,
    _read_data,
    _read_physical_names,
    _write_physical_names,
)
from meshio._common import (
    num_nodes_per_cell,
    cell_data_from_raw,
    warn,
)
from meshio._exceptions import WriteError

from sgio.core.property_ref_csys import resolve_element_local_csys

if TYPE_CHECKING:
    from sgio.core.mesh import CellBlock


def _to_ascii_scalar(value):
    """Convert NumPy/Python scalars to plain ASCII-safe values."""
    if isinstance(value, np.generic):
        return value.item()
    return value


def _write_data(fh, tag, name, data, binary):
    if binary:
        fh.write(f"${tag}\n".encode())
    else:
        fh.write(f"${tag}\n")
    # <http://gmsh.info/doc/texinfo/gmsh.html>:
    # > Number of string tags.
    # > gives the number of string tags that follow. By default the first
    # > string-tag is interpreted as the name of the post-processing view and
    # > the second as the name of the interpolation scheme. The interpolation
    # > scheme is provided in the $InterpolationScheme section (see below).
    if binary:
        fh.write(f"{1}\n".encode())
        fh.write(f'"{name}"\n'.encode())
        fh.write(f"{1}\n".encode())
        fh.write(f"{0.0}\n".encode())
        # three integer tags:
        fh.write(f"{3}\n".encode())
        # time step
        fh.write(f"{0}\n".encode())
    else:
        fh.write(f"{1}\n")
        fh.write(f'"{name}"\n')
        fh.write(f"{1}\n")
        fh.write(f"{0.0}\n")
        # three integer tags:
        fh.write(f"{3}\n")
        # time step
        fh.write(f"{0}\n")

    # number of components
    num_components = data.shape[1] if len(data.shape) > 1 else 1
    if num_components not in [1, 3, 9]:
        raise WriteError("Gmsh only permits 1, 3, or 9 components per data field.")

    # Cut off the last dimension in case it's 1. This avoids problems with
    # writing the data.
    if len(data.shape) > 1 and data.shape[1] == 1:
        data = data[:, 0]

    if binary:
        fh.write(f"{num_components}\n".encode())
        # num data items
        fh.write(f"{data.shape[0]}\n".encode())
        # actually write the data
        if num_components == 1:
            dtype = [("index", c_int), ("data", c_double)]
        else:
            dtype = [("index", c_int), ("data", c_double, num_components)]
        tmp = np.empty(len(data), dtype=dtype)
        tmp["index"] = 1 + np.arange(len(data))
        tmp["data"] = data
        tmp.tofile(fh)
        fh.write(b"\n")
        fh.write(f"$End{tag}\n".encode())
    else:
        fh.write(f"{num_components}\n")
        # num data items
        fh.write(f"{data.shape[0]}\n")
        # actually write the data
        if num_components == 1:
            for k, x in enumerate(data):
                fh.write(f"{k + 1} {_to_ascii_scalar(x)}\n")
        else:
            for k, x in enumerate(data):
                values = " ".join(str(_to_ascii_scalar(i)) for i in x)
                fh.write(f"{k + 1} {values}\n")
        fh.write(f"$End{tag}\n")



def write_element_node_data(file, name, data):
    file.write(f"$ElementNodeData\n")

    file.write(f"{1}\n")  # 1 string tag
    file.write(f'"{name}"\n')

    file.write(f"{1}\n")  # 1 real tag
    file.write(f"{0.0}\n")

    file.write(f"{3}\n")  # 3 integer tags
    file.write(f"{0}\n")  # time step
    file.write(f"{1}\n")  # number of components
    file.write(f"{len(data)}\n")  # num data items

    for _eid, _nvals in data.items():
        file.write(f'{_eid} {len(_nvals)}')
        for _v in _nvals:
            file.write(f'  {_v}')
        file.write('\n')

    file.write(f"$EndElementNodeData\n")


def build_geometrical_tags(
    mesh,
    property_id: list[np.ndarray],
) -> list[np.ndarray]:
    """Create default geometrical tags for non-Gmsh section data."""
    geometrical_data: list[np.ndarray] = []

    for block_index, array in enumerate(property_id, start=1):
        block_values = np.asarray(array, dtype=np.int32)
        if np.any(block_values != 0):
            geometrical_data.append(block_values.copy())
        else:
            geometrical_data.append(np.full(block_values.shape, block_index, dtype=np.int32))

    return geometrical_data


def _normalize_local_coordinate_fields(
    cell_data: dict[str, list[np.ndarray]],
    cells: list[CellBlock],
) -> None:
    """Populate canonical and compatibility local-csys fields on read."""
    normalized = resolve_element_local_csys(cell_data, cells)
    if normalized is None:
        return

    cell_data["element_local_csys"] = normalized
    cell_data["property_ref_csys"] = [block.copy() for block in normalized]


def normalize_additional_rotation_fields(
    cell_data: dict[str, list[np.ndarray]],
    cells: list[CellBlock],
) -> None:
    """Populate canonical additional-rotation fields, promoting the legacy
    ``additional_rotation`` field to ``additional_rotation_1`` if needed.

    Shared by the Gmsh reader (``finalize_sg_cell_data``) and writer
    (``_prepare_gmsh41_mesh``) so both accept the same legacy input shape.
    """
    rotation_1 = cell_data.get("additional_rotation_1")
    rotation_2 = cell_data.get("additional_rotation_2")
    rotation_3 = cell_data.get("additional_rotation_3")
    legacy_rotation = cell_data.get("additional_rotation")

    if rotation_1 is None and legacy_rotation is not None:
        rotation_1 = [np.asarray(block, dtype=float) for block in legacy_rotation]

    if rotation_1 is None and rotation_2 is None and rotation_3 is None:
        return

    reference_blocks = rotation_1 or rotation_2 or rotation_3
    assert reference_blocks is not None

    def _zeros_like_cells() -> list[np.ndarray]:
        return [np.zeros(len(cell_block.data), dtype=float) for cell_block in cells]

    cell_data["additional_rotation_1"] = (
        [np.asarray(block, dtype=float) for block in rotation_1]
        if rotation_1 is not None
        else _zeros_like_cells()
    )
    cell_data["additional_rotation_2"] = (
        [np.asarray(block, dtype=float) for block in rotation_2]
        if rotation_2 is not None
        else _zeros_like_cells()
    )
    cell_data["additional_rotation_3"] = (
        [np.asarray(block, dtype=float) for block in rotation_3]
        if rotation_3 is not None
        else _zeros_like_cells()
    )


def finalize_sg_cell_data(
    cell_data: dict[str, list[np.ndarray]],
    cells: list["CellBlock"],
) -> None:
    """Apply SG-specific post-processing to freshly read Gmsh cell data.

    Shared by every MSH-version reader so that local coordinate systems,
    additional rotations and ``property_id`` are resolved identically
    regardless of which ``$MeshFormat`` version the file declares.

    Parameters
    ----------
    cell_data : dict of str to list of numpy.ndarray
        Cell data read from the file, modified in place.
    cells : list of CellBlock
        Cell blocks the data belongs to.
    """
    _normalize_local_coordinate_fields(cell_data, cells)
    normalize_additional_rotation_fields(cell_data, cells)

    # Map gmsh:physical to property_id for compatibility with SGIO.
    # Priority: gmsh:physical > existing property_id from $ElementData > zeros fallback.
    if "gmsh:physical" in cell_data:
        cell_data["property_id"] = cell_data["gmsh:physical"]
    elif "property_id" not in cell_data:
        # No physical groups and no $ElementData property_id — create empty arrays
        warn("No physical groups found in mesh. Creating empty property_id arrays. "
             "Consider using Gmsh physical groups to assign materials.")
        cell_data["property_id"] = [
            np.zeros(len(cell_block.data), dtype=int) for cell_block in cells
        ]
    # else: property_id already populated from $ElementData — keep it
