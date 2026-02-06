"""
I/O for SwiftComp format
"""
from __future__ import annotations
import logging
from typing import TextIO, List, Dict, Tuple, Optional, Union

import numpy as np
from meshio._files import is_buffer

from sgio.core.mesh import SGMesh
from sgio.iofunc._meshio import (
    register_sgmesh_format,
    _meshio_to_sg_order,
    _sg_to_meshio_order,
    _read_nodes,
    _write_nodes,
)

logger = logging.getLogger(__name__)

# Element type detection constants
NODE_COUNT_1D = 5  # Node count for 1D elements
NODE_COUNT_2D = 9  # Node count for 2D elements
NODE_COUNT_3D = 20  # Node count for 3D elements
CSYS_MATRIX_SIZE = 9  # Coordinate system transformation matrix size (3x3)


def _determine_element_type(node_ids: List, elem_id: int) -> Tuple[str, List[int]]:
    """Determine element type from node IDs and convert to integers.
    
    Analyzes the node ID list to determine the element type (line, triangle,
    quad, tetra, wedge, hexahedron) and returns the cleaned node IDs.
    
    Parameters
    ----------
    node_ids : list of str
        Raw node IDs from file (may contain '0' placeholders)
    elem_id : int
        Element ID for error reporting
        
    Returns
    -------
    tuple
        A tuple containing:
        - cell_type : str
            Element type string (e.g., 'line', 'triangle', 'quad')
        - node_ids : list of int
            Cleaned node IDs as integers
            
    Raises
    ------
    ValueError
        If node IDs are invalid or element type cannot be determined
    """
    cell_type = ''
    try:
        if len(node_ids) == NODE_COUNT_1D:  # 1d elements
            node_ids = [int(_i) for _i in node_ids if _i != '0']
            if len(node_ids) == 2:
                cell_type = 'line'
            else:
                cell_type = 'line{}'.format(len(node_ids))
        elif len(node_ids) == NODE_COUNT_2D:  # 2d elements
            if node_ids[3] == '0':  # triangle
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {3: 'triangle', 6: 'triangle6'}[len(node_ids)]
            else:  # quadrilateral
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {4: 'quad', 8: 'quad8', 9: 'quad9'}[len(node_ids)]
        elif len(node_ids) == NODE_COUNT_3D:  # 3d elements
            if node_ids[4] == '0':  # tetrahedral
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {4: 'tetra', 10: 'tetra10'}[len(node_ids)]
            elif node_ids[6] == '0':  # wedge
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {6: 'wedge', 15: 'tetra15'}[len(node_ids)]
            else:  # hexahedron
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {8: 'hexahedron', 20: 'hexahedron20'}[len(node_ids)]
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid node IDs or element type for element {elem_id}: {e}")
    
    return cell_type, node_ids


def read_buffer(f: TextIO, sgdim: int, nnode: int, nelem: int, read_local_frame: bool) -> SGMesh:
    """Read SwiftComp mesh data from a file buffer.
    
    Parses a SwiftComp mesh file to extract nodes, elements, and optional
    local coordinate system data. Constructs an SGMesh object with the
    extracted data.
    
    Parameters
    ----------
    f : TextIO
        File buffer object to read from
    sgdim : int
        Spatial dimension of the mesh (1, 2, or 3)
    nnode : int
        Number of nodes to read from the file
    nelem : int
        Number of elements to read from the file
    read_local_frame : bool
        Whether to read local coordinate system data for elements
        
    Returns
    -------
    SGMesh
        Mesh object containing points, cells, and associated data
        
    Raises
    ------
    ValueError
        If file format is invalid or data cannot be parsed
    IOError
        If file reading encounters errors
        
    Examples
    --------
    >>> with open('mesh.sc', 'r') as f:
    ...     mesh = read_buffer(f, sgdim=3, nnode=100, nelem=50, read_local_frame=True)
    """
    # Input validation
    if sgdim not in (1, 2, 3):
        raise ValueError(f"sgdim must be 1, 2, or 3, got {sgdim}")
    if nnode < 0:
        raise ValueError(f"nnode must be non-negative, got {nnode}")
    if nelem < 0:
        raise ValueError(f"nelem must be non-negative, got {nelem}")
    
    logger.debug(f"Reading SwiftComp mesh: sgdim={sgdim}, nnode={nnode}, nelem={nelem}, read_local_frame={read_local_frame}")

    # Initialize the optional data fields
    points = []
    cells = []
    cell_ids = []
    point_sets = {}
    cell_sets = {}
    cell_sets_element = {}  # Handle cell sets defined in ELEMENT
    cell_sets_element_order = []  # Order of keys is not preserved in Python 3.5
    field_data = {}
    cell_data = {}
    point_data = {}
    point_ids = None

    # Read nodes
    points, point_ids, line = _read_nodes(f, nnode, sgdim)

    # Read elements
    cells, elem_ids, prop_ids, cell_ids, line = _read_elements(f, nelem, point_ids)

    # Set element_id cell data
    cell_data['element_id'] = elem_ids

    _cd = []
    for _cb in cells:
        _ct = _cb[0]
        _cd.append(prop_ids[_ct])
    cell_data['property_id'] = _cd

    if read_local_frame:
        # Read local coordinate system for sectional properties
        cell_csys = _read_property_ref_csys(f, nelem, cells, cell_ids)
        cell_data['property_ref_csys'] = cell_csys

    return SGMesh(
        points,
        cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        point_sets=point_sets,
        cell_sets=cell_sets,
    )




def _read_elements(f: TextIO, nelem: int, point_ids: Dict) -> Tuple:
    """Read element connectivity and properties from SwiftComp file.
    
    Parses element definitions from the file, determining element types
    based on node counts and organizing elements by type.
    
    Parameters
    ----------
    f : TextIO
        File buffer object to read from
    nelem : int
        Number of elements to read
    point_ids : dict
        Mapping from file node IDs to internal node IDs
        
    Returns
    -------
    tuple
        A tuple containing:
        - cells : list of tuples
            Element data organized by type [(cell_type, connectivity), ...]
        - elem_ids : list of lists
            Element IDs for each cell type
        - prop_ids : dict
            Property IDs for each cell type
        - cell_ids : dict
            Mapping from element ID to (cell_type_index, element_index)
        - line : str
            Last line read from file
            
    Raises
    ------
    ValueError
        If element format is invalid or node IDs are out of range
    KeyError
        If node IDs are not found in point_ids mapping
"""

    line = ""  # Initialize line variable
    cells = []
    cell_type_to_index = {}
    elem_ids = []  # Element id in the original file; Same shape as cells
    prop_ids = {}  # property id for each element; will update cell_data (swiftcomp)
    cell_ids = {}
    counter = 0
    while counter < nelem:
        line = f.readline().split('#')[0].strip()
        if line == "": continue

        line = line.split()
        elem_id, prop_id, node_ids = line[0], line[1], line[2:]
        try:
            elem_id = int(elem_id)
        except ValueError as e:
            raise ValueError(f"Invalid element ID '{elem_id}' on line {counter + 1}: {e}")

        # Determine element type and convert node IDs
        cell_type, node_ids = _determine_element_type(node_ids, elem_id)


        if not cell_type in cell_type_to_index.keys():
            cells.append([cell_type, []])
            elem_ids.append([])
            cell_type_to_index[cell_type] = len(cells) - 1
            prop_ids[cell_type] = []

        cell_type_id = cell_type_to_index[cell_type]
        try:
            _point_ids = [point_ids[_i] for _i in node_ids]
        except KeyError as e:
            raise ValueError(f"Node ID {e} in element {elem_id} not found in node list")
        cells[cell_type_id][1].append(_point_ids)
        elem_ids[cell_type_id].append(elem_id)
        cell_ids[elem_id] = (
            cell_type_id,
            len(cells[cell_type_id][1]) - 1
        )
        try:
            prop_ids[cell_type].append(int(prop_id))
        except ValueError as e:
            raise ValueError(f"Invalid property ID '{prop_id}' for element {elem_id}: {e}")

        counter += 1

    for _i in range(len(cells)):
        cells[_i] = tuple(cells[_i])

    return cells, elem_ids, prop_ids, cell_ids, line









def _read_property_ref_csys(file: TextIO, nelem: int, cells: List, cell_ids: Dict) -> List[np.ndarray]:
    """Read local coordinate system data for element properties.
    
    Parses reference coordinate system definitions for each element,
    organizing the data by cell type for use in property calculations.
    
    Parameters
    ----------
    file : TextIO
        File buffer object to read from
    nelem : int
        Number of elements to read coordinate systems for
    cells : list of tuples
        Element data organized by type
    cell_ids : dict
        Mapping from element ID to (cell_type_index, element_index)
        
    Returns
    -------
    list of numpy.ndarray
        Coordinate system arrays for each cell type, where each array
        contains transformation matrices for elements of that type
        
    Raises
    ------
    ValueError
        If coordinate system data format is invalid
    IndexError
        If element IDs are out of range
    """

    cell_csys = []
    counter = 0
    while counter < nelem:
        line = file.readline().strip()
        if line == "": continue

        line = line.split()

        try:
            elem_id = int(line[0])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid element ID on coordinate system line {counter + 1}: {e}")
        
        try:
            elem_csys = list(map(float, line[1:]))
        except ValueError as e:
            raise ValueError(f"Invalid coordinate system values for element {elem_id}: {e}")
        
        try:
            cell_block_id, cell_id = cell_ids[elem_id]
        except KeyError:
            raise ValueError(f"Element ID {elem_id} not found in element list")

        if cell_block_id > len(cell_csys) - 1:
            _ncell = len(cells[cell_block_id][1])
            cell_csys.append(np.zeros((_ncell, CSYS_MATRIX_SIZE)))

        cell_csys[cell_block_id][cell_id] = elem_csys

        counter += 1

    return cell_csys









# ====================================================================

def write(
    filename: Union[str, TextIO], mesh: SGMesh, sgdim: int, model_space: str, 
    prop_ref_y: str = 'x', renumber_nodes: bool = False, 
    renumber_elements: bool = False, int_fmt: str = '8d', 
    float_fmt: str = "20.9e") -> None:
    """Write SGMesh to SwiftComp format file.
    
    Outputs mesh data in SwiftComp format, including nodes, elements,
    and optional local coordinate system information.
    
    Parameters
    ----------
    filename : str or file-like
        Output file path or file buffer object
    mesh : SGMesh
        Mesh object containing points, cells, and associated data
    sgdim : int
        Spatial dimension of the mesh (1, 2, or 3)
    model_space : str
        Model space identifier for the mesh
    prop_ref_y : str, optional
        Reference axis for property orientation, default 'x'
    renumber_nodes : bool, optional
        Whether to renumber nodes sequentially, default False
    renumber_elements : bool, optional
        Whether to renumber elements sequentially, default False
    int_fmt : str, optional
        Format string for integer output, default '8d'
    float_fmt : str, optional
        Format string for float output, default "20.9e"
        
    Raises
    ------
    ValueError
        If mesh data is invalid or incomplete
    IOError
        If file writing encounters errors
        
    Examples
    --------
    >>> write('output.sc', mesh, sgdim=3, model_space='3D')
    """
    if is_buffer(filename, 'w'):
        write_buffer(
            filename, mesh, sgdim, model_space,
            prop_ref_y, renumber_nodes, renumber_elements,
            int_fmt, float_fmt
            )
    else:
        with open(str(filename), 'at') as file:
            write_buffer(
                file, mesh, sgdim, model_space,
                prop_ref_y, renumber_nodes, renumber_elements,
                int_fmt, float_fmt
                )



def write_buffer(
    file: TextIO, mesh: SGMesh, sgdim: int, model_space: str, prop_ref_y: str = 'x',
    renumber_nodes: bool = False, renumber_elements: bool = False,
    int_fmt: str = '8d', float_fmt: str = "20.9e"
    ) -> None:
    """Write SGMesh data to SwiftComp format file buffer.
    
    Outputs mesh data in SwiftComp format to a file buffer, including
    nodes, elements, and optional local coordinate system information.
    
    Parameters
    ----------
    file : TextIO
        File buffer object to write to
    mesh : SGMesh
        Mesh object containing points, cells, and associated data
    sgdim : int
        Spatial dimension of the mesh (1, 2, or 3)
    model_space : str
        Model space identifier for the mesh
    prop_ref_y : str, optional
        Reference axis for property orientation, default 'x'
    renumber_nodes : bool, optional
        Whether to renumber nodes sequentially, default False
    renumber_elements : bool, optional
        Whether to renumber elements sequentially, default False
    int_fmt : str, optional
        Format string for integer output, default '8d'
    float_fmt : str, optional
        Format string for float output, default "20.9e"
        
    Raises
    ------
    ValueError
        If mesh data is invalid or incomplete
    KeyError
        If required cell data fields are missing
    """
    # Input validation
    if sgdim not in (1, 2, 3):
        raise ValueError(f"sgdim must be 1, 2, or 3, got {sgdim}")
    if mesh is None:
        raise ValueError("mesh cannot be None")
    if not hasattr(mesh, 'points') or not hasattr(mesh, 'cells'):
        raise ValueError("mesh must have 'points' and 'cells' attributes")
    if 'property_id' not in mesh.cell_data:
        raise ValueError("mesh.cell_data must contain 'property_id'")

    _node_id = mesh.point_data.get('node_id', [])

    _write_nodes(
        file, mesh.points, sgdim, node_id=_node_id,
        model_space=model_space,
        renumber_nodes=renumber_nodes,
        int_fmt=int_fmt, float_fmt=float_fmt
        )

    if not 'element_id' in mesh.cell_data.keys():
        mesh.cell_data['element_id'] = []
    cell_id_to_elem_id = _write_elements(
        file, mesh.cells, mesh.cell_data['property_id'],
        mesh.cell_data['element_id'], _node_id,
        renumber_nodes=renumber_nodes,
        int_fmt=int_fmt
        )

    if 'property_ref_csys' in mesh.cell_data.keys():
        _write_property_ref_csys(
            file,
            mesh.cell_data['property_ref_csys'],
            cell_id_to_elem_id,
            int_fmt, float_fmt
        )




def _write_elements(
    f: TextIO, cells: List, cell_prop_ids: List, elem_id: List, 
    node_id, renumber_nodes: bool, int_fmt: str = '8d'
    ) -> List:
    """Write element connectivity and properties to SwiftComp format.
    
    Outputs element definitions in SwiftComp format, including element
    IDs, property IDs, and node connectivity for each element type.
    
    Parameters
    ----------
    f : TextIO
        File buffer object to write to
    cells : list
        List of cell blocks containing element data
    cell_prop_ids : list of lists
        Property IDs for elements in each cell block
    elem_id : list of lists
        Element IDs for elements in each cell block (modified in-place)
    node_id : list
        Node ID mapping for renumbering
    renumber_nodes : bool
        Whether to apply node renumbering
    int_fmt : str, optional
        Format string for integer output, default '8d'
        
    Returns
    -------
    list of lists
        Mapping from cell indices to element IDs for reference
        
    Raises
    ------
    ValueError
        If element data is inconsistent or invalid
    IndexError
        If array indices are out of range
    """
    if len(elem_id) == 0:
        generate_eid = True
    else:
        generate_eid = False

    cell_id_to_elem_id = []

    sfi = '{:' + int_fmt + '}'

    consecutive_index = 0
    for k, cell_block in enumerate(cells):
        cell_type = cell_block.type
        node_idcs = _meshio_to_sg_order(
            cell_type, cell_block.data,
            node_id=node_id, renumber_nodes=renumber_nodes
            )

        _cid_to_eid = []
        if generate_eid:
            elem_id.append([])

        for i, c in enumerate(node_idcs):
            if generate_eid:
                _eid = consecutive_index + i + 1
                elem_id[k].append(_eid)
            else:
                _eid = elem_id[k][i]

            _pid = cell_prop_ids[k][i]

            _nums = [_eid, _pid]  # Element id, property id

            _nums.extend(c.tolist())

            # Write the numbers
            fmt = ''.join([sfi,]*len(_nums))
            f.write(fmt.format(*_nums))
            if k == 0 and i == 0:
                f.write('  # element connectivity')
            f.write('\n')

            _cid_to_eid.append(_eid)

        cell_id_to_elem_id.append(_cid_to_eid)

        consecutive_index += len(node_idcs)

    f.write('\n')
    return cell_id_to_elem_id




def _write_property_ref_csys(file: TextIO, cell_csys: List, cell_id_to_elem_id: List, int_fmt: str = '8d', float_fmt: str = '20.12e') -> None:
    """Write local coordinate system data for element properties.
    
    Outputs reference coordinate system definitions for each element
    in SwiftComp format, used for property orientation calculations.
    
    Parameters
    ----------
    file : TextIO
        File buffer object to write to
    cell_csys : list of numpy.ndarray
        Coordinate system arrays for each cell type
    cell_id_to_elem_id : list of lists
        Mapping from cell indices to element IDs
    int_fmt : str, optional
        Format string for integer output, default '8d'
    float_fmt : str, optional
        Format string for float output, default '20.12e'
        
    Raises
    ------
    ValueError
        If coordinate system data dimensions are invalid
    IndexError
        If element ID mappings are out of range
    """

    sfi = '{:' + int_fmt + '}'
    sff = ''.join(['{:' + float_fmt + '}', ]*CSYS_MATRIX_SIZE)
    c = [0, 0, 0]

    for i, block_data in enumerate(cell_csys):
        for j, csys in enumerate(block_data):
            elem_id = cell_id_to_elem_id[i][j]

            file.write(sfi.format(elem_id))
            file.write(sff.format(*(list(csys)+c)))
            file.write('\n')

    file.write('\n')
    return


register_sgmesh_format('swiftcomp', ['.sc', '.dat', '.sg'], read_buffer, write_buffer)
