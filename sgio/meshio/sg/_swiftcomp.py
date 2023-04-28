"""
I/O for SwiftComp sg format
"""
from __future__ import annotations

import numpy as np

from .._common import cell_data_from_raw, num_nodes_per_cell, raw_from_cell_data, warn
from .._exceptions import ReadError
from .._mesh import CellBlock, Mesh
from .common import (
    _fast_forward_over_blank_lines,
    _fast_forward_to_end_block,
    _meshio_to_gmsh_order,
    _meshio_to_gmsh_type,
    _read_data,
    _read_physical_names,
    _write_data,
    _write_physical_names,
)

c_int = np.dtype("i")
c_double = np.dtype("d")

def write(filename, mesh, float_fmt=".16e", binary=True):
    """Writes msh files, cf.
    <http://gmsh.info//doc/texinfo/gmsh.html#MSH-ASCII-file-format>.
    """
    # Filter the point data: gmsh:dim_tags are tags, the rest is actual point data.
    point_data = {}
    for key, d in mesh.point_data.items():
        if key not in ["gmsh:dim_tags"]:
            point_data[key] = d

    # Split the cell data: gmsh:physical and gmsh:geometrical are tags, the rest is
    # actual cell data.
    tag_data = {}
    cell_data = {}
    for key, d in mesh.cell_data.items():
        if key in ["gmsh:physical", "gmsh:geometrical", "cell_tags"]:
            tag_data[key] = d
        else:
            cell_data[key] = d

    # Always include the physical and geometrical tags. See also the quoted excerpt from
    # the gmsh documentation in the _read_cells_ascii function above.
    for tag in ["gmsh:physical", "gmsh:geometrical"]:
        if tag not in tag_data:
            warn(f"Appending zeros to replace the missing {tag[5:]} tag data.")
            tag_data[tag] = [
                np.zeros(len(cell_block), dtype=c_int) for cell_block in mesh.cells
            ]

    with open(filename, "wb") as fh:
        mode_idx = 1 if binary else 0
        size_of_double = 8
        fh.write(f"$MeshFormat\n2.2 {mode_idx} {size_of_double}\n".encode())
        if binary:
            np.array([1], dtype=c_int).tofile(fh)
            fh.write(b"\n")
        fh.write(b"$EndMeshFormat\n")

        if mesh.field_data:
            _write_physical_names(fh, mesh.field_data)

        _write_nodes(fh, mesh.points, float_fmt, binary)
        _write_elements(fh, mesh.cells, tag_data, binary)
        if mesh.gmsh_periodic is not None:
            _write_periodic(fh, mesh.gmsh_periodic, float_fmt)

        for name, dat in point_data.items():
            _write_data(fh, "NodeData", name, dat, binary)
        cell_data_raw = raw_from_cell_data(cell_data)
        for name, dat in cell_data_raw.items():
            _write_data(fh, "ElementData", name, dat, binary)


def _write_nodes(fh, points, float_fmt, binary):
    if points.shape[1] == 2:
        # msh2 requires 3D points, but 2D points given. Appending 0 third component.
        points = np.column_stack([points, np.zeros_like(points[:, 0])])

    fh.write(b"$Nodes\n")
    fh.write(f"{len(points)}\n".encode())
    if binary:
        dtype = [("index", c_int), ("x", c_double, (3,))]
        tmp = np.empty(len(points), dtype=dtype)
        tmp["index"] = 1 + np.arange(len(points))
        tmp["x"] = points
        tmp.tofile(fh)
        fh.write(b"\n")
    else:
        fmt = "{} " + " ".join(3 * ["{:" + float_fmt + "}"]) + "\n"
        for k, x in enumerate(points):
            fh.write(fmt.format(k + 1, x[0], x[1], x[2]).encode())
    fh.write(b"$EndNodes\n")


def _write_elements(fh, cells: list[CellBlock], tag_data, binary: bool):
    # write elements
    fh.write(b"$Elements\n")

    # count all cells
    total_num_cells = sum(len(cell_block) for cell_block in cells)
    fh.write(f"{total_num_cells}\n".encode())

    consecutive_index = 0
    for k, cell_block in enumerate(cells):
        cell_type = cell_block.type
        node_idcs = _meshio_to_gmsh_order(cell_type, cell_block.data)

        tags = []
        for name in ["gmsh:physical", "gmsh:geometrical", "cell_tags"]:
            if name in tag_data:
                tags.append(tag_data[name][k])
        fcd = np.concatenate([tags]).astype(c_int).T

        if len(fcd) == 0:
            fcd = np.empty((len(node_idcs), 0), dtype=c_int)

        if binary:
            # header
            header = [_meshio_to_gmsh_type[cell_type], node_idcs.shape[0], fcd.shape[1]]
            np.array(header, dtype=c_int).tofile(fh)
            # actual data
            a = np.arange(len(node_idcs), dtype=c_int)[:, np.newaxis]
            a += 1 + consecutive_index
            array = np.hstack([a, fcd, node_idcs + 1])
            if array.dtype != c_int:
                array = array.astype(c_int)
            array.tofile(fh)
        else:
            form = (
                "{} "
                + str(_meshio_to_gmsh_type[cell_type])
                + " "
                + str(fcd.shape[1])
                + " {} {}\n"
            )
            for i, c in enumerate(node_idcs):
                fh.write(
                    form.format(
                        consecutive_index + i + 1,
                        " ".join([str(val) for val in fcd[i]]),
                        # a bit clumsy for `c+1`, but if c is uint64, c+1 is float64
                        " ".join([str(cc) for cc in c + np.array(1, dtype=c.dtype)]),
                    ).encode()
                )

        consecutive_index += len(node_idcs)
    if binary:
        fh.write(b"\n")
    fh.write(b"$EndElements\n")

