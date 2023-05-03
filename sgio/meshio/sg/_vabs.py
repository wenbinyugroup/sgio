"""
I/O for SwiftComp sg format
"""
from __future__ import annotations

import numpy as np

from .._files import is_buffer
from .._common import cell_data_from_raw, num_nodes_per_cell, raw_from_cell_data, warn
from .._exceptions import ReadError
from .._mesh import CellBlock, Mesh
from .common import (
    # _fast_forward_over_blank_lines,
    # _fast_forward_to_end_block,
    _meshio_to_sg_order,
    _sg_to_meshio_order,
    _read_nodes,
    _write_nodes,
    # _write_elements,
    # _meshio_to_gmsh_type,
    # _read_data,
    # _read_physical_names,
    # _write_data,
    # _write_physical_names,
)

# c_int = np.dtype("i")
# c_double = np.dtype("d")

def read(filename, sgdim:int, nnode:int, nelem:int, **kwargs):
    """Reads a Gmsh msh file."""
    if is_buffer(filename, 'r'):
        mesh = read_buffer(filename, sgdim, nnode, nelem)
    else:
        with open(filename, 'r') as file:
            mesh = read_buffer(file, sgdim, nnode, nelem)
    return mesh




def read_buffer(f, sgdim:int, nnode:int, nelem:int, **kwargs):
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
    # cell_type_to_id = {}
    # for _cell_type, _cell_points in cells_dict.items():
    #     cells.append(CellBlock(_cell_type, _cell_points))
    #     cell_type_to_id[_cell_type] = len(cells) - 1
    cell_data['element_id'] = np.asarray(elem_ids)

    # Read element property id and csys rotation (theta_1)
    # _cd = []
    # for _cb in cells:
    #     _ct = _cb[0]
    #     _cd.append(prop_ids[_ct])
    # cell_data['property'] = np.array(_cd)

    # Read local coordinate system for sectional properties
    cell_prop_id, cell_csys = _read_property_id_ref_csys(f, nelem, cells, elem_id_to_cell_id)
    cell_data['property_id'] = np.asarray(cell_prop_id)
    cell_data['property_ref_csys'] = np.asarray(cell_csys)

    return Mesh(
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
        line = f.readline().strip()
        if line == "": continue

        line = line.split()
        # if file_format.lower().startswith('v'):
        #     cell_id, node_ids = line[0], line[1:]
        # elif file_format.lower().startswith('s'):
        elem_id, node_ids = int(line[0]), line[1:]

        # Check element type
        cell_type = ''
        if node_ids[3] == '0':  # triangle
            node_ids = [int(_i) for _i in node_ids if _i != '0']
            cell_type = {3: 'triangle', 6: 'triangle6'}[len(node_ids)]
        else:  # quadrilateral
            node_ids = [int(_i) for _i in node_ids if _i != '0']
            cell_type = {4: 'quad', 8: 'quad8', 9: 'quad9'}[len(node_ids)]


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

    return cells, elem_ids, elem_id_to_cell_id









def _read_property_id_ref_csys(file, nelem, cells, elem_id_to_cell_id):
    """
    """

    cell_prop_id = []
    cell_csys = []
    # print(cells)
    # print(cell_ids)

    counter = 0
    while counter < nelem:
        line = file.readline().strip()
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

def write(filename, mesh, sgdim, int_fmt='8d', float_fmt="20.9e"):
    """
    """
    if is_buffer(filename, 'w'):
        write_buffer(filename, mesh, sgdim, int_fmt, float_fmt)
    else:
        with open(filename, 'at') as file:
            write_buffer(file, mesh, sgdim, int_fmt, float_fmt)



def write_buffer(file, mesh, sgdim, int_fmt='8d', float_fmt="20.9e"):
    """Writes msh files, cf.
    <http://gmsh.info//doc/texinfo/gmsh.html#MSH-ASCII-file-format>.
    """
    # # Filter the point data: gmsh:dim_tags are tags, the rest is actual point data.
    # point_data = {}
    # for key, d in mesh.point_data.items():
    #     if key not in ["gmsh:dim_tags"]:
    #         point_data[key] = d

    # # Split the cell data: gmsh:physical and gmsh:geometrical are tags, the rest is
    # # actual cell data.
    # tag_data = {}
    # cell_data = {}
    # for key, d in mesh.cell_data.items():
    #     if key in ["gmsh:physical", "gmsh:geometrical", "cell_tags"]:
    #         tag_data[key] = d
    #     else:
    #         cell_data[key] = d

    # # Always include the physical and geometrical tags. See also the quoted excerpt from
    # # the gmsh documentation in the _read_cells_ascii function above.
    # for tag in ["gmsh:physical", "gmsh:geometrical"]:
    #     if tag not in tag_data:
    #         warn(f"Appending zeros to replace the missing {tag[5:]} tag data.")
    #         tag_data[tag] = [
    #             np.zeros(len(cell_block), dtype=c_int) for cell_block in mesh.cells
    #         ]

    # with open(filename, "wb") as fh:
    # mode_idx = 1 if binary else 0
    # size_of_double = 8
    # fh.write(f"$MeshFormat\n2.2 {mode_idx} {size_of_double}\n".encode())
    # if binary:
    #     np.array([1], dtype=c_int).tofile(fh)
    #     fh.write(b"\n")
    # fh.write(b"$EndMeshFormat\n")

    # if mesh.field_data:
    #     _write_physical_names(fh, mesh.field_data)

    _write_nodes(file, mesh.points, sgdim, int_fmt, float_fmt)
    if not 'element_id' in mesh.cell_data.keys():
        mesh.cell_data['element_id'] = []
    _write_elements(file, mesh.cells, mesh.cell_data['element_id'], int_fmt)
    # if 'property_ref_csys' in mesh.cell_data.keys():
    _write_property_id_ref_csys(
        file,
        mesh.cell_data['property_id'],
        mesh.cell_data['property_ref_csys'],
        mesh.cell_data['element_id'],
        int_fmt, float_fmt
    )
    # if mesh.gmsh_periodic is not None:
    #     _write_periodic(fh, mesh.gmsh_periodic, float_fmt)

    # for name, dat in point_data.items():
    #     _write_data(fh, "NodeData", name, dat, binary)
    # cell_data_raw = raw_from_cell_data(cell_data)
    # for name, dat in cell_data_raw.items():
    #     _write_data(fh, "ElementData", name, dat, binary)


# def _write_nodes(fh, points, float_fmt, binary):
#     if points.shape[1] == 2:
#         # msh2 requires 3D points, but 2D points given. Appending 0 third component.
#         points = np.column_stack([points, np.zeros_like(points[:, 0])])

#     fh.write(b"$Nodes\n")
#     fh.write(f"{len(points)}\n".encode())
#     if binary:
#         dtype = [("index", c_int), ("x", c_double, (3,))]
#         tmp = np.empty(len(points), dtype=dtype)
#         tmp["index"] = 1 + np.arange(len(points))
#         tmp["x"] = points
#         tmp.tofile(fh)
#         fh.write(b"\n")
#     else:
#         fmt = "{} " + " ".join(3 * ["{:" + float_fmt + "}"]) + "\n"
#         for k, x in enumerate(points):
#             fh.write(fmt.format(k + 1, x[0], x[1], x[2]).encode())
#     fh.write(b"$EndNodes\n")



def _write_elements(f, cells, elem_id, int_fmt:str='8d'):
    """
    """
    if len(elem_id) == 0:
        generate_eid = True
    else:
        generate_eid = False
    # elem_ids = []

    sfi = '{:' + int_fmt + '}'

    consecutive_index = 0
    for k, cell_block in enumerate(cells):
        cell_type = cell_block.type
        node_idcs = _meshio_to_sg_order(cell_type, cell_block.data)

        # _cid_to_eid = []
        if generate_eid:
            elem_id.append([])

        for i, c in enumerate(node_idcs):

            if generate_eid:
                _eid = consecutive_index + i + 1
                elem_id[k].append(_eid)
            else:
                _eid = elem_id[k][i]

            _nums = [_eid, ]  # Element id

            _nums.extend(c.tolist())  # Node ids

            # Write the numbers
            fmt = ''.join([sfi,]*len(_nums))
            f.write(fmt.format(*_nums))
            # logger.debug('sfi = {}'.format(sfi))
            # sui.writeFormatIntegers(f, _nums, fmt=sfi, newline=False)
            if k == 0 and i == 0:  f.write('  # element connectivity')
            f.write('\n')

            # _cid_to_eid.append(_eid)

        # elem_ids.append(_cid_to_eid)

        consecutive_index += len(node_idcs)

    f.write('\n')
    return




def _write_property_id_ref_csys(
    file, cell_prop_id, cell_csys, elem_ids,
    int_fmt:str='8d', float_fmt:str='20.12e'
    ):
    """
    """

    # sfi = '{:' + int_fmt + '}'
    # sff = ''.join(['{:' + float_fmt + '}', ]*9)
    sfmt = ''.join([
        '{:' + int_fmt + '}',
        '{:' + int_fmt + '}',
        '{:' + float_fmt + '}'
    ])

    for i, block_data in enumerate(cell_prop_id):
        for j, prop_id in enumerate(block_data):
            elem_id = elem_ids[i][j]
            theta_1 = cell_csys[i][j]

            _nums = [elem_id, prop_id, theta_1]

            file.write(sfmt.format(*_nums))
            file.write('\n')

    file.write('\n')
    return



