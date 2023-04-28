"""
I/O for MSG-SwiftComp/VABS sg files.
"""
import pathlib
from itertools import count

import numpy as np

# from ..__about__ import __version__
# from .._common import num_nodes_per_cell
# from .._exceptions import ReadError
from .._files import open_file
from .._helpers import register_format
from .._mesh import CellBlock, Mesh

from . import _vabs, _swiftcomp

_readers = {"vabs": _vabs, "swiftcomp": _swiftcomp, "sc": _swiftcomp}
_writers = {"vabs": _vabs, "swiftcomp": _swiftcomp, "sc": _swiftcomp}


def read(filename):
    """Reads a SG file."""
    filename = pathlib.Path(filename)
    with open_file(filename, "r") as f:
        mesh = read_buffer(f)
    return mesh


def read_buffer(f):
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

    line = f.readline()
    while True:
        if not line:  # EOF
            break

        # Comments
        if line.startswith("**"):
            line = f.readline()
            continue

    # Parse cell sets defined in ELEMENT
    for i, name in enumerate(cell_sets_element_order):
        # Not sure whether this case would ever happen
        if name in cell_sets.keys():
            cell_sets[name][i] = cell_sets_element[name]
        else:
            cell_sets[name] = []
            for ic in range(len(cells)):
                cell_sets[name].append(
                    cell_sets_element[name] if i == ic else np.array([], dtype="int32")
                )

    return Mesh(
        points,
        cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        point_sets=point_sets,
        cell_sets=cell_sets,
    )


def _read_nodes(f):
    return


def _read_cells(f):
    return


def merge(
    mesh, points, cells, point_data, cell_data, field_data, point_sets, cell_sets
):
    """
    Merge Mesh object into existing containers for points, cells, sets, etc..

    :param mesh:
    :param points:
    :param cells:
    :param point_data:
    :param cell_data:
    :param field_data:
    :param point_sets:
    :param cell_sets:
    :type mesh: Mesh
    """
    ext_points = np.array([p for p in mesh.points])

    if len(points) > 0:
        new_point_id = points.shape[0]
        # new_cell_id = len(cells) + 1
        points = np.concatenate([points, ext_points])
    else:
        # new_cell_id = 0
        new_point_id = 0
        points = ext_points

    cnt = 0
    for c in mesh.cells:
        new_data = np.array([d + new_point_id for d in c.data])
        cells.append(CellBlock(c.type, new_data))
        cnt += 1

    # The following aren't currently included in the abaqus parser, and are therefore
    # excluded?
    # point_data.update(mesh.point_data)
    # cell_data.update(mesh.cell_data)
    # field_data.update(mesh.field_data)

    # Update point and cell sets to account for change in cell and point ids
    for key, val in mesh.point_sets.items():
        point_sets[key] = [x + new_point_id for x in val]

    # Todo: Add support for merging cell sets
    # cellblockref = [[] for i in range(cnt-new_cell_id)]
    # for key, val in mesh.cell_sets.items():
    #     cell_sets[key] = cellblockref + [np.array([x for x in val[0]])]

    return points, cells


def write(
    filename, mesh: Mesh, file_format, int_fmt: str = "8d", float_fmt: str = ".16e"
) -> None:
    with open_file(filename, "at") as f:
        write_buffer(f, mesh, file_format, int_fmt, float_fmt)

def write_buffer(
    file, mesh: Mesh, file_format, int_fmt: str = "8d", float_fmt: str = ".16e"
) -> None:
    pass





register_format(
    "vabs", [".sg"], read, {"vabs": write})

