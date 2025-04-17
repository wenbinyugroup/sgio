"""
I/O for SwiftComp format
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

# c_int = np.dtype("i")
# c_double = np.dtype("d")

# def read(filename, sgdim:int, nnode:int, nelem:int, read_local_frame):
#     """Reads a Gmsh msh file."""
#     if is_buffer(filename, 'r'):
#         mesh = read_buffer(filename, sgdim, nnode, nelem, read_local_frame)
#     else:
#         with open(filename, 'r') as file:
#             mesh = read_buffer(file, sgdim, nnode, nelem, read_local_frame)
#     return mesh




def read_buffer(f, sgdim:int, nnode:int, nelem:int, read_local_frame):
    """
    """
    logger.debug(locals())

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
    cells, prop_ids, cell_ids, line = _read_elements(f, nelem, point_ids)
    # print(cells)

    _cd = []
    for _cb in cells:
        _ct = _cb[0]
        _cd.append(prop_ids[_ct])
    # print(_cd)
    cell_data['property_id'] = _cd

    if read_local_frame:
        # Read local coordinate system for sectional properties
        cell_csys = _read_property_ref_csys(f, nelem, cells, cell_ids)
        cell_data['property_ref_csys'] = np.asarray(cell_csys)

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
    cells = []
    cell_type_to_index = {}
    prop_ids = {}  # property id for each element; will update cell_data (swiftcomp)
    cell_ids = {}
    counter = 0
    while counter < nelem:
        line = f.readline().strip()
        if line == "": continue

        line = line.split()
        # if file_format.lower().startswith('v'):
        #     cell_id, node_ids = line[0], line[1:]
        # elif file_format.lower().startswith('s'):
        cell_id, prop_id, node_ids = line[0], line[1], line[2:]

        # Check element type
        cell_type = ''
        if len(node_ids) == 5:  # 1d elements
            node_ids = [int(_i) for _i in node_ids if _i != '0']
            if len(node_ids) == 2:
                cell_type = 'line'
            else:
                cell_type = 'line{}'.format(len(node_ids))
        elif len(node_ids) == 9:  # 2d elements
            if node_ids[3] == '0':  # triangle
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {3: 'triangle', 6: 'triangle6'}[len(node_ids)]
            else:  # quadrilateral
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {4: 'quad', 8: 'quad8', 9: 'quad9'}[len(node_ids)]
        elif len(node_ids) == 20:  # 3d elements
            if node_ids[4] == '0':  # tetrahedral
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {4: 'tetra', 10: 'tetra10'}[len(node_ids)]
            elif node_ids[6] == '0':  # wedge
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {6: 'wedge', 15: 'tetra15'}[len(node_ids)]
            else:  # hexahedron
                node_ids = [int(_i) for _i in node_ids if _i != '0']
                cell_type = {8: 'hexahedron', 20: 'hexahedron20'}[len(node_ids)]


        if not cell_type in cell_type_to_index.keys():
            # cells[cell_type] = []
            cells.append([cell_type, []])
            cell_type_to_index[cell_type] = len(cells) - 1
            # cell_ids[cell_type] = {}
            prop_ids[cell_type] = []

        cells[cell_type_to_index[cell_type]][1].append([point_ids[_i] for _i in node_ids])
        cell_ids[int(cell_id)] = (
            cell_type_to_index[cell_type],
            len(cells[cell_type_to_index[cell_type]][1])-1
        )
        # if file_format.lower().startswith('s'):
        prop_ids[cell_type].append(int(prop_id))

        counter += 1

    for _i in range(len(cells)):
        cells[_i] = tuple(cells[_i])

    return cells, prop_ids, cell_ids, line









def _read_property_ref_csys(file, nelem, cells, cell_ids):
    """
    """

    cell_csys = []
    # print(cells)
    # print(cell_ids)

    counter = 0
    while counter < nelem:
        line = file.readline().strip()
        if line == "": continue

        line = line.split()

        elem_id = int(line[0])
        elem_csys = list(map(float, line[1:]))

        cell_block_id, cell_id = cell_ids[elem_id]

        if cell_block_id > len(cell_csys) - 1:
            _ncell = len(cells[cell_block_id][1])
            print('_ncell =', _ncell)
            cell_csys.append(np.zeros((_ncell, 9)))

        # print(cell_csys[cell_block_id][cell_id])

        cell_csys[cell_block_id][cell_id] = elem_csys

        counter += 1

    return cell_csys









# ====================================================================

def write(
    filename, mesh:SGMesh, sgdim, model_space,
    int_fmt='8d', float_fmt="20.9e"):
    """
    """
    if is_buffer(filename, 'w'):
        write_buffer(filename, mesh, sgdim, model_space, int_fmt, float_fmt)
    else:
        with open(filename, 'at') as file:
            write_buffer(file, mesh, sgdim, model_space, int_fmt, float_fmt)



def write_buffer(
    file, mesh:SGMesh, sgdim, model_space,
    int_fmt='8d', float_fmt="20.9e"):
    """
    """

    _write_nodes(
        file, mesh.points, sgdim, model_space=model_space,
        int_fmt=int_fmt, float_fmt=float_fmt
        )

    cell_id_to_elem_id = _write_elements(file, mesh.cells, mesh.cell_data['property_id'], int_fmt)

    if 'property_ref_csys' in mesh.cell_data.keys():
        _write_property_ref_csys(
            file,
            mesh.cell_data['property_ref_csys'],
            cell_id_to_elem_id,
            int_fmt, float_fmt
        )




def _write_elements(f, cells, cell_prop_ids, int_fmt:str='8d'):
    """
    """
    cell_id_to_elem_id = []

    sfi = '{:' + int_fmt + '}'

    consecutive_index = 0
    for k, cell_block in enumerate(cells):
        cell_type = cell_block.type
        node_idcs = _meshio_to_sg_order(cell_type, cell_block.data)

        _cid_to_eid = []

        for i, c in enumerate(node_idcs):
            _eid = consecutive_index + i + 1
            _pid = cell_prop_ids[k][i]

            _nums = [_eid, _pid]  # Element id, property id

            _nums.extend(c.tolist())

            # print(_nums)

            # Write the numbers
            fmt = ''.join([sfi,]*len(_nums))
            f.write(fmt.format(*_nums))
            # logger.debug('sfi = {}'.format(sfi))
            # sui.writeFormatIntegers(f, _nums, fmt=sfi, newline=False)
            if k == 0 and i == 0:
                f.write('  # element connectivity')
            f.write('\n')

            _cid_to_eid.append(_eid)

        cell_id_to_elem_id.append(_cid_to_eid)

        consecutive_index += len(node_idcs)

    f.write('\n')
    return cell_id_to_elem_id




def _write_property_ref_csys(file, cell_csys, cell_id_to_elem_id, int_fmt:str='8d', float_fmt:str='20.12e'):
    """
    """

    sfi = '{:' + int_fmt + '}'
    sff = ''.join(['{:' + float_fmt + '}', ]*9)
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
