"""
I/O for VABS format
"""
from __future__ import annotations

import logging

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

vabs_to_meshio_type = {
    3: 'triangle',
    6: 'triangle6',
    4: 'quad',
    8: 'quad8',
    9: 'quad9',
}

# def read(filename, sgdim:int, nnode:int, nelem:int, **kwargs):
#     """Reads a Gmsh msh file."""
#     if is_buffer(filename, 'r'):
#         mesh = read_buffer(filename, sgdim, nnode, nelem)
#     else:
#         with open(filename, 'r') as file:
#             mesh = read_buffer(file, sgdim, nnode, nelem)
#     return mesh




def read_buffer(f, sgdim:int, nnode:int, nelem:int, format_flag, **kwargs):
    """
    """
    # Initialize the optional data fields
    points = []
    cells = []
    # cell_ids = []
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
    cells, elem_ids, elem_id_to_cell_id = _read_elements(f, nelem, point_ids)
    cell_data['element_id'] = elem_ids

    # Read local coordinate system for sectional properties
    cell_prop_id, cell_csys = _read_property_id_ref_csys(
        f, nelem, cells, elem_id_to_cell_id, format_flag)
    cell_data['property_id'] = cell_prop_id
    cell_data['property_ref_csys'] = cell_csys

    # print(cells)

    return SGMesh(
        points,
        cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        point_sets=point_sets,
        cell_sets=cell_sets,
    )




def _read_elements(f, nelem:int, point_ids):
    """
    """

    cells = []
    cell_type_to_index = {}
    elem_ids = []  # Element id in the original file; Same shape as cells
    elem_id_to_cell_id = {}

    counter = 0
    while counter < nelem:
        line = f.readline()
        line = line.split('!')[0].strip()
        if line == "": continue

        line = line.split()
        # if file_format.lower().startswith('v'):
        #     cell_id, node_ids = line[0], line[1:]
        # elif file_format.lower().startswith('s'):
        elem_id, node_ids = int(line[0]), line[1:]

        # Check element type
        # cell_type = ''
        # if node_ids[3] == '0':  # triangle
        #     node_ids = [int(_i) for _i in node_ids if _i != '0']
        # else:  # quadrilateral
        node_ids = [int(_i) for _i in node_ids if _i != '0']
        cell_type = vabs_to_meshio_type[len(node_ids)]

        if not cell_type in cell_type_to_index.keys():
            # cells[cell_type] = []
            cells.append([cell_type, []])
            elem_ids.append([])
            cell_type_to_index[cell_type] = len(cells) - 1
            # cell_ids[cell_type] = {}
            # prop_ids[cell_type] = []

        cell_type_id = cell_type_to_index[cell_type]
        cell_id = len(cells[cell_type_id][1])
        cells[cell_type_id][1].append([point_ids[_i] for _i in node_ids])
        elem_ids[cell_type_id].append(elem_id)
        # if file_format.lower().startswith('s'):
        # prop_ids[cell_type].append(int(prop_id))
        elem_id_to_cell_id[elem_id] = (cell_type_id, cell_id)

        counter += 1

    for _i in range(len(cells)):
        cells[_i] = tuple(cells[_i])


    return cells, elem_ids, elem_id_to_cell_id









def _read_property_id_ref_csys(file, nelem, cells, elem_id_to_cell_id, format_flag):
    """Read the data block of element property id and reference csys.

    Parameters
    ----------
    file : file
        The file to read from.
    nelem : int
        The number of elements.
    cells : list
        The list of cells.
    elem_id_to_cell_id : dict
        The dictionary of element id to cell id.
    format_flag : int
        The format flag. 0 for old format, 1 for new format.

    Returns
    -------
    cell_prop_id : list
        The list of property ids.
    cell_csys : list
        The list of reference csys.
    """

    cell_prop_id = []
    cell_csys = []
    # print(cells)
    # print(cell_ids)

    counter = 0
    while counter < nelem:
        line = file.readline()
        line = line.split('!')[0].strip()
        if line == "": continue

        line = line.split()

        elem_id = int(line[0])
        prop_id = int(line[1])
        elem_csys = float(line[2])

        cell_block_id, cell_id = elem_id_to_cell_id[elem_id]

        if cell_block_id > len(cell_csys) - 1:
            _ncell = len(cells[cell_block_id][1])
            # print('_ncell =', _ncell)
            cell_prop_id.append(np.zeros(_ncell, dtype=int))
            cell_csys.append(np.zeros(_ncell))

        # print(cell_csys[cell_block_id][cell_id])

        cell_prop_id[cell_block_id][cell_id] = prop_id
        cell_csys[cell_block_id][cell_id] = elem_csys

        counter += 1

    return cell_prop_id, cell_csys









# ====================================================================

def write(
    filename, mesh, sgdim, model_space='', prop_ref_y='x',
    renumber_nodes=False, renumber_elements=False,
    int_fmt='8d', float_fmt="20.9e"):
    """
    """
    if is_buffer(filename, 'w'):
        write_buffer(
            filename, mesh, sgdim, model_space=model_space, prop_ref_y=prop_ref_y,
            renumber_nodes=renumber_nodes, renumber_elements=renumber_elements,
            int_fmt=int_fmt, float_fmt=float_fmt)
    else:
        with open(filename, 'at') as file:
            write_buffer(
                file, mesh, sgdim, model_space=model_space, prop_ref_y=prop_ref_y,
                int_fmt=int_fmt, float_fmt=float_fmt)



def write_buffer(
    file, mesh, sgdim, model_space='', prop_ref_y='x',
    renumber_nodes=False, renumber_elements=False,
    int_fmt='8d', float_fmt="20.9e"
    ):
    """Write mesh data to VABS format buffer.

    Parameters
    ----------
    file : file
        The file buffer to write to.
    mesh : SGMesh
        The mesh object containing points, cells, and associated data.
    sgdim : int
        The spatial dimension of the structural gene (2 or 3).
    model_space : str, optional
        The model coordinate space ('xy', 'yz', 'zx'), by default ''.
    prop_ref_y : str, optional
        Reference axis for property coordinate system ('x', 'y', 'z'), by default 'x'.
    renumber_nodes : bool, optional
        Whether to renumber nodes, by default False.
    renumber_elements : bool, optional
        Whether to renumber elements, by default False.
    int_fmt : str, optional
        Format string for integer output, by default '8d'.
    float_fmt : str, optional
        Format string for float output, by default "20.9e".

    Returns
    -------
    None
        Writes mesh data directly to the file buffer.
    """

    # _node_id = []
    # if renumber_nodes:
    _node_id = mesh.point_data.get('node_id', [])
    # print(f'_node_id = {_node_id}')

    _write_nodes(
        file, mesh.points, sgdim, node_id=_node_id,
        renumber_nodes=renumber_nodes,
        model_space=model_space,
        int_fmt=int_fmt, float_fmt=float_fmt
    )

    if not 'element_id' in mesh.cell_data.keys():
        mesh.cell_data['element_id'] = []
    _write_elements(
        file, mesh.cells, mesh.cell_data['element_id'], _node_id,
        renumber_nodes=renumber_nodes,
        int_fmt=int_fmt
        )

    try:
        if prop_ref_y == 'x':
            property_ref_csys = mesh.cell_data['property_ref_x']
        elif prop_ref_y == 'y':
            property_ref_csys = mesh.cell_data['property_ref_y']
        elif prop_ref_y == 'z':
            property_ref_csys = mesh.cell_data['property_ref_z']
    except KeyError:
        try:
            property_ref_csys = mesh.cell_data['property_ref_csys']
        except KeyError:
            property_ref_csys = None

    _write_property_id_ref_csys(
        file,
        mesh.cell_data['property_id'],
        property_ref_csys,
        mesh.cell_data['element_id'],
        model_space=model_space,
        ref_y=prop_ref_y,
        int_fmt=int_fmt,
        float_fmt=float_fmt
    )




def _write_elements(
    f, cells, elem_id, node_id, renumber_nodes=False,
    int_fmt:str='8d'
    ):
    """Write element connectivity data to VABS format file.

    Parameters
    ----------
    f : file
        The file object to write to.
    cells : list
        List of cell blocks containing element connectivity data.
    elem_id : list
        List of element IDs for each cell block. If empty, IDs are auto-generated.
    node_id : list
        List of node IDs for renumbering (currently unused).
    renumber_nodes : bool, optional
        Whether to renumber nodes (currently unused), by default False.
    int_fmt : str, optional
        Format string for integer output, by default '8d'.

    Returns
    -------
    None
        Modifies elem_id list in-place if auto-generating element IDs.
    """
    if len(elem_id) == 0:
        generate_eid = True
    else:
        generate_eid = False
    # elem_ids = []

    # if len(node_id) > 0:
    #     _node_id = node_id.tolist()

    sfi = '{:' + int_fmt + '}'

    consecutive_index = 0
    for k, cell_block in enumerate(cells):
        cell_type = cell_block.type
        node_idcs = _meshio_to_sg_order(
            cell_type, cell_block.data,
            node_id=node_id, renumber_nodes=renumber_nodes)

        # print(f'cell_block.data = {cell_block.data}')
        # print(f'node_idcs = {node_idcs}')

        # _cid_to_eid = []
        if generate_eid:
            elem_id.append([])

        for i, c in enumerate(node_idcs):

            if generate_eid:
                _eid = consecutive_index + i + 1
                elem_id[k].append(_eid)
            else:
                _eid = int(elem_id[k][i])

            _nums = [_eid, ]  # Element id

            # if renumber_nodes:
            #     # Get the index of node id in node_id
            #     # print(f'c = {c.tolist()}')
            #     logger.debug(f'c = {c.tolist()}')
            #     _nids = [_node_id.index(_i) + 1 for _i in c.tolist() if _i != 0]
            #     # print(f'_nids = {_nids}')
            #     logger.debug(f'_nids = {_nids}')
            #     _nums.extend(_nids)
            # else:
            # Ensure node ids are integers
            _nums.extend([int(x) for x in c.tolist()])  # Node ids

            # Write the numbers
            fmt = ''.join([sfi,]*len(_nums))
            f.write(fmt.format(*_nums))
            # logger.debug('sfi = {}'.format(sfi))
            # sui.writeFormatIntegers(f, _nums, fmt=sfi, newline=False)
            if k == 0 and i == 0:  f.write('  ! element connectivity')
            f.write('\n')

            # _cid_to_eid.append(_eid)

        # elem_ids.append(_cid_to_eid)

        consecutive_index += len(node_idcs)

    f.write('\n')
    return




def _write_property_id_ref_csys(
    file, cell_prop_id, cell_csys, elem_ids,
    model_space='', ref_y='x',
    int_fmt:str='8d', float_fmt:str='20.12e'
    ):
    """Write the property id and reference csys (theta_1) to the file.

    Parameters
    ----------
    file : file
        The file to write to.
    cell_prop_id : list of lists
        The property id for each cell.
    cell_csys : list of lists
        The reference csys for each cell.
    elem_ids : list of lists
        The element id for each cell.
    ref_y : str
        The reference y-axis for the reference csys.
    int_fmt : str
        The format string for the integer.
    float_fmt : str
        The format string for the float.

    Returns
    -------
    None
    """

    # sfi = '{:' + int_fmt + '}'
    # sff = ''.join(['{:' + float_fmt + '}', ]*9)
    sfmt = ''.join([
        '{:' + int_fmt + '}',
        '{:' + int_fmt + '}',
        '{:' + float_fmt + '}'
    ])

    for i, block_data in enumerate(cell_prop_id):
        # i-th cell/element block

        for j, prop_id in enumerate(block_data):
            # j-th cell/element in the i-th cell/element block
            # Ensure integer types for elem_id and prop_id
            prop_id = int(prop_id)
            elem_id = int(elem_ids[i][j])

            try:
                theta_1 = cell_csys[i][j]
                if not isinstance(theta_1, float):
                    # Calculate theta_1 from the csys
                    _csys = theta_1
                    # _vx2 = np.array([1, 0, 0])

                    _vy2 = np.array(_csys[:3])
                    # logger.debug(f'_vy2 = {_vy2}')

                    # Method 1
                    # _cos_theta_1 = np.dot(_vx2, _vy2) / (np.linalg.norm(_vx2) * np.linalg.norm(_vy2))
                    # print(f'_cos_theta_1 = {_cos_theta_1}')
                    # theta_1 = np.rad2deg(np.arccos(_cos_theta_1))
                    # print(f'theta_1 = {theta_1}')

                    # Method 2
                    if model_space == 'xy':
                        theta_1 = np.rad2deg(np.arctan2(_vy2[1], _vy2[0]))
                    elif model_space == 'yz':
                        theta_1 = np.rad2deg(np.arctan2(_vy2[2], _vy2[1]))
                    elif model_space == 'zx':
                        theta_1 = np.rad2deg(np.arctan2(_vy2[0], _vy2[2]))
                    else:
                        raise ValueError(f'Invalid model space: {model_space}')
                    # print(f'theta_1 = {theta_1}')

            except TypeError:
                theta_1 = 0

            _nums = [elem_id, prop_id, theta_1]
            # print(_nums)

            file.write(sfmt.format(*_nums))
            file.write('\n')

    file.write('\n')
    return



register_sgmesh_format('vabs', ['.vabs', '.dat', '.sg'], read_buffer, write_buffer)

