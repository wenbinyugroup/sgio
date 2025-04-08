from __future__ import annotations

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
from meshio._exceptions import WriteError

from sgio.core.mesh import SGMesh


c_int = np.dtype("int32")
c_double = np.dtype("float64")


def addPointDictDataToMesh(name:str|list, dict_data:dict[int, list], mesh:SGMesh):
    """Add point/node data (dictionary) to point_data of mesh.

    Parameters:
    -----------
    name:
        Name(s) of the point data. If it is a list, then it should have the same length as data for each node.
    dict_data:
        Data in the dictionary form {nid: data}.
    mesh:
        Mesh where the point data will be added.
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

    return




def addCellDictDataToMesh(name:str|list, dict_data:dict[int, list], mesh:SGMesh):
    """Add cell/element data (dictionary) to cell_data of mesh.

    The mesh should contain a map between (cell_type, index) and element id.    

    Parameters:
    -----------
    name:
        Name(s) of the cell data. If it is a list, then it should have the same length as data list for each element.
    dict_data:
        Data in the dictionary form {eid: data}.
    mesh:
        Mesh where the cell data will be added.

    """

    _cell_data_eid = mesh.cell_data['element_id']

    if isinstance(name, str):
        _cell_data = []

        for _i, _typei_ids in enumerate(_cell_data_eid):
            _typei_data = []

            for _j, _eid in enumerate(_typei_ids):
                _data = dict_data[_eid]
                _typei_data.append(_data)

            _cell_data.append(_typei_data)

        mesh.cell_data[name] = np.array(_cell_data)


    elif isinstance(name, list):
        ncomps = len(name)
        _cell_data_all = []
        for _i in range(ncomps):
            _cell_data_all.append([])

        for _i, _typei_ids in enumerate(_cell_data_eid):
            _typei_data_all = []
            for _ in range(ncomps):
                _typei_data_all.append([])

            for _j, _eid in enumerate(_typei_ids):
                _data_all = dict_data[_eid]
                for _k, _data in enumerate(_data_all):
                    _typei_data_all[_k].append(_data)

            for _l in range(ncomps):
                _cell_data_all[_l].append(_typei_data_all[_l])

        for _i, _name in enumerate(name):
            _data = _cell_data_all[_i]
            mesh.cell_data[_name] = np.array(_data)

    return




# ====================================================================
# Readers


def _read_nodes(f, nnodes:int, sgdim:int=3):
    points = []
    point_ids = {}
    counter = 0
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

    return np.array(points, dtype=float), point_ids, line




def _sg_to_meshio_order(cell_type: str, idx: ArrayLike) -> np.ndarray:
    # TODO
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




def _meshio_to_sg_order(cell_type:str, idx:ArrayLike):
    idx_sg = np.asarray(idx) + 1

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




# ====================================================================
# Writers


def _write_nodes(f, points, sgdim, int_fmt:str='8d', float_fmt:str='20.9e'):
    sfi = '{:' + int_fmt + '}'
    sff = ''.join(['{:' + float_fmt + '}', ]*sgdim)
    # print('sff =', sff)
    # sff = ''.join([sff]*sgdim)
    # count = 0
    # nnode = len(self.nodes)
    # for nid, ncoord in self.nodes.items():
    for i, ncoord in enumerate(points):
        # count += 1
        nid = i + 1
        f.write(sfi.format(nid))

        # print(ncoord[-sgdim:])
        f.write(sff.format(*ncoord[-sgdim:]))
        # if sgdim == 1:
        #     sui.writeFormatFloats(f, ncoord[2:], fmt=sff, newline=False)
        # elif self.sgdim == 2:
        #     sui.writeFormatFloats(f, ncoord[1:], fmt=sff, newline=False)
        # elif self.sgdim == 3:
        #     sui.writeFormatFloats(f, ncoord, fmt=sff, newline=False)

        if i == 0:
            f.write('  ! nodal coordinates')

        f.write('\n')

    f.write('\n')

    return




def _meshio_to_sg_order(cell_type:str, idx:ArrayLike):
    """
    """
    idx_sg = np.asarray(idx) + 1

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




# def _write_data(fh, tag, name, data, binary):
#     fh.write(f"${tag}\n".encode())
#     # <http://gmsh.info/doc/texinfo/gmsh.html>:
#     # > Number of string tags.
#     # > gives the number of string tags that follow. By default the first
#     # > string-tag is interpreted as the name of the post-processing view and
#     # > the second as the name of the interpolation scheme. The interpolation
#     # > scheme is provided in the $InterpolationScheme section (see below).
#     fh.write(f"{1}\n".encode())
#     fh.write(f'"{name}"\n'.encode())
#     fh.write(f"{1}\n".encode())
#     fh.write(f"{0.0}\n".encode())
#     # three integer tags:
#     fh.write(f"{3}\n".encode())
#     # time step
#     fh.write(f"{0}\n".encode())
#     # number of components
#     num_components = data.shape[1] if len(data.shape) > 1 else 1
#     if num_components not in [1, 3, 9]:
#         raise WriteError("Gmsh only permits 1, 3, or 9 components per data field.")

#     # Cut off the last dimension in case it's 1. This avoids problems with
#     # writing the data.
#     if len(data.shape) > 1 and data.shape[1] == 1:
#         data = data[:, 0]

#     fh.write(f"{num_components}\n".encode())
#     # num data items
#     fh.write(f"{data.shape[0]}\n".encode())
#     # actually write the data
#     if binary:
#         if num_components == 1:
#             dtype = [("index", c_int), ("data", c_double)]
#         else:
#             dtype = [("index", c_int), ("data", c_double, num_components)]
#         tmp = np.empty(len(data), dtype=dtype)
#         tmp["index"] = 1 + np.arange(len(data))
#         tmp["data"] = data
#         tmp.tofile(fh)
#         fh.write(b"\n")
#     else:
#         fmt = " ".join(["{}"] + ["{!r}"] * num_components) + "\n"
#         # TODO unify
#         if num_components == 1:
#             for k, x in enumerate(data):
#                 fh.write(fmt.format(k + 1, x).encode())
#         else:
#             for k, x in enumerate(data):
#                 fh.write(fmt.format(k + 1, *x).encode())

#     fh.write(f"$End{tag}\n".encode())
