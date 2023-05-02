"""
I/O for MSG-SwiftComp/VABS sg files.
"""
import pathlib
from itertools import count

import numpy as np

# from ..__about__ import __version__
# from .._common import num_nodes_per_cell
from .._exceptions import ReadError, WriteError
from .._files import is_buffer, open_file
from .._helpers import register_format
from .._mesh import CellBlock, Mesh

from . import _vabs, _swiftcomp

_readers = {"vabs": _vabs, "swiftcomp": _swiftcomp, "sc": _swiftcomp}
_writers = {"vabs": _vabs, "swiftcomp": _swiftcomp, "sc": _swiftcomp}


def read(
    filename, file_format, sgdim:int, nnode:int, nelem:int, read_local_frame
) -> None:
    try:
        reader = _readers[file_format]
    except KeyError:
        raise WriteError(
            "Need mesh format in {} (got {})".format(
                sorted(_readers.keys()), file_format
            )
        )

    return reader.read(filename, sgdim, nnode, nelem, read_local_frame)


# def read(filename, **kwargs):
#     """Reads a Gmsh msh file."""
#     if is_buffer(filename, 'r'):
#         mesh = read_buffer(filename, **kwargs)
#     else:
#         with open(filename, 'r') as file:
#             mesh = read_buffer(file, **kwargs)
#     return mesh


# def read_buffer(f, **kwargs):
#     # The various versions of the format are specified at
#     # <http://gmsh.info/doc/texinfo/gmsh.html#File-formats>.
#     line = f.readline().decode().strip()

#     try:
#         reader = _readers[fmt_version]
#     except KeyError:
#         try:
#             reader = _readers[fmt_version.split(".")[0]]
#         except KeyError:
#             raise ValueError(
#                 "Need mesh format in {} (got {})".format(
#                     sorted(_readers.keys()), fmt_version
#                 )
#             )
#     return reader.read_buffer(f, is_ascii, data_size)


# def merge(
#     mesh, points, cells, point_data, cell_data, field_data, point_sets, cell_sets
# ):
#     """
#     Merge Mesh object into existing containers for points, cells, sets, etc..

#     :param mesh:
#     :param points:
#     :param cells:
#     :param point_data:
#     :param cell_data:
#     :param field_data:
#     :param point_sets:
#     :param cell_sets:
#     :type mesh: Mesh
#     """
#     ext_points = np.array([p for p in mesh.points])

#     if len(points) > 0:
#         new_point_id = points.shape[0]
#         # new_cell_id = len(cells) + 1
#         points = np.concatenate([points, ext_points])
#     else:
#         # new_cell_id = 0
#         new_point_id = 0
#         points = ext_points

#     cnt = 0
#     for c in mesh.cells:
#         new_data = np.array([d + new_point_id for d in c.data])
#         cells.append(CellBlock(c.type, new_data))
#         cnt += 1

#     # The following aren't currently included in the abaqus parser, and are therefore
#     # excluded?
#     # point_data.update(mesh.point_data)
#     # cell_data.update(mesh.cell_data)
#     # field_data.update(mesh.field_data)

#     # Update point and cell sets to account for change in cell and point ids
#     for key, val in mesh.point_sets.items():
#         point_sets[key] = [x + new_point_id for x in val]

#     # Todo: Add support for merging cell sets
#     # cellblockref = [[] for i in range(cnt-new_cell_id)]
#     # for key, val in mesh.cell_sets.items():
#     #     cell_sets[key] = cellblockref + [np.array([x for x in val[0]])]

#     return points, cells


def write(
    filename, mesh: Mesh, file_format, sgdim,
    int_fmt:str="8d", float_fmt:str="20.9e"
) -> None:
    try:
        writer = _writers[file_format]
    except KeyError:
        raise WriteError(
            "Need mesh format in {} (got {})".format(
                sorted(_writers.keys()), file_format
            )
        )

    writer.write(filename, mesh, sgdim, int_fmt=int_fmt, float_fmt=float_fmt)






register_format(
    "vabs", [".vabs", ".sg"],
    lambda f, **kwargs: read(f, 'vabs', **kwargs),
    {"vabs": lambda f, m, **kwargs: write(f, m, 'vabs', **kwargs)}
)

register_format(
    "sc", [".sc", ".sg"],
    lambda f, **kwargs: read(f, 'sc', **kwargs),
    {"sc": lambda f, m, **kwargs: write(f, m, 'sc', **kwargs)}
)

