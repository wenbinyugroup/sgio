from __future__ import annotations

import numpy as np


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
    WriteError
)

c_int = np.dtype("i")
c_size_t = np.dtype("P")
c_double = np.dtype("d")

def write_buffer(file, mesh, float_fmt=".16e", binary=True, **kwargs):
    """Writes msh files, cf.
    <http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format>.
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

    # with open(filename, "wb") as fh:
    file_type = 1 if binary else 0
    data_size = c_size_t.itemsize
    file.write(f"$MeshFormat\n")
    if binary:
        file.write(f"4.1 {file_type} {data_size}\n".encode())
    else:
        file.write(f"4.1 {file_type} {data_size}\n")

    if binary:
        np.array([1], dtype=c_int).tofile(file)
        file.write(b"\n")
        file.write(b"$EndMeshFormat\n")
    else:
        file.write("$EndMeshFormat\n")

    if mesh.field_data:
        _write_physical_names(file, mesh.field_data)

    _write_entities(
        file, mesh.cells, tag_data, mesh.cell_sets, mesh.point_data, binary
    )
    _write_nodes(file, mesh.points, mesh.cells, mesh.point_data, float_fmt, binary)
    _write_elements(file, mesh.cells, tag_data, binary)
    if mesh.gmsh_periodic is not None:
        _write_periodic(file, mesh.gmsh_periodic, float_fmt, binary)

    for name, dat in point_data.items():
        _write_data(file, "NodeData", name, dat, binary)
    cell_data_raw = raw_from_cell_data(cell_data)
    for name, dat in cell_data_raw.items():
        _write_data(file, "ElementData", name, dat, binary)


def _write_entities(fh, cells, tag_data, cell_sets, point_data, binary):
    """Write entity section in a .msh file.

    The entity section links up to three kinds of information:
        1) The geometric objects represented in the mesh.
        2) Physical tags of geometric objects. This data will be a subset
           of that represented in 1)
        3) Which geometric objects form the boundary of this object.
           The boundary is formed of objects with dimension 1 less than
           the current one. A boundary can only be specified for objects of
           dimension at least 1.

    The entities of all geometric objects is pulled from
    point_data['gmsh:dim_tags']. For details, see the function _write_nodes().

    Physical tags are specified as tag_data, while the boundary of a geometric
    object is specified in cell_sets.

    """

    # The data format for the entities section is
    #
    #    numPoints(size_t) numCurves(size_t)
    #      numSurfaces(size_t) numVolumes(size_t)
    #    pointTag(int) X(double) Y(double) Z(double)
    #      numPhysicalTags(size_t) physicalTag(int) ...
    #    ...
    #    curveTag(int) minX(double) minY(double) minZ(double)
    #      maxX(double) maxY(double) maxZ(double)
    #      numPhysicalTags(size_t) physicalTag(int) ...
    #      numBoundingPoints(size_t) pointTag(int) ...
    #    ...
    #    surfaceTag(int) minX(double) minY(double) minZ(double)
    #      maxX(double) maxY(double) maxZ(double)
    #      numPhysicalTags(size_t) physicalTag(int) ...
    #      numBoundingCurves(size_t) curveTag(int) ...
    #    ...
    #    volumeTag(int) minX(double) minY(double) minZ(double)
    #      maxX(double) maxY(double) maxZ(double)
    #      numPhysicalTags(size_t) physicalTag(int) ...
    #      numBoundngSurfaces(size_t) surfaceTag(int) ...

    # Both nodes and cells have entities, but the cell entities are a subset of
    # the nodes. The reason is (if the inner workings of Gmsh has been correctly
    # understood) that node entities are assigned to all
    # objects necessary to specify the geometry whereas only cells of Physical
    # objcets (gmsh jargon) are present among the cell entities.
    # The entities section must therefore be built on the node-entities, if
    # these are available. If this is not the case, we leave this section blank.
    # TODO: Should this give a warning?
    if "gmsh:dim_tags" not in point_data:
        return

    # print(f'tag_data: {tag_data}')

    if binary:
        fh.write(b"$Entities\n")
    else:
        fh.write("$Entities\n")

    # Array of entity tag (first row) and dimension (second row) per node.
    # We need to combine the two, since entity tags are reset for each dimension.
    # Uniquify, so that each row in node_dim_tags represent a unique entity
    node_dim_tags = np.unique(point_data["gmsh:dim_tags"], axis=0)

    # Write number of entities per dimension
    num_occ = np.bincount(node_dim_tags[:, 0], minlength=4)
    if num_occ.size > 4:
        raise ValueError("Encountered entity with dimension > 3")

    if binary:
        num_occ.astype(c_size_t).tofile(fh)
    else:
        fh.write(f"{num_occ[0]} {num_occ[1]} {num_occ[2]} {num_occ[3]}\n")

    # Array of dimension and entity tag per cell. Will be compared with the
    # similar not array.
    cell_dim_tags = np.empty((len(cells), 2), dtype=int)
    for ci, cell_block in enumerate(cells):
        cell_dim_tags[ci] = [
            cell_block.dim,
            tag_data["gmsh:geometrical"][ci][0],
        ]

    # We will only deal with bounding entities if this information is available
    has_bounding_elements = "gmsh:bounding_entities" in cell_sets

    # The node entities form a superset of cell entities. Write entity information
    # based on nodes, supplement with cell information when there is a matcihng
    # cell block.
    for dim, tag in node_dim_tags:
        # Find the matching cell block, if it exists
        matching_cell_block = np.where(
            np.logical_and(cell_dim_tags[:, 0] == dim, cell_dim_tags[:, 1] == tag)
        )[0]
        if matching_cell_block.size > 1:
            # It is not 100% clear if this is not permissible, but the current
            # implementation for sure does not allow it.
            raise ValueError("Encountered non-unique CellBlock dim_tag")

        # The information to be written varies according to entity dimension,
        # whether entity has a physical tag, and between ascii and binary.
        # The resulting code is a bit ugly, but no simpler and clean option
        # seems possible.

        # Entity tag
        if binary:
            np.array([tag], dtype=c_int).tofile(fh)
        else:
            fh.write(f"{tag} ")

        # Min-max coordinates for the entity. For now, simply put zeros here,
        # and hope that gmsh does not complain. To expand this, the point
        # coordinates must be made available to this function; the bounding
        # box can then be found by a min-max over the points of the matching
        # cell.
        if dim == 0:
            # Bounding box is a point
            if binary:
                np.zeros(3, dtype=c_double).tofile(fh)
            else:
                fh.write("0 0 0 ")
        else:
            # Bounding box has six coordinates
            if binary:
                np.zeros(6, dtype=c_double).tofile(fh)
            else:
                fh.write("0 0 0 0 0 0 ")

        # If there is a corresponding cell block, write physical tags (if any)
        # and bounding entities (if any)
        if matching_cell_block.size > 0:
            # entity has a physical tag, write this
            # ASSUMPTION: There is a single physical tag for this
            try:
                physical_tag = tag_data["gmsh:physical"][matching_cell_block[0]][0]
                if binary:
                    np.array([1], dtype=c_size_t).tofile(fh)
                    np.array([physical_tag], dtype=c_int).tofile(fh)
                else:
                    fh.write(f"1 {physical_tag} ")
            except KeyError:
                pass
        else:
            # The number of physical tags is zero
            if binary:
                np.array([0], dtype=c_size_t).tofile(fh)
            else:
                fh.write("0 ")

        if dim > 0:
            # Entities not of the lowest dimension can have their
            # bounding elements (of dimension one less) specified
            if has_bounding_elements and matching_cell_block.size > 0:
                # The bounding element should be a list
                bounds = cell_sets["gmsh:bounding_entities"][matching_cell_block[0]]
                num_bounds = len(bounds)
                if num_bounds > 0:
                    if binary:
                        np.array(num_bounds, dtype=c_size_t).tofile(fh)
                        np.array(bounds, dtype=c_int).tofile(fh)
                    else:
                        fh.write(f"{num_bounds} ")
                        for bi in bounds:
                            fh.write(f"{bi} ")
                        fh.write("\n")
                else:
                    # Register that there are no bounding elements
                    if binary:
                        np.array([0], dtype=c_size_t).tofile(fh)
                    else:
                        fh.write("0\n")

            else:
                # Register that there are no bounding elements
                if binary:
                    np.array([0], dtype=c_size_t).tofile(fh)
                else:
                    fh.write("0\n")
        else:
            # If ascii, enforce line change
            if not binary:
                fh.write("\n")

    if binary:
        fh.write(b"\n")
    # raise NotImplementedError
        fh.write(b"$EndEntities\n")
    else:
        fh.write("\n")
    # raise NotImplementedError
        fh.write("$EndEntities\n")


def _write_nodes(fh, points, cells, point_data, float_fmt, binary):
    """Write node information.

    If data on dimension and tags of the geometric entities which the nodes belong to
    is available available, the nodes will be grouped accordingly. This data is
    specified as point_data, using the key 'gmsh:dim_tags' and data as an
    num_points x 2 numpy array (first column is the dimension of the geometric entity
    of this node, second is the tag).

    If dim_tags are not available, all nodes will be assigned the same tag of 0. This
    only makes sense if a single cell block is present in the mesh; an error will be
    raised if len(cells) > 1.

    """
    if points.shape[1] == 2:
        # msh4 requires 3D points, but 2D points given.
        # Appending 0 third component.
        points = np.column_stack([points, np.zeros_like(points[:, 0])])

    fh.write(f"$Nodes\n")

    # The format for the nodes section is
    #
    # $Nodes
    #   numEntityBlocks(size_t) numNodes(size_t) minNodeTag(size_t) maxNodeTag(size_t)
    #   entityDim(int) entityTag(int) parametric(int; 0 or 1)
    #   numNodesInBlock(size_t)
    #     nodeTag(size_t)
    #     ...
    #     x(double) y(double) z(double)
    #        < u(double; if parametric and entityDim >= 1) >
    #        < v(double; if parametric and entityDim >= 2) >
    #        < w(double; if parametric and entityDim == 3) >
    #     ...
    #   ...
    # $EndNodes
    #
    n = points.shape[0]
    min_tag = 1
    max_tag = n
    is_parametric = 0

    # If node (entity) tag and dimension is available, we make a list of unique
    # combinations thereof, and a map from the full node set to the unique
    # set.
    if "gmsh:dim_tags" in point_data:
        # reverse_index_map maps from all nodes to their respective representation in
        # (the uniquified) node_dim_tags. This approach works for general orderings of
        # the nodes
        node_dim_tags, reverse_index_map = np.unique(
            point_data["gmsh:dim_tags"],
            axis=0,
            return_inverse=True,
        )
    else:
        # If entity information is not provided, we will assign the same entity for all
        # nodes. This only makes sense if the cells are of a single type
        if len(cells) != 1:
            raise WriteError(
                "Specify entity information (gmsh:dim_tags in point_data) "
                + "to deal with more than one cell type. "
            )

        dim = cells[0].dim
        tag = 0
        node_dim_tags = np.array([[dim, tag]])
        # All nodes map to the (single) dimension-entity object
        reverse_index_map = np.full(n, 0, dtype=int)

    num_blocks = node_dim_tags.shape[0]

    # First write preamble
    if binary:
        if points.dtype != c_double:
            warn(f"Binary Gmsh needs c_double points (got {points.dtype}). Converting.")
            points = points.astype(c_double)
        np.array([num_blocks, n, min_tag, max_tag], dtype=c_size_t).tofile(fh)
    else:
        fh.write(f"{num_blocks} {n} {min_tag} {max_tag}\n")

    for j in range(num_blocks):
        dim, tag = node_dim_tags[j]

        node_tags = np.where(reverse_index_map == j)[0]
        num_points_this = node_tags.size

        if binary:
            np.array([dim, tag, is_parametric], dtype=c_int).tofile(fh)
            np.array([num_points_this], dtype=c_size_t).tofile(fh)
            (node_tags + 1).astype(c_size_t).tofile(fh)
            points[node_tags].tofile(fh)
        else:
            fh.write(f"{dim} {tag} {is_parametric} {num_points_this}\n")
            (node_tags + 1).astype(c_size_t).tofile(fh, "\n", "%d")
            fh.write("\n")
            np.savetxt(fh, points[node_tags], delimiter=" ", fmt="%" + float_fmt)

    if binary:
        fh.write(b"\n")
        fh.write(b"$EndNodes\n")
    else:
        fh.write("\n")
        fh.write("$EndNodes\n")


def _write_elements(fh, cells, tag_data, binary: bool) -> None:
    """write the $Elements block

    $Elements
      numEntityBlocks(size_t)
      numElements(size_t) minElementTag(size_t) maxElementTag(size_t)
      entityDim(int) entityTag(int) elementType(int; see below) numElementsInBlock(size_t)
        elementTag(size_t) nodeTag(size_t) ...
        ...
      ...
    $EndElements
    """
    fh.write(f"$Elements\n")

    total_num_cells = sum(len(c) for c in cells)
    num_blocks = len(cells)
    min_element_tag = 1
    max_element_tag = total_num_cells
    if binary:
        np.array(
            [num_blocks, total_num_cells, min_element_tag, max_element_tag],
            dtype=c_size_t,
        ).tofile(fh)

        tag0 = 1
        for ci, cell_block in enumerate(cells):
            node_idcs = _meshio_to_gmsh_order(cell_block.type, cell_block.data)
            if node_idcs.dtype != c_size_t:
                # Binary Gmsh needs c_size_t. Converting."
                node_idcs = node_idcs.astype(c_size_t)

            # entityDim(int) entityTag(int) elementType(int)
            # numElementsBlock(size_t)

            # The entity tag should be equal within a CellBlock
            if "gmsh:geometrical" in tag_data:
                entity_tag = tag_data["gmsh:geometrical"][ci][0]
            else:
                entity_tag = 0

            cell_type = _meshio_to_gmsh_type[cell_block.type]
            np.array([cell_block.dim, entity_tag, cell_type], dtype=c_int).tofile(fh)
            n = node_idcs.shape[0]
            np.array([n], dtype=c_size_t).tofile(fh)

            if node_idcs.dtype != c_size_t:
                warn(
                    f"Binary Gmsh cells need c_size_t (got {node_idcs.dtype}). "
                    + "Converting."
                )
                node_idcs = node_idcs.astype(c_size_t)

            np.column_stack(
                [
                    np.arange(tag0, tag0 + n, dtype=c_size_t),
                    # increment indices by one to conform with gmsh standard
                    node_idcs + 1,
                ]
            ).tofile(fh)
            tag0 += n

        fh.write(b"\n")
    else:
        fh.write(
            "{} {} {} {}\n".format(
                num_blocks, total_num_cells, min_element_tag, max_element_tag
            )
        )

        tag0 = 1
        for ci, cell_block in enumerate(cells):
            node_idcs = _meshio_to_gmsh_order(cell_block.type, cell_block.data)

            # entityDim(int) entityTag(int) elementType(int) numElementsBlock(size_t)

            # The entity tag should be equal within a CellBlock
            if "gmsh:geometrical" in tag_data:
                entity_tag = tag_data["gmsh:geometrical"][ci][0]
            else:
                entity_tag = 0

            cell_type = _meshio_to_gmsh_type[cell_block.type]
            n = len(cell_block.data)
            fh.write(f"{cell_block.dim} {entity_tag} {cell_type} {n}\n")
            np.savetxt(
                fh,
                # Gmsh indexes from 1 not 0
                np.column_stack([np.arange(tag0, tag0 + n), node_idcs + 1]),
                "%d",
                " ",
            )
            tag0 += n

    fh.write(f"$EndElements\n")


def _write_periodic(fh, periodic, float_fmt: str, binary: bool) -> None:
    """write the $Periodic block

    specified as

    $Periodic
      numPeriodicLinks(size_t)
      entityDim(int) entityTag(int) entityTagMaster(int)
      numAffine(size_t) value(double) ...
      numCorrespondingNodes(size_t)
        nodeTag(size_t) nodeTagMaster(size_t)
        ...
      ...
    $EndPeriodic

    """

    def tofile(fh, value, dtype, **kwargs):
        ary = np.array(value, dtype=dtype)
        if binary:
            ary.tofile(fh)
        else:
            ary = np.atleast_2d(ary)
            fmt = float_fmt if dtype == c_double else "d"
            fmt = "%" + kwargs.pop("fmt", fmt)
            np.savetxt(fh, ary, fmt=fmt, **kwargs)

    fh.write(f"$Periodic\n")
    tofile(fh, len(periodic), c_size_t)
    for dim, (stag, mtag), affine, slave_master in periodic:
        tofile(fh, [dim, stag, mtag], c_int)
        if affine is None or len(affine) == 0:
            tofile(fh, 0, c_size_t)
        else:
            tofile(fh, len(affine), c_size_t, newline=" ")
            tofile(fh, affine, c_double, fmt=float_fmt)
        slave_master = np.array(slave_master, dtype=c_size_t)
        slave_master = slave_master.reshape(-1, 2)
        slave_master = slave_master + 1  # Add one, Gmsh is 1-based
        tofile(fh, len(slave_master), c_size_t)
        tofile(fh, slave_master, c_size_t)
    if binary:
        fh.write(b"\n")
        fh.write(b"$EndPeriodic\n")
    else:
        fh.write("\n")
        fh.write("$EndPeriodic\n")
