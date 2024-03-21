from __future__ import annotations

import shlex

import numpy as np
from numpy.typing import ArrayLike

from .._common import warn
from .._exceptions import ReadError, WriteError

c_int = np.dtype("int32")
c_double = np.dtype("float64")


# def _fast_forward_to_end_block(f, block):
#     """fast-forward to end of block"""
#     # See also https://github.com/nschloe/pygalmesh/issues/34

#     for line in f:
#         try:
#             line = line.decode()
#         except UnicodeDecodeError:
#             pass
#         if line.strip() == f"$End{block}":
#             break
#     else:
#         warn(f"${block} not closed by $End{block}.")


# def _fast_forward_over_blank_lines(f):
#     is_eof = False
#     while True:
#         line = f.readline().decode()
#         if not line:
#             is_eof = True
#             break
#         elif len(line.strip()) > 0:
#             break
#     return line, is_eof


def _read_nodes(f, nnodes:int, sgdim:int=3):
    points = []
    point_ids = {}
    counter = 0
    while counter < nnodes:
        line = f.readline()
        line = line.split('#')[0].strip()
        if line == "":
            continue

        line = line.strip().split()
        point_id, coords = line[0], line[1:]
        point_ids[int(point_id)] = counter
        points.append([0.0,]*(3-sgdim)+[float(x) for x in coords])
        counter += 1

    return np.array(points, dtype=float), point_ids, line


# def _read_physical_names(f, field_data):
#     line = f.readline().decode()
#     num_phys_names = int(line)
#     for _ in range(num_phys_names):
#         line = shlex.split(f.readline().decode())
#         key = line[2]
#         value = np.array(line[1::-1], dtype=int)
#         field_data[key] = value
#     _fast_forward_to_end_block(f, "PhysicalNames")


# def _read_data(f, tag, data_dict, data_size, is_ascii):
#     # Read string tags
#     num_string_tags = int(f.readline().decode())
#     string_tags = [
#         f.readline().decode().strip().replace('"', "") for _ in range(num_string_tags)
#     ]
#     # The real tags typically only contain one value, the time.
#     # Discard it.
#     num_real_tags = int(f.readline().decode())
#     for _ in range(num_real_tags):
#         f.readline()
#     num_integer_tags = int(f.readline().decode())
#     integer_tags = [int(f.readline().decode()) for _ in range(num_integer_tags)]
#     num_components = integer_tags[1]
#     num_items = integer_tags[2]
#     if is_ascii:
#         data = np.fromfile(f, count=num_items * (1 + num_components), sep=" ").reshape(
#             (num_items, 1 + num_components)
#         )
#         # The first entry is the node number
#         data = data[:, 1:]
#     else:
#         # binary
#         dtype = [("index", c_int), ("values", c_double, (num_components,))]
#         data = np.fromfile(f, count=num_items, dtype=dtype)
#         if not (data["index"] == range(1, num_items + 1)).all():
#             raise ReadError()
#         data = np.ascontiguousarray(data["values"])

#     _fast_forward_to_end_block(f, tag)

#     # The gmsh format cannot distinguish between data of shape (n,) and (n, 1).
#     # If shape[1] == 1, cut it off.
#     if data.shape[1] == 1:
#         data = data[:, 0]

#     data_dict[string_tags[0]] = data


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
            f.write('  # nodal coordinates')

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


# def _write_elements(f, cells, solver, sfi:str='8d'):

#     consecutive_index = 0
#     for k, cell_block in enumerate(cells):
#         cell_type = cell_block.type
#         node_idcs = _meshio_to_sg_order(cell_type, cell_block.data)

#         for i, c in enumerate(node_idcs):
#             _eid = consecutive_index + i + 1
#             _nums = [_eid,]  # Element id

#             if solver.lower().startswith('s'):
#                 _nums.append(self.elem_prop[_eid])

#             _nums.extend(c.tolist())

#             # Write the numbers
#             # logger.debug('sfi = {}'.format(sfi))
#             sui.writeFormatIntegers(f, _nums, fmt=sfi, newline=False)
#             if k == 0 and i == 0:
#                 f.write('  # element connectivity')
#             f.write('\n')

#         consecutive_index += len(node_idcs)

#     f.write('\n')
#     return




# def _write_physical_names(fh, field_data):
#     # Write physical names
#     entries = []
#     for phys_name in field_data:
#         try:
#             phys_num, phys_dim = field_data[phys_name]
#             phys_num, phys_dim = int(phys_num), int(phys_dim)
#             entries.append((phys_dim, phys_num, phys_name))
#         except (ValueError, TypeError):
#             warn("Field data contains entry that cannot be processed.")
#     entries.sort()
#     if entries:
#         fh.write(b"$PhysicalNames\n")
#         fh.write(f"{len(entries)}\n".encode())
#         for entry in entries:
#             fh.write('{} {} "{}"\n'.format(*entry).encode())
#         fh.write(b"$EndPhysicalNames\n")


def _write_data(fh, tag, name, data, binary):
    fh.write(f"${tag}\n".encode())
    # <http://gmsh.info/doc/texinfo/gmsh.html>:
    # > Number of string tags.
    # > gives the number of string tags that follow. By default the first
    # > string-tag is interpreted as the name of the post-processing view and
    # > the second as the name of the interpolation scheme. The interpolation
    # > scheme is provided in the $InterpolationScheme section (see below).
    fh.write(f"{1}\n".encode())
    fh.write(f'"{name}"\n'.encode())
    fh.write(f"{1}\n".encode())
    fh.write(f"{0.0}\n".encode())
    # three integer tags:
    fh.write(f"{3}\n".encode())
    # time step
    fh.write(f"{0}\n".encode())
    # number of components
    num_components = data.shape[1] if len(data.shape) > 1 else 1
    if num_components not in [1, 3, 9]:
        raise WriteError("Gmsh only permits 1, 3, or 9 components per data field.")

    # Cut off the last dimension in case it's 1. This avoids problems with
    # writing the data.
    if len(data.shape) > 1 and data.shape[1] == 1:
        data = data[:, 0]

    fh.write(f"{num_components}\n".encode())
    # num data items
    fh.write(f"{data.shape[0]}\n".encode())
    # actually write the data
    if binary:
        if num_components == 1:
            dtype = [("index", c_int), ("data", c_double)]
        else:
            dtype = [("index", c_int), ("data", c_double, num_components)]
        tmp = np.empty(len(data), dtype=dtype)
        tmp["index"] = 1 + np.arange(len(data))
        tmp["data"] = data
        tmp.tofile(fh)
        fh.write(b"\n")
    else:
        fmt = " ".join(["{}"] + ["{!r}"] * num_components) + "\n"
        # TODO unify
        if num_components == 1:
            for k, x in enumerate(data):
                fh.write(fmt.format(k + 1, x).encode())
        else:
            for k, x in enumerate(data):
                fh.write(fmt.format(k + 1, *x).encode())

    fh.write(f"$End{tag}\n".encode())
