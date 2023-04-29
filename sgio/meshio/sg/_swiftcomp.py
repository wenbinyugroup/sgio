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
    _write_elements(file, mesh.cells, mesh.cell_data['property_id'], int_fmt)
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



def _write_elements(f, cells, cell_prop_ids, int_fmt:str='8d'):
    """
    """
    sfi = '{:' + int_fmt + '}'

    consecutive_index = 0
    for k, cell_block in enumerate(cells):
        cell_type = cell_block.type
        node_idcs = _meshio_to_sg_order(cell_type, cell_block.data)

        for i, c in enumerate(node_idcs):
            _eid = consecutive_index + i + 1
            _pid = cell_prop_ids[k][i]

            _nums = [_eid, _pid]  # Element id, property id

            _nums.extend(c.tolist())

            # Write the numbers
            fmt = ''.join([sfi,]*len(_nums))
            f.write(fmt.format(*_nums))
            # logger.debug('sfi = {}'.format(sfi))
            # sui.writeFormatIntegers(f, _nums, fmt=sfi, newline=False)
            if k == 0 and i == 0:
                f.write('  # element connectivity')
            f.write('\n')

        consecutive_index += len(node_idcs)

    f.write('\n')
    return