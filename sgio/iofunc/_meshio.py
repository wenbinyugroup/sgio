"""SG-format common parsers.

This module hosts low-level text parsing/writing helpers shared between the
VABS and SwiftComp adapters (``_read_nodes`` / ``_write_nodes`` /
``_sg_to_meshio_order`` / ``_meshio_to_sg_order``). They are scheduled to
move to ``iofunc/sg_common/`` (or each adapter's ``parser.py``) when Phase 8
splits adapters internally.

The two public helpers ``add_point_dict_data_to_mesh`` /
``add_cell_dict_data_to_mesh`` remain here as thin backward-compatible shims;
the real implementation lives on :class:`SGMesh` as instance methods
(``add_point_data_from_dict`` / ``add_cell_data_from_dict``).
"""
from __future__ import annotations

import logging
from typing import Union, IO

import numpy as np
from numpy.typing import ArrayLike

from sgio.core.mesh import SGMesh


logger = logging.getLogger(__name__)


def is_buffer(obj, mode: str) -> bool:
    """Return True if ``obj`` is a file-like buffer compatible with ``mode``."""
    return ("r" in mode and hasattr(obj, "read")) or (
        "w" in mode and hasattr(obj, "write")
    )


def add_point_dict_data_to_mesh(
    name: Union[str, list],
    dict_data: dict[int, list],
    mesh: SGMesh,
) -> None:
    """Backward-compatible shim. Delegates to :meth:`SGMesh.add_point_data_from_dict`."""
    mesh.add_point_data_from_dict(name, dict_data)


def add_cell_dict_data_to_mesh(
    name: Union[str, list],
    dict_data: dict[int, list],
    mesh: SGMesh,
) -> None:
    """Backward-compatible shim. Delegates to :meth:`SGMesh.add_cell_data_from_dict`."""
    mesh.add_cell_data_from_dict(name, dict_data)


# ====================================================================
# Readers


def _read_nodes(f: IO, nnodes: int, sgdim: int = 3) -> tuple[np.ndarray, dict[int, int], str]:
    """Read node coordinates from SG format file.
    
    Parameters
    ----------
    f : file-like object
        File buffer to read from (must support readline).
    nnodes : int
        Number of nodes to read.
    sgdim : int, optional
        Spatial dimension (1, 2, or 3), default is 3.
        
    Returns
    -------
    points : np.ndarray
        Array of node coordinates with shape (nnodes, 3).
        Coordinates are padded with 0.0 for dimensions < 3.
    point_ids : dict[int, int]
        Mapping from original node ID to 0-indexed array position.
    line : str
        Last line read (for continued parsing).
        
    Notes
    -----
    - Skips comment lines (lines starting with '!' or empty lines)
    - Node IDs can be non-sequential
    - Returned points are always 3D (padded with zeros if sgdim < 3)
    """
    points = []
    point_ids = {}
    counter = 0
    line = ""
    while counter < nnodes:
        line = f.readline()
        line = line.split('!')[0].strip()
        if line == "":
            continue

        line = line.strip().split()
        point_id, coords = line[0], line[1:]
        point_ids[int(point_id)] = counter
        points.append([0.0,]*(3-sgdim)+[float(x) for x in coords])
        counter += 1

    return np.array(points, dtype=float), point_ids, " ".join(line) if isinstance(line, list) else line




def _sg_to_meshio_order(cell_type: str, idx: ArrayLike) -> np.ndarray:
    """Convert SG cell node ordering to meshio/VTK ordering.
    
    Parameters
    ----------
    cell_type : str
        Cell type identifier (e.g., 'tetra10', 'hexahedron20', 'wedge15').
    idx : array-like
        Array of node indices in SG ordering.
        
    Returns
    -------
    np.ndarray
        Array of node indices reordered to meshio/VTK convention.
        If cell_type is not in the mapping, returns original ordering.
        
    Notes
    -----
    Only certain higher-order cell types require reordering.
    Linear elements (tetra4, hex8, etc.) use the same ordering.
    """
    # TODO: Verify ordering against latest meshio/VTK specifications
    # Gmsh cells are mostly ordered like VTK, with a few exceptions:
    meshio_ordering = {
        # fmt: off
        "tetra10": [0, 1, 2, 3, 4, 5, 6, 7, 9, 8],
        "hexahedron20": [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 13,
            9, 16, 18, 19, 17, 10, 12, 14, 15,
        ],  # https://vtk.org/doc/release/4.2/html/classvtkQuadraticHexahedron.html and https://gmsh.info/doc/texinfo/gmsh.html#Node-ordering
        "hexahedron27": [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 13,
            9, 16, 18, 19, 17, 10, 12, 14, 15,
            22, 23, 21, 24, 20, 25, 26,
        ],
        "wedge15": [
            0, 1, 2, 3, 4, 5, 6, 9, 7, 12, 14, 13, 8, 10, 11
        ],  # http://davis.lbl.gov/Manuals/VTK-4.5/classvtkQuadraticWedge.html and https://gmsh.info/doc/texinfo/gmsh.html#Node-ordering
        "pyramid13": [0, 1, 2, 3, 4, 5, 8, 10, 6, 7, 9, 11, 12],
        # fmt: on
    }
    idx = np.asarray(idx)
    if cell_type not in meshio_ordering:
        return idx
    return idx[:, meshio_ordering[cell_type]]







# ====================================================================
# Writers


def _write_nodes(
    f: IO, points: np.ndarray, sgdim: int, node_id: list[int] = [],
    model_space: str = '', int_fmt: str = '8d', float_fmt: str = '20.9e'
) -> None:
    """Write node coordinates to SG format file.

    Parameters
    ----------
    f : file-like object
        File buffer to write to (must support write operations).
    points : np.ndarray
        Array of node coordinates with shape (n_nodes, 3).
    sgdim : int
        Spatial dimension (1, 2, or 3) to write.
    node_id : list of int, optional
        List of original node IDs. If empty, nodes are numbered sequentially
        from 1.
    model_space : str, optional
        Coordinate plane for lower dimensions:
        - For sgdim=1: 'x', 'y', or 'z'
        - For sgdim=2: 'xy', 'yz', or 'zx'
        - For sgdim=3: ignored
    int_fmt : str, optional
        Format string for integer node IDs (default '8d').
    float_fmt : str, optional
        Format string for float coordinates (default '20.9e').

    Raises
    ------
    ValueError
        If model_space is invalid for the given sgdim.

    Notes
    -----
    Writes one node per line with format: node_id coord1 [coord2] [coord3].
    First line includes comment "! nodal coordinates".
    """
    sfi = '{:' + int_fmt + '}'
    sff = ''.join(['{:' + float_fmt + '}', ] * sgdim)

    for i, ncoord in enumerate(points):
        nid = node_id[i] if len(node_id) > 0 else i + 1
        f.write(sfi.format(nid))  # node id

        if sgdim == 1:
            if model_space == 'x':
                f.write(sff.format(ncoord[0]))
            elif model_space == 'y':
                f.write(sff.format(ncoord[1]))
            elif model_space == 'z':
                f.write(sff.format(ncoord[2]))
            else:
                raise ValueError(f"Invalid model space: {model_space}")

        elif sgdim == 2:
            if model_space == 'xy':
                f.write(sff.format(ncoord[0], ncoord[1]))
            elif model_space == 'yz':
                f.write(sff.format(ncoord[1], ncoord[2]))
            elif model_space == 'zx':
                f.write(sff.format(ncoord[2], ncoord[0]))
            else:
                raise ValueError(f"Invalid model space: {model_space}")

        elif sgdim == 3:
            f.write(sff.format(*ncoord))

        # Add comment
        if i == 0:
            f.write('  ! nodal coordinates')

        f.write('\n')

    f.write('\n')




def _meshio_to_sg_order(
    cell_type: str, idx: ArrayLike,
    node_id: list[int] = []
) -> np.ndarray:
    """Convert meshio cell connectivity to SG format with padding and reordering.

    Parameters
    ----------
    cell_type : str
        Cell type identifier (e.g., 'triangle6', 'tetra10', 'wedge15').
    idx : array-like
        2D array of cell connectivity with shape (n_cells, n_elem_nodes).
        Contains 0-based point indices into the mesh points array.
    node_id : list of int, optional
        Array of node IDs (one per mesh point). If provided, point indices are
        mapped to the corresponding node IDs. If empty, sequential 1-based IDs
        (``idx + 1``) are used.

    Returns
    -------
    np.ndarray
        2D array of cell connectivity in SG format with shape (n_cells, max_nodes_sg).
        Includes zero-padding and special zero-insertion for certain element types.

    Notes
    -----
    - SG format uses fixed-width cell connectivity with zero-padding.
    - Some elements (triangle6, tetra10, wedge15) insert a zero at a specific position.
    - Maximum nodes per cell: line=5, triangle/quad=9, tetra/wedge/hex=20.
    """
    idx_sg = np.asarray(idx, dtype=int)
    # Map 0-based point indices to 1-based SG node IDs.
    if len(node_id) == 0:
        idx_sg = idx_sg + 1
    else:
        idx_sg = np.asarray(node_id, dtype=int).reshape(-1)[idx_sg]

    idx_to_insert = None
    if cell_type == 'triangle6':
        idx_to_insert = 3
    elif cell_type == 'tetra10':
        idx_to_insert = 4
    elif cell_type == 'wedge15':
        idx_to_insert = 6

    max_nodes = idx_sg.shape[1]
    if cell_type.startswith('line'):
        max_nodes = 5
    elif cell_type.startswith('triangle') or cell_type.startswith('quad'):
        max_nodes = 9
    elif cell_type.startswith('tetra') or cell_type.startswith('wedge') or cell_type.startswith('hexahedron'):
        max_nodes = 20

    # Insert 0 for some types of cells
    if idx_to_insert:
        idx_sg = np.insert(idx_sg, idx_to_insert, 0, axis=1)

    # Fill the remaining location with 0s
    pad_width = max_nodes - idx_sg.shape[1]
    # logger.debug('pad width = {}'.format(pad_width))
    idx_sg = np.pad(idx_sg, ((0, 0), (0, pad_width)), 'constant', constant_values=0)

    return idx_sg


