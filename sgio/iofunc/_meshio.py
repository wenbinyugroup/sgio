"""
Middle layer between sgio and meshio for customizing mesh I/O functionality.

Overall, this module is similar to meshio._helpers.py.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional, Union, Any, IO

import numpy as np
from numpy.typing import ArrayLike

from meshio._common import (
    num_nodes_per_cell,
    cell_data_from_raw,
    raw_from_cell_data,
    write_xml,
    _pick_first_int_data,
    info,
    warn,
    error,
    is_in_any,
    join_strings,
    replace_space,
)
from meshio._exceptions import ReadError, WriteError
from meshio._helpers import reader_map, _writer_map, extension_to_filetypes
from meshio import Mesh

from sgio.core.mesh import SGMesh

logger = logging.getLogger(__name__)

# Maps for SG-specific readers and writers
sgmesh_reader_map: dict[str, Callable] = {}
sgmesh_writer_map: dict[str, Callable] = {}

# Map of file extensions to format names
sgmesh_ext_to_filetypes: dict[str, list[str]] = {}



def register_sgmesh_format(
    format_name: str, extensions: list[str], reader: Optional[Callable], writer: Optional[Callable]
) -> None:
    """Register a custom SGMesh file format with reader and writer functions.
    
    Parameters
    ----------
    format_name : str
        Name identifier for the file format (e.g., 'vabs', 'swiftcomp').
    extensions : list of str
        List of file extensions associated with this format (e.g., ['.vab', '.dat']).
    reader : callable or None
        Function to read files in this format. Should accept file object and return SGMesh.
    writer : callable or None
        Function to write files in this format. Should accept file object and SGMesh.
        
    Examples
    --------
    >>> def my_reader(f): return SGMesh(...)
    >>> def my_writer(f, mesh): ...
    >>> register_sgmesh_format('custom', ['.cst'], my_reader, my_writer)
    """
    for ext in extensions:
        if ext not in sgmesh_ext_to_filetypes:
            sgmesh_ext_to_filetypes[ext] = []
        sgmesh_ext_to_filetypes[ext].append(format_name)

    if reader is not None:
        sgmesh_reader_map[format_name] = reader

    if writer is not None:
        sgmesh_writer_map[format_name] = writer


def read_sgmesh_buffer(file: IO, file_format: Optional[str], **kwargs) -> Union[SGMesh, Mesh, None]:
    """Read mesh data from a file buffer using specified format.

    Parameters
    ----------
    file : file-like object
        The file buffer to read from (must support read operations).
    file_format : str or None
        Format identifier (e.g., 'vabs', 'gmsh'). Required when reading from buffer.
    **kwargs : dict
        Additional keyword arguments passed to the format-specific reader function.

    Returns
    -------
    SGMesh or Mesh or None
        The mesh data read from file. Returns SGMesh for SG-specific formats,
        meshio.Mesh for standard formats, or None if reading fails.
        
    Raises
    ------
    ValueError
        If file_format is None or if the format is not recognized.
        
    Examples
    --------
    >>> with open('mesh.vab', 'r') as f:
    ...     mesh = read_sgmesh_buffer(f, 'vabs')
    """

    if file_format is None:
        raise ValueError("File format must be given if buffer is used")

    reader = None

    try:
        reader = sgmesh_reader_map[file_format]
    except KeyError:
        try:
            reader = reader_map[file_format]  # meshio reader
        except KeyError:
            raise ValueError(f"Unknown file format '{file_format}'")

    return reader(file, **kwargs)




def write_sgmesh_buffer(file: IO, mesh: SGMesh, file_format: Optional[str], **kwargs) -> None:
    """Write mesh data to a file buffer using specified format.

    Parameters
    ----------
    file : file-like object
        The file buffer to write to (must support write operations).
    mesh : SGMesh
        The mesh data to write.
    file_format : str or None
        Format identifier (e.g., 'vabs', 'gmsh'). Required when writing to buffer.
    **kwargs : dict
        Additional keyword arguments passed to the format-specific writer function.
        
    Raises
    ------
    ValueError
        If file_format is None or if the format is not recognized.
        
    Examples
    --------
    >>> mesh = SGMesh(points=..., cells=...)
    >>> with open('output.vab', 'w') as f:
    ...     write_sgmesh_buffer(f, mesh, 'vabs')
    """

    if file_format is None:
        raise ValueError("File format must be given if buffer is used")

    writer = None

    try:
        writer = sgmesh_writer_map[file_format]
    except KeyError:
        try:
            writer = _writer_map[file_format]  # meshio writer
        except KeyError:
            raise ValueError(f"Unknown file format '{file_format}'")

    return writer(file, mesh, **kwargs)



def add_point_dict_data_to_mesh(name: Union[str, list], dict_data: dict[int, list], mesh: SGMesh) -> None:
    """Add point/node data from dictionary to mesh.point_data.

    Parameters
    ----------
    name : str or list of str
        Name(s) of the point data fields to add.
        If list, must match the length of data values per node.
    dict_data : dict[int, list]
        Mapping from node ID to data values.
        Format: {node_id: value} for single component or {node_id: [val1, val2, ...]} for multiple.
    mesh : SGMesh
        Target mesh object. Data will be added to mesh.point_data attribute.
        
    Notes
    -----
    Node IDs in dict_data are 1-indexed, but will be converted to 0-indexed for mesh storage.
    
    Examples
    --------
    >>> # Single component
    >>> data = {1: 1.5, 2: 2.5, 3: 3.5}
    >>> add_point_dict_data_to_mesh('temperature', data, mesh)
    
    >>> # Multiple components
    >>> data = {1: [1.0, 2.0], 2: [3.0, 4.0]}
    >>> add_point_dict_data_to_mesh(['u', 'v'], data, mesh)
    """

    npoints = len(mesh.points)

    if isinstance(name, str):
        _point_data = []
        for _i in range(npoints):
            _nid = _i + 1
            _data = dict_data[_nid]
            _point_data.append(_data)
        mesh.point_data[name] = np.array(_point_data)

    elif isinstance(name, list):
        ncomps = len(name)
        _point_data_all = []
        for _i in range(ncomps):
            _point_data_all.append([])

        for _i in range(npoints):
            _nid = _i + 1
            _data = dict_data[_nid]
            for _j in range(ncomps):
                _point_data_all[_j].append(_data[_j])

        for _i, _name in enumerate(name):
            _data = _point_data_all[_i]
            mesh.point_data[_name] = np.array(_data)




def _is_element_node_data(dict_data: dict[int, list]) -> bool:
    """Check if data structure represents element-node data (nested) or element data (flat)."""
    first_eid = next(iter(dict_data))
    first_data = dict_data[first_eid]
    return isinstance(first_data, list) and len(first_data) > 0 and isinstance(first_data[0], list)


def _add_single_component_cell_data(name: str, dict_data: dict[int, list], cell_data_eid: list) -> list:
    """Build cell data array for a single component."""
    cell_data = []
    for typei_ids in cell_data_eid:
        typei_data = []
        for eid in typei_ids:
            typei_data.append(dict_data[eid])
        cell_data.append(typei_data)
    return cell_data


def _add_multi_component_cell_data(names: list, dict_data: dict[int, list], cell_data_eid: list) -> dict:
    """Build cell data arrays for multiple components."""
    ncomps = len(names)
    cell_data_all = [[] for _ in range(ncomps)]

    for typei_ids in cell_data_eid:
        typei_data_all = [[] for _ in range(ncomps)]

        for eid in typei_ids:
            data_all = dict_data[eid]
            for k, data in enumerate(data_all):
                typei_data_all[k].append(data)

        for l in range(ncomps):
            cell_data_all[l].append(typei_data_all[l])

    return {name: cell_data_all[i] for i, name in enumerate(names)}


def add_cell_dict_data_to_mesh(name: Union[str, list], dict_data: dict[int, list], mesh: SGMesh) -> None:
    """Add cell/element data from dictionary to mesh.cell_data or mesh.cell_point_data.

    Automatically detects data type (element vs element-node) and adds to appropriate attribute.
    The mesh must contain 'element_id' in cell_data for mapping.

    Parameters
    ----------
    name : str or list of str
        Name(s) of the cell data fields to add.
        If list, must match the number of components in the data.
    dict_data : dict[int, list or list of list]
        Mapping from element ID to data values.
        For element data (flat): {eid: [comp1, comp2, ...]}
        For element-node data (nested): {eid: [[comp1_n1, comp2_n1, ...], [comp1_n2, comp2_n2, ...], ...]}
    mesh : SGMesh
        Target mesh object. Must have mesh.cell_data['element_id'] defined.

    Notes
    -----
    - Element data (flat lists) → added to mesh.cell_data
    - Element-node data (nested lists) → added to mesh.cell_point_data
    - Detection is automatic based on first element's data structure
    
    Examples
    --------
    >>> # Element data (one value per element)
    >>> data = {1: [100.0], 2: [200.0]}
    >>> add_cell_dict_data_to_mesh('material_id', data, mesh)
    
    >>> # Element-node data (values at each node of each element)
    >>> data = {1: [[1.0, 2.0], [3.0, 4.0]], 2: [[5.0, 6.0], [7.0, 8.0]]}
    >>> add_cell_dict_data_to_mesh(['stress_x', 'stress_y'], data, mesh)
    """
    cell_data_eid = mesh.cell_data['element_id']

    # Detect and route to appropriate handler
    if _is_element_node_data(dict_data):
        _add_cell_point_dict_data_to_mesh(name, dict_data, mesh)
        return

    # Add element data to cell_data
    if isinstance(name, str):
        mesh.cell_data[name] = _add_single_component_cell_data(name, dict_data, cell_data_eid)
    elif isinstance(name, list):
        result = _add_multi_component_cell_data(name, dict_data, cell_data_eid)
        for field_name, data in result.items():
            mesh.cell_data[field_name] = data


def _build_single_component_cell_point_data(dict_data: dict[int, list], cell_data_eid: list) -> list:
    """Build cell point data array for a single component (all values together)."""
    cell_point_data = []
    for typei_ids in cell_data_eid:
        typei_data = []
        for eid in typei_ids:
            typei_data.append(dict_data[eid])
        cell_point_data.append(np.array(typei_data))
    return cell_point_data


def _build_multi_component_cell_point_data(names: list, dict_data: dict[int, list], cell_data_eid: list) -> dict:
    """Build cell point data arrays for multiple components (transposed structure)."""
    result = {}
    for comp_idx, comp_name in enumerate(names):
        cell_point_data = []
        for typei_ids in cell_data_eid:
            typei_data = []
            for eid in typei_ids:
                elem_node_data = dict_data[eid]
                comp_values = [node_data[comp_idx] for node_data in elem_node_data]
                typei_data.append(comp_values)
            cell_point_data.append(np.array(typei_data))
        result[comp_name] = cell_point_data
    return result


def _add_cell_point_dict_data_to_mesh(name: Union[str, list], dict_data: dict[int, list], mesh: SGMesh) -> None:
    """Add element-node (cell point) data from dictionary to mesh.cell_point_data.

    Helper function for adding nodal values per element to mesh.
    The mesh must contain 'element_id' in cell_data for mapping.

    Parameters
    ----------
    name : str or list of str
        Name(s) of the cell point data fields to add.
        If list, must match the number of components per node.
    dict_data : dict[int, list of list]
        Mapping from element ID to node-wise data.
        Format: {eid: [[comp1_n1, comp2_n1, ...], [comp1_n2, comp2_n2, ...], ...]}
        Each element maps to a list of nodes, each node has component values.
    mesh : SGMesh
        Target mesh object. Must have mesh.cell_data['element_id'] defined.
        
    Notes
    -----
    This is a private helper function called by add_cell_dict_data_to_mesh.
    Data structure is transposed when multiple component names are provided.
    
    Examples
    --------
    >>> # Single field name (all components together)
    >>> data = {1: [[1.0, 2.0], [3.0, 4.0]]}  # 2 nodes, 2 components each
    >>> _add_cell_point_dict_data_to_mesh('displacement', data, mesh)
    
    >>> # Multiple field names (components separated)
    >>> data = {1: [[1.0, 2.0], [3.0, 4.0]]}  # 2 nodes, 2 components each
    >>> _add_cell_point_dict_data_to_mesh(['disp_x', 'disp_y'], data, mesh)
    """
    cell_data_eid = mesh.cell_data['element_id']

    if isinstance(name, str):
        mesh.cell_point_data[name] = _build_single_component_cell_point_data(dict_data, cell_data_eid)
    elif isinstance(name, list):
        result = _build_multi_component_cell_point_data(name, dict_data, cell_data_eid)
        for field_name, data in result.items():
            mesh.cell_point_data[field_name] = data




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




# def _meshio_to_sg_order(cell_type:str, idx:ArrayLike):
#     idx_sg = np.asarray(idx) + 1

#     idx_to_insert = None
#     if cell_type == 'triangle6':
#         idx_to_insert = 3
#     elif cell_type == 'tetra10':
#         idx_to_insert = 4
#     elif cell_type == 'wedge15':
#         idx_to_insert = 6

#     max_nodes = idx_sg.shape[1]
#     if cell_type.startswith('line'):
#         max_nodes = 5
#     elif cell_type.startswith('triangle') or cell_type.startswith('quad'):
#         max_nodes = 9
#     elif cell_type.startswith('tetra') or cell_type.startswith('wedge') or cell_type.startswith('hexahedron'):
#         max_nodes = 20

#     # Insert 0 for some types of cells
#     if idx_to_insert:
#         idx_sg = np.insert(idx_sg, idx_to_insert, 0, axis=1)

#     # Fill the remaining location with 0s
#     pad_width = max_nodes - idx_sg.shape[1]
#     # logger.debug('pad width = {}'.format(pad_width))
#     idx_sg = np.pad(idx_sg, ((0, 0), (0, pad_width)), 'constant', constant_values=0)

#     return idx_sg




# ====================================================================
# Writers


def _write_nodes(
    f: IO, points: np.ndarray, sgdim: int, node_id: list[int] = [], model_space: str = '',
    renumber_nodes: bool = False,
    int_fmt: str = '8d', float_fmt: str = '20.9e'
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
        List of original node IDs. If empty, nodes are numbered sequentially.
    model_space : str, optional
        Coordinate plane for lower dimensions:
        - For sgdim=1: 'x', 'y', or 'z'
        - For sgdim=2: 'xy', 'yz', or 'zx'
        - For sgdim=3: ignored
    renumber_nodes : bool, optional
        If True, override node_id and use sequential numbering (1, 2, 3, ...).
        Default is False.
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
    - Writes one node per line with format: node_id coord1 [coord2] [coord3]
    - First line includes comment "! nodal coordinates"
    """
    sfi = '{:' + int_fmt + '}'
    sff = ''.join(['{:' + float_fmt + '}', ]*sgdim)

    # print(sfi)
    # print(sff)

    for i, ncoord in enumerate(points):
        if renumber_nodes:
            nid = i + 1
        else:
            if len(node_id) > 0:
                nid = node_id[i]
            else:
                nid = i + 1
        f.write(sfi.format(nid))  # node id

        # logger.debug(ncoord)

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
    node_id: list[int] = [], renumber_nodes: bool = True
) -> np.ndarray:
    """Convert meshio cell connectivity to SG format with padding and reordering.

    Parameters
    ----------
    cell_type : str
        Cell type identifier (e.g., 'triangle6', 'tetra10', 'wedge15').
    idx : array-like
        2D array of cell connectivity with shape (n_cells, n_elem_nodes).
        Contains original node indices (0-indexed or from node_id).
    node_id : list of int, optional
        Array of original node IDs for mapping. If empty and renumber_nodes=True,
        uses sequential 1-based numbering.
    renumber_nodes : bool, optional
        If True, convert to 1-based node IDs. Default is True.

    Returns
    -------
    np.ndarray
        2D array of cell connectivity in SG format with shape (n_cells, max_nodes_sg).
        Includes zero-padding and special zero-insertion for certain element types.
        
    Notes
    -----
    - SG format uses fixed-width cell connectivity with zero-padding
    - Some elements (triangle6, tetra10, wedge15) insert a zero at specific position
    - Maximum nodes per cell: line=5, triangle/quad=9, tetra/wedge/hex=20
    """
    idx_sg = np.asarray(idx)
    if renumber_nodes:
        if len(node_id) == 0:
            idx_sg = np.asarray(idx) + 1
        else:
            idx_map = {v: i+1 for i, v in enumerate(node_id)}
            idx_sg = np.vectorize(idx_map.get)(idx_sg)

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


