from __future__ import annotations

import logging
import numpy as np
from meshio import CellBlock
from meshio.gmsh._gmsh22 import (
    c_int,
    c_double,
    read_buffer,
    _read_nodes,
    _read_cells,
    _read_cells_ascii,
    _read_cells_binary,
    _read_periodic,
    _write_periodic,
)

logger = logging.getLogger(__name__)

from ._common import (
    _fast_forward_over_blank_lines,
    _fast_forward_to_end_block,
    _gmsh_to_meshio_order,
    _gmsh_to_meshio_type,
    _meshio_to_gmsh_order,
    _meshio_to_gmsh_type,
    _read_data,
    _read_physical_names,
    _write_data,
    _write_physical_names,
)
from sgio.iofunc._meshio import (
    warn,
    raw_from_cell_data,
)


def write_buffer(file, mesh, float_fmt=".16e", binary=False, **kwargs):
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
        elif key in ["property_id",]:
            tag_data["gmsh:physical"] = d
            tag_data["gmsh:geometrical"] = d
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

    # with open(filename, "wb") as fh:
    mode_idx = 1 if binary else 0
    size_of_double = 8
    file.write(f"$MeshFormat\n")
    if binary:
        file.write(f"2.2 {mode_idx} {size_of_double}\n".encode())
    else:
        file.write(f"2.2 {mode_idx} {size_of_double}\n")

    if binary:
        np.array([1], dtype=c_int).tofile(file)
        file.write(b"\n")
        file.write(b"$EndMeshFormat\n")
    else:
        file.write("$EndMeshFormat\n")

    if mesh.field_data:
        _write_physical_names(file, mesh.field_data)

    _write_nodes(file, mesh.points, float_fmt, binary)
    _write_elements(file, mesh.cells, tag_data, binary)
    if mesh.gmsh_periodic is not None:
        _write_periodic(file, mesh.gmsh_periodic, float_fmt)

    for name, dat in point_data.items():
        _write_data(file, "NodeData", name, dat, binary)
    cell_data_raw = raw_from_cell_data(cell_data)
    for name, dat in cell_data_raw.items():
        _write_data(file, "ElementData", name, dat, binary)

    # Write cell_point_data (element nodal data) to ElementNodeData sections
    if hasattr(mesh, 'cell_point_data') and mesh.cell_point_data:
        _write_cell_point_data(file, mesh, binary)


def _write_nodes(fh, points, float_fmt, binary):
    if points.shape[1] == 2:
        # msh2 requires 3D points, but 2D points given. Appending 0 third component.
        points = np.column_stack([points, np.zeros_like(points[:, 0])])

    if binary:
        fh.write(b"$Nodes\n")
        fh.write(f"{len(points)}\n".encode())
    else:
        fh.write("$Nodes\n")
        fh.write(f"{len(points)}\n")

    if binary:
        dtype = [("index", c_int), ("x", c_double, (3,))]
        tmp = np.empty(len(points), dtype=dtype)
        tmp["index"] = 1 + np.arange(len(points))
        tmp["x"] = points
        tmp.tofile(fh)
        fh.write(b"\n")
        fh.write(b"$EndNodes\n")
    else:
        fmt = "{} " + " ".join(3 * ["{:" + float_fmt + "}"]) + "\n"
        for k, x in enumerate(points):
            fh.write(fmt.format(k + 1, x[0], x[1], x[2]))
        fh.write("$EndNodes\n")


def _write_elements(fh, cells: list[CellBlock], tag_data, binary: bool):
    # write elements
    if binary:
        fh.write(b"$Elements\n")
    else:
        fh.write("$Elements\n")

    # count all cells
    total_num_cells = sum(len(cell_block) for cell_block in cells)
    if binary:
        fh.write(f"{total_num_cells}\n".encode())
    else:
        fh.write(f"{total_num_cells}\n")

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
                    )
                )

        consecutive_index += len(node_idcs)
    if binary:
        # fh.write(b"\n")
        fh.write(b"$EndElements\n")
    else:
        # fh.write("\n")
        fh.write("$EndElements\n")


def _write_cell_point_data(fh, mesh, binary: bool) -> None:
    """Write cell_point_data (element nodal data) to $ElementNodeData sections.

    Parameters
    ----------
    fh : file
        File handle to write to
    mesh : SGMesh
        Mesh object containing cell_point_data
    binary : bool
        Whether to write in binary mode

    Notes
    -----
    The $ElementNodeData format is:
        $ElementNodeData
          numStringTags(ASCII int)
          stringTag(string) ...
          numRealTags(ASCII int)
          realTag(ASCII double) ...
          numIntegerTags(ASCII int)
          integerTag(ASCII int) ...
          elementTag(int) numNodesPerElement(int) value(double) ...
          ...
        $EndElementNodeData

    The cell_point_data structure is:
        {name: [array_for_cell_block_0, array_for_cell_block_1, ...]}
    where each array has shape (n_elements, n_nodes_per_element) for single component
    or (n_elements, n_nodes_per_element, n_components) for multi-component data.
    """
    # Get element IDs from cell_data
    if 'element_id' not in mesh.cell_data:
        logger.warning("Cannot write cell_point_data: mesh.cell_data['element_id'] not found")
        return

    element_ids = mesh.cell_data['element_id']

    # Process each field in cell_point_data
    for field_name, cell_blocks_data in mesh.cell_point_data.items():
        # Determine number of components from the data shape
        first_block_data = cell_blocks_data[0]
        if len(first_block_data.shape) == 2:
            # Shape: (n_elements, n_nodes_per_element) - single component
            num_components = 1
        elif len(first_block_data.shape) == 3:
            # Shape: (n_elements, n_nodes_per_element, n_components)
            num_components = first_block_data.shape[2]
        else:
            logger.warning(f"Unexpected shape for cell_point_data '{field_name}': {first_block_data.shape}")
            continue

        # Count total number of elements across all cell blocks
        total_elements = sum(len(block_data) for block_data in cell_blocks_data)

        # Write header
        if binary:
            fh.write(b"$ElementNodeData\n")
            # 1 string tag: field name
            fh.write(f"{1}\n".encode())
            fh.write(f'"{field_name}"\n'.encode())
            # 1 real tag: time value
            fh.write(f"{1}\n".encode())
            fh.write(f"{0.0}\n".encode())
            # 3 integer tags: time step, num components, num elements
            fh.write(f"{3}\n".encode())
            fh.write(f"{0}\n".encode())  # time step
            fh.write(f"{num_components}\n".encode())
            fh.write(f"{total_elements}\n".encode())
        else:
            fh.write("$ElementNodeData\n")
            # 1 string tag: field name
            fh.write(f"{1}\n")
            fh.write(f'"{field_name}"\n')
            # 1 real tag: time value
            fh.write(f"{1}\n")
            fh.write(f"{0.0}\n")
            # 3 integer tags: time step, num components, num elements
            fh.write(f"{3}\n")
            fh.write(f"{0}\n")  # time step
            fh.write(f"{num_components}\n")
            fh.write(f"{total_elements}\n")

        # Write data for each element across all cell blocks
        for block_idx, block_data in enumerate(cell_blocks_data):
            block_element_ids = element_ids[block_idx]

            for elem_idx, elem_data in enumerate(block_data):
                elem_id = int(block_element_ids[elem_idx])

                # elem_data shape: (n_nodes_per_element,) or (n_nodes_per_element, n_components)
                if num_components == 1:
                    # Single component: elem_data is 1D array
                    num_nodes = len(elem_data)
                    if binary:
                        np.array([elem_id], dtype=c_int).tofile(fh)
                        np.array([num_nodes], dtype=c_int).tofile(fh)
                        elem_data.astype(c_double).tofile(fh)
                    else:
                        fh.write(f"{elem_id} {num_nodes}")
                        for val in elem_data:
                            fh.write(f" {float(val)}")
                        fh.write("\n")
                else:
                    # Multi-component: elem_data is 2D array (n_nodes, n_components)
                    num_nodes = elem_data.shape[0]
                    if binary:
                        np.array([elem_id], dtype=c_int).tofile(fh)
                        np.array([num_nodes], dtype=c_int).tofile(fh)
                        # Flatten the data: all components for node 1, then node 2, etc.
                        elem_data.astype(c_double).flatten().tofile(fh)
                    else:
                        fh.write(f"{elem_id} {num_nodes}")
                        for node_vals in elem_data:
                            for val in node_vals:
                                fh.write(f" {float(val)}")
                        fh.write("\n")

        # Write footer
        if binary:
            fh.write(b"\n")
            fh.write(b"$EndElementNodeData\n")
        else:
            fh.write("$EndElementNodeData\n")



