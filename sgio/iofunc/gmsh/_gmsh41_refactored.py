from __future__ import annotations

import logging
from functools import partial
from typing import BinaryIO, TextIO, Union, Tuple, Dict, List, Optional

import numpy as np
import numpy.typing as npt
from meshio import CellBlock, Mesh


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
    num_nodes_per_cell,
    cell_data_from_raw,
)
from sgio.iofunc._meshio import (
    warn,
    raw_from_cell_data,
    WriteError,
    ReadError,
)

"""Gmsh 4.1 format mesh I/O.

This module implements reading and writing of Gmsh 4.1 MSH file format.
The format is specified at:
http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format

Main entry points:
    - read_buffer(): Read a Gmsh 4.1 format mesh from a file buffer
    - write_buffer(): Write a mesh to a file buffer in Gmsh 4.1 format

Both binary and ASCII formats are supported.

Format Structure:
    - $MeshFormat section: Version and mode information
    - $PhysicalNames section: Named physical groups (optional)
    - $Entities section: Geometric entities and their relationships (optional)
    - $Nodes section: Node coordinates and tags
    - $Elements section: Element connectivity
    - $Periodic section: Periodic boundary conditions (optional)
    - $NodeData/$ElementData sections: Field data (optional)
    - $ElementNodeData sections: Nodal data per element (optional)

Key Features:
    - Unified GmshWriter class for binary/ASCII output
    - Helper functions for modular code organization
    - Comprehensive type hints for IDE support
    - Support for entity tags, physical groups, and bounding entities
"""

logger = logging.getLogger(__name__)

c_int = np.dtype("i")
c_size_t = np.dtype("P")
c_double = np.dtype("d")

# Type aliases
FileHandle = Union[BinaryIO, TextIO]
DimTag = Tuple[int, int]  # (dimension, tag)
PhysicalTags = Tuple[Dict[int, List[int]], ...]  # indexed by dimension
BoundingEntities = Tuple[Dict[int, npt.NDArray], ...]

# Gmsh format constants
GMSH_MAX_DIM = 4  # Maximum entity dimension (point=0, curve=1, surface=2, volume=3)
GMSH_BBOX_POINT_COORDS = 3  # Bounding box coordinates for point entities
GMSH_BBOX_ENTITY_COORDS = 6  # Bounding box coordinates for entities with dim > 0
GMSH_NODE_TAG_OFFSET = 1  # Gmsh uses 1-based indexing, Python uses 0-based

# Component count constraints (from Gmsh spec)
GMSH_VALID_COMPONENTS = (1, 3, 9)  # Valid number of components per data field


def _size_type(data_size):
    return np.dtype(f"u{data_size}")


class GmshWriter:
    """Helper class to handle binary/ASCII writing modes uniformly."""

    def __init__(self, fh: FileHandle, binary: bool):
        self.fh = fh
        self.binary = binary

    def write_string(self, text: str) -> None:
        """Write string in appropriate format."""
        if self.binary:
            self.fh.write(text.encode() if isinstance(text, str) else text)
        else:
            self.fh.write(text)

    def write_array(self, data, dtype, sep: str = " ", fmt: str = None) -> None:
        """Write numpy array in appropriate format."""
        arr = np.asarray(data, dtype=dtype)
        if self.binary:
            arr.tofile(self.fh)
        else:
            if fmt:
                arr = np.atleast_2d(arr)
                np.savetxt(self.fh, arr, fmt=fmt, delimiter=sep, newline=sep)
            else:
                arr.tofile(self.fh, sep, "%d")

    def write_section_header(self, section_name: str) -> None:
        """Write section header like $Entities."""
        self.write_string(f"${section_name}\n")

    def write_section_footer(self, section_name: str) -> None:
        """Write section footer like $EndEntities."""
        self.write_string(f"$End{section_name}\n")

    def newline(self) -> None:
        """Write a newline."""
        self.write_string("\n" if not self.binary else b"\n")


# ====================================================================
# Readers
# ====================================================================

def read_buffer(f: FileHandle, is_ascii: bool, data_size: int) -> Mesh:
    """Read gmsh 4.1 format mesh from buffer.

    The format is specified at
    <http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format>.

    Args:
        f: File handle to read from
        is_ascii: Whether the file is in ASCII mode
        data_size: Size of size_t type in bytes

    Returns:
        Mesh object containing the mesh data
    """
    # Initialize the optional data fields
    points = []
    cells = None
    field_data = {}
    cell_data_raw = {}
    cell_tags = {}
    point_data = {}
    physical_tags = None
    bounding_entities = None
    cell_sets = {}
    periodic = None

    while True:
        # fast-forward over blank lines
        line, is_eof = _fast_forward_over_blank_lines(f)
        if is_eof:
            break

        if line[0] != "$":
            raise ReadError(f"Unexpected line {repr(line)}")

        environ = line[1:].strip()

        if environ == "PhysicalNames":
            _read_physical_names(f, field_data)
        elif environ == "Entities":
            # Read physical tags and information on bounding entities.
            physical_tags, bounding_entities = _read_entities(f, is_ascii, data_size)
        elif environ == "Nodes":
            points, point_tags, point_entities = _read_nodes(f, is_ascii, data_size)
        elif environ == "Elements":
            cells, cell_tags, cell_sets = _read_elements(
                f,
                point_tags,
                physical_tags,
                bounding_entities,
                is_ascii,
                data_size,
                field_data,
            )
        elif environ == "Periodic":
            periodic = _read_periodic(f, is_ascii, data_size)
        elif environ == "NodeData":
            _read_data(f, "NodeData", point_data, data_size, is_ascii)
        elif environ == "ElementData":
            _read_data(f, "ElementData", cell_data_raw, data_size, is_ascii)
        else:
            # Skip unrecognized sections
            _fast_forward_to_end_block(f, environ)

    if cells is None:
        raise ReadError("$Element section not found.")

    cell_data = cell_data_from_raw(cells, cell_data_raw)
    cell_data.update(cell_tags)

    # Add node entity information to the point data
    point_data.update({"gmsh:dim_tags": point_entities})

    return Mesh(
        points,
        cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        cell_sets=cell_sets,
        gmsh_periodic=periodic,
    )


def _read_entities(f: FileHandle, is_ascii: bool, data_size: int) -> Tuple[PhysicalTags, BoundingEntities]:
    """Read the entity section.

    Args:
        f: File handle to read from
        is_ascii: Whether the file is in ASCII mode
        data_size: Size of size_t type in bytes

    Returns:
        Tuple of (physical_tags, bounding_entities) where:
        - physical_tags: Physical tags indexed by dimension
        - bounding_entities: Bounding entities indexed by dimension
    """
    fromfile = partial(np.fromfile, sep=" " if is_ascii else "")
    c_size_t = _size_type(data_size)
    physical_tags = ({}, {}, {}, {})
    bounding_entities = ({}, {}, {}, {})
    number = fromfile(f, c_size_t, 4)  # dims 0, 1, 2, 3

    for d, n in enumerate(number):
        for _ in range(n):
            (tag,) = fromfile(f, c_int, 1)
            fromfile(f, c_double, 3 if d == 0 else 6)  # discard bounding-box
            (num_physicals,) = fromfile(f, c_size_t, 1)
            physical_tags[d][tag] = list(fromfile(f, c_int, num_physicals))
            if d > 0:
                # Number of bounding entities
                num_BREP_ = fromfile(f, c_size_t, 1)[0]
                # Store bounding entities
                bounding_entities[d][tag] = fromfile(f, c_int, num_BREP_)

    _fast_forward_to_end_block(f, "Entities")
    return physical_tags, bounding_entities


def _read_nodes(f: FileHandle, is_ascii: bool, data_size: int) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    """Read node data: Node coordinates and tags.

    Also find the entities of the nodes, and store this as point_data.
    Note that entity tags are 1-offset within each dimension, thus it is
    necessary to keep track of both tag and dimension of the entity.

    Args:
        f: File handle to read from
        is_ascii: Whether the file is in ASCII mode
        data_size: Size of size_t type in bytes

    Returns:
        Tuple of (points, tags, dim_tags) where:
        - points: Node coordinates (N, 3)
        - tags: Node tags (N,)
        - dim_tags: Entity dimension and tags for each node (N, 2)
    """
    fromfile = partial(np.fromfile, sep=" " if is_ascii else "")
    c_size_t = _size_type(data_size)

    # numEntityBlocks numNodes minNodeTag maxNodeTag (all size_t)
    num_entity_blocks, total_num_nodes, _, _ = fromfile(f, c_size_t, 4)

    points = np.empty((total_num_nodes, 3), dtype=float)
    tags = np.empty(total_num_nodes, dtype=int)
    dim_tags = np.empty((total_num_nodes, 2), dtype=int)

    idx = 0
    for _ in range(num_entity_blocks):
        # entityDim(int) entityTag(int) parametric(int) numNodes(size_t)
        dim, entity_tag, parametric = fromfile(f, c_int, 3)
        if parametric != 0:
            raise ReadError("parametric nodes not implemented")
        num_nodes = int(fromfile(f, c_size_t, 1)[0])

        ixx = slice(idx, idx + num_nodes)
        tags[ixx] = fromfile(f, c_size_t, num_nodes) - 1

        # x(double) y(double) z(double) (* numNodes)
        points[ixx] = fromfile(f, c_double, num_nodes * 3).reshape((num_nodes, 3))

        # Entity tag and entity dimension of the nodes
        dim_tags[ixx, 0] = dim
        dim_tags[ixx, 1] = entity_tag
        idx += num_nodes

    _fast_forward_to_end_block(f, "Nodes")
    return points, tags, dim_tags


def _read_elements(
    f: FileHandle,
    point_tags: npt.NDArray,
    physical_tags: Optional[PhysicalTags],
    bounding_entities: Optional[BoundingEntities],
    is_ascii: bool,
    data_size: int,
    field_data: Dict[str, Tuple[int, int]]
) -> Tuple[List[CellBlock], Dict, Dict]:
    """Read element data from gmsh 4.1 file.

    Args:
        f: File handle to read from
        point_tags: Point tags array
        physical_tags: Physical tags indexed by dimension
        bounding_entities: Bounding entities indexed by dimension
        is_ascii: Whether the file is in ASCII mode
        data_size: Size of size_t type in bytes
        field_data: Field data dictionary

    Returns:
        Tuple of (cells, cell_data, cell_sets)
    """
    fromfile = partial(np.fromfile, sep=" " if is_ascii else "")
    c_size_t = _size_type(data_size)

    # numEntityBlocks numElements minElementTag maxElementTag (all size_t)
    num_entity_blocks, _, _, _ = fromfile(f, c_size_t, 4)

    data = []
    cell_data = {}
    cell_sets = {k: [None] * num_entity_blocks for k in field_data.keys()}

    for k in range(num_entity_blocks):
        # entityDim(int) entityTag(int) elementType(int) numElements(size_t)
        dim, tag, type_ele = fromfile(f, c_int, 3)
        (num_ele,) = fromfile(f, c_size_t, 1)
        for physical_name, cell_set in cell_sets.items():
            cell_set[k] = np.arange(
                num_ele
                if (
                    physical_tags
                    and field_data[physical_name][1] == dim
                    and field_data[physical_name][0] in physical_tags[dim][tag]
                )
                else 0,
                dtype=type(num_ele),
            )
        tpe = _gmsh_to_meshio_type[type_ele]
        num_nodes_per_ele = num_nodes_per_cell[tpe]
        d = fromfile(f, c_size_t, int(num_ele * (1 + num_nodes_per_ele))).reshape(
            (num_ele, -1)
        )

        # Find physical tag, if defined; else it is None.
        pt = None if not physical_tags else physical_tags[dim][tag]
        # Bounding entities (of lower dimension) if defined.
        if dim > 0 and bounding_entities:
            be = bounding_entities[dim][tag]
        else:
            be = None
        data.append((pt, be, tag, tpe, d))

    _fast_forward_to_end_block(f, "Elements")

    # Inverse point tags
    inv_tags = np.full(np.max(point_tags) + 1, -1, dtype=int)
    inv_tags[point_tags] = np.arange(len(point_tags))

    # Note that the first column in the data array is the element tag; discard it.
    # Ensure integer types for node indices
    data = [
        (physical_tag, bound_entity, geom_tag, tpe,
         inv_tags[(d[:, 1:].astype(int) - 1)])
        for physical_tag, bound_entity, geom_tag, tpe, d in data
    ]

    cells = []
    for physical_tag, bound_entity, geom_tag, key, values in data:
        # Ensure the cell data is integer type
        cells.append(CellBlock(key, _gmsh_to_meshio_order(key, values.astype(int))))
        if physical_tag:
            if "gmsh:physical" not in cell_data:
                cell_data["gmsh:physical"] = []
            cell_data["gmsh:physical"].append(
                np.full(len(values), physical_tag[0], int)
            )
        if "gmsh:geometrical" not in cell_data:
            cell_data["gmsh:geometrical"] = []
        cell_data["gmsh:geometrical"].append(np.full(len(values), geom_tag, int))

        # The bounding entities is stored in the cell_sets.
        if bounding_entities:
            if "gmsh:bounding_entities" not in cell_sets:
                cell_sets["gmsh:bounding_entities"] = []
            cell_sets["gmsh:bounding_entities"].append(bound_entity)

    return cells, cell_data, cell_sets


def _read_periodic(f: FileHandle, is_ascii: bool, data_size: int) -> List:
    """Read periodic information from gmsh 4.1 file.

    Args:
        f: File handle to read from
        is_ascii: Whether the file is in ASCII mode
        data_size: Size of size_t type in bytes

    Returns:
        List of periodic boundary information
    """
    fromfile = partial(np.fromfile, sep=" " if is_ascii else "")
    c_size_t = _size_type(data_size)
    periodic = []
    # numPeriodicLinks(size_t)
    num_periodic = int(fromfile(f, c_size_t, 1)[0])
    for _ in range(num_periodic):
        # entityDim(int) entityTag(int) entityTagMaster(int)
        edim, stag, mtag = fromfile(f, c_int, 3)
        # numAffine(size_t) value(double) ...
        num_affine = int(fromfile(f, c_size_t, 1)[0])
        affine = fromfile(f, c_double, num_affine)
        # numCorrespondingNodes(size_t)
        num_nodes = int(fromfile(f, c_size_t, 1)[0])
        # nodeTag(size_t) nodeTagMaster(size_t) ...
        slave_master = fromfile(f, c_size_t, num_nodes * 2).reshape(-1, 2)
        slave_master = slave_master - 1  # Subtract one, Python is 0-based
        periodic.append([edim, (stag, mtag), affine, slave_master])

    _fast_forward_to_end_block(f, "Periodic")
    return periodic


# ====================================================================
# Writers
# ====================================================================

def write_buffer(
    file: FileHandle,
    mesh: Mesh,
    float_fmt: str,
    mesh_only: bool,
    binary: bool,
    **kwargs
) -> None:
    """Write mesh to msh file format.

    Format specification:
    <http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format>

    Args:
        file: File handle to write to
        mesh: Mesh object to write
        float_fmt: Format string for floating point numbers
        mesh_only: If True, skip writing entity information
        binary: Whether to write in binary mode
        **kwargs: Additional keyword arguments (currently unused)
    """
    logger.debug('writing gmsh buffer...')
    logger.debug(locals())

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

    if not mesh_only:
        _write_entities(
            file, mesh.cells, tag_data, mesh.cell_sets, mesh.point_data, binary
        )

    _write_nodes(file, mesh.points, mesh.cells, mesh.point_data, float_fmt, binary)
    _write_elements(file, mesh.cells, tag_data, binary)
    if mesh.gmsh_periodic is not None:
        _write_periodic(file, mesh.gmsh_periodic, float_fmt, binary)

    # if not mesh_only:
    for name, dat in point_data.items():
        _write_data(file, "NodeData", name, dat, binary)
    cell_data_raw = raw_from_cell_data(cell_data)
    for name, dat in cell_data_raw.items():
        _write_data(file, "ElementData", name, dat, binary)

    # Write cell_point_data (element nodal data) to ElementNodeData sections
    if hasattr(mesh, 'cell_point_data') and mesh.cell_point_data:
        _write_cell_point_data(file, mesh, binary)


def _prepare_entity_data(
    cells: List[CellBlock],
    tag_data: Dict,
    point_data: Dict,
    cell_sets: Dict
) -> Tuple[npt.NDArray, npt.NDArray, bool]:
    """Prepare entity-related data structures.

    Args:
        cells: List of cell blocks
        tag_data: Tag data dictionary
        point_data: Point data dictionary
        cell_sets: Cell sets dictionary

    Returns:
        Tuple of (node_dim_tags, cell_dim_tags, has_bounding_entities) where:
        - node_dim_tags: Unique (dim, tag) pairs from point data
        - cell_dim_tags: (dim, tag) pairs for each cell block
        - has_bounding_entities: Whether bounding entity info exists
    """
    # Uniquify node dimension-tags
    node_dim_tags = np.unique(point_data["gmsh:dim_tags"], axis=0)

    # Prepare cell dimension-tags
    cell_dim_tags = np.empty((len(cells), 2), dtype=int)
    for ci, cell_block in enumerate(cells):
        cell_dim_tags[ci] = [
            cell_block.dim,
            tag_data["gmsh:geometrical"][ci][0],
        ]

    has_bounding_entities = "gmsh:bounding_entities" in cell_sets

    return node_dim_tags, cell_dim_tags, has_bounding_entities


def _write_entity_bbox(writer: GmshWriter, dim: int) -> None:
    """Write bounding box coordinates (zeros placeholder).

    Args:
        writer: GmshWriter instance
        dim: Entity dimension (0 for point, >0 for higher-dimensional entities)
    """
    num_coords = GMSH_BBOX_POINT_COORDS if dim == 0 else GMSH_BBOX_ENTITY_COORDS
    writer.write_array(np.zeros(num_coords), c_double)
    if not writer.binary:
        writer.fh.write(" ")


def _write_physical_and_bounding_tags(
    writer: GmshWriter,
    dim: int,
    matching_cell_block: npt.NDArray,
    tag_data: Dict,
    cell_sets: Dict,
    has_bounding_entities: bool
) -> None:
    """Write physical tags and bounding entities for an entity.

    Handles three cases:
    1. Entity with physical tag
    2. Entity without physical tag
    3. Bounding entities (for dim > 0)

    Args:
        writer: GmshWriter instance
        dim: Entity dimension
        matching_cell_block: Matching cell block indices
        tag_data: Tag data dictionary
        cell_sets: Cell sets dictionary
        has_bounding_entities: Whether bounding entity info exists
    """
    # Guard clause: no matching cell block
    if matching_cell_block.size == 0:
        writer.write_array([0], c_size_t)
        if not writer.binary:
            writer.fh.write("0 ")

        if dim > 0:
            writer.write_array([0], c_size_t)
            if not writer.binary:
                writer.fh.write("0\n")
        elif not writer.binary:
            writer.fh.write("\n")
        return

    # Main path: has matching cell block
    # Write physical tag if available
    try:
        physical_tag = tag_data["gmsh:physical"][matching_cell_block[0]][0]
        writer.write_array([1], c_size_t)
        writer.write_array([physical_tag], c_int)
        if not writer.binary:
            writer.fh.write(" ")
    except KeyError:
        writer.write_array([0], c_size_t)
        if not writer.binary:
            writer.fh.write("0 ")

    # Write bounding entities for dim > 0
    if dim > 0:
        if has_bounding_entities:
            bounds = cell_sets["gmsh:bounding_entities"][matching_cell_block[0]]
            num_bounds = len(bounds)

            if num_bounds > 0:
                writer.write_array([num_bounds], c_size_t)
                writer.write_array(bounds, c_int)
                if not writer.binary:
                    writer.fh.write("\n")
            else:
                writer.write_array([0], c_size_t)
                if not writer.binary:
                    writer.fh.write("0\n")
        else:
            writer.write_array([0], c_size_t)
            if not writer.binary:
                writer.fh.write("0\n")
    else:
        # Dimension 0: enforce line change for ASCII
        if not writer.binary:
            writer.fh.write("\n")


def _write_entities(
    fh: FileHandle,
    cells: List[CellBlock],
    tag_data: Dict,
    cell_sets: Dict,
    point_data: Dict,
    binary: bool
) -> None:
    """Write entity section in a .msh file.

    The entity section links three kinds of information:
        1) The geometric objects represented in the mesh
        2) Physical tags of geometric objects
        3) Bounding entities (for objects of dimension >= 1)

    The entities of all geometric objects are pulled from point_data['gmsh:dim_tags'].
    Physical tags are specified as tag_data, while the boundary of a geometric
    object is specified in cell_sets.
    """
    # Early return if no entity data
    if "gmsh:dim_tags" not in point_data:
        return

    writer = GmshWriter(fh, binary)
    writer.write_section_header("Entities")

    # Prepare data structures
    node_dim_tags, cell_dim_tags, has_bounding_entities = _prepare_entity_data(
        cells, tag_data, point_data, cell_sets
    )

    # Write number of entities per dimension
    num_occ = np.bincount(node_dim_tags[:, 0], minlength=GMSH_MAX_DIM)
    if num_occ.size > GMSH_MAX_DIM:
        raise ValueError(f"Encountered entity with dimension > {GMSH_MAX_DIM - 1}")

    writer.write_array(num_occ, c_size_t)
    if not binary:
        fh.write("\n")

    # Write entity data
    for dim, tag in node_dim_tags:
        # Find matching cell block
        matching_cell_block = np.where(
            np.logical_and(cell_dim_tags[:, 0] == dim, cell_dim_tags[:, 1] == tag)
        )[0]

        if matching_cell_block.size > 1:
            raise ValueError("Encountered non-unique CellBlock dim_tag")

        # Write entity tag
        writer.write_array([tag], c_int)
        if not writer.binary:
            writer.fh.write(" ")

        # Write bounding box (placeholder zeros)
        _write_entity_bbox(writer, dim)

        # Write physical tags and bounding entities
        _write_physical_and_bounding_tags(
            writer, dim, matching_cell_block, tag_data, cell_sets, has_bounding_entities
        )

    writer.newline()
    writer.write_section_footer("Entities")


def _prepare_node_dim_tags(
    point_data: Dict,
    cells: List[CellBlock],
    n: int
) -> Tuple[npt.NDArray, npt.NDArray]:
    """Prepare node dimension-tag mappings.

    Args:
        point_data: Point data dictionary
        cells: List of cell blocks
        n: Number of points

    Returns:
        Tuple of (node_dim_tags, reverse_index_map) where:
        - node_dim_tags: Unique (dim, tag) combinations
        - reverse_index_map: Maps each node to its dim_tag index
    """
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
        # If entity information is not provided, assign the same entity for all nodes.
        # This only makes sense if the cells are of a single type
        if len(cells) != 1:
            raise WriteError(
                "Specify entity information (gmsh:dim_tags in point_data) "
                "to deal with more than one cell type."
            )

        dim = cells[0].dim
        tag = GMSH_NODE_TAG_OFFSET
        node_dim_tags = np.array([[dim, tag]])
        # All nodes map to the (single) dimension-entity object
        reverse_index_map = np.full(n, 0, dtype=int)

    return node_dim_tags, reverse_index_map


def _write_node_block(
    writer: GmshWriter,
    dim: int,
    tag: int,
    node_tags: npt.NDArray,
    points: npt.NDArray,
    float_fmt: str
) -> None:
    """Write a single node entity block.

    Args:
        writer: GmshWriter instance
        dim: Entity dimension
        tag: Entity tag
        node_tags: Node indices for this block
        points: All point coordinates
        float_fmt: Format string for floating point numbers
    """
    num_points_this = node_tags.size
    is_parametric = 0

    writer.write_array([dim, tag, is_parametric], c_int)
    writer.write_array([num_points_this], c_size_t)

    if writer.binary:
        (node_tags + GMSH_NODE_TAG_OFFSET).astype(c_size_t).tofile(writer.fh)
        points[node_tags].tofile(writer.fh)
    else:
        (node_tags + GMSH_NODE_TAG_OFFSET).astype(c_size_t).tofile(writer.fh, "\n", "%d")
        writer.fh.write("\n")
        np.savetxt(writer.fh, points[node_tags], delimiter=" ", fmt="%" + float_fmt)


def _write_nodes(
    fh: FileHandle,
    points: npt.NDArray,
    cells: List[CellBlock],
    point_data: Dict,
    float_fmt: str,
    binary: bool
) -> None:
    """Write node information.

    If data on dimension and tags of the geometric entities which the nodes belong to
    is available, the nodes will be grouped accordingly. This data is specified as
    point_data, using the key 'gmsh:dim_tags' and data as a num_points x 2 numpy
    array (first column is the dimension of the geometric entity of this node,
    second is the tag).

    If dim_tags are not available, all nodes will be assigned the same tag. This only
    makes sense if a single cell block is present in the mesh; an error will be raised
    if len(cells) > 1.
    """
    # Ensure 3D points (msh4 requires 3D points)
    if points.shape[1] == 2:
        points = np.column_stack([points, np.zeros_like(points[:, 0])])

    writer = GmshWriter(fh, binary)
    writer.write_section_header("Nodes")

    n = points.shape[0]
    min_tag = GMSH_NODE_TAG_OFFSET
    max_tag = n

    # Prepare dimension-tag mappings
    node_dim_tags, reverse_index_map = _prepare_node_dim_tags(point_data, cells, n)
    num_blocks = node_dim_tags.shape[0]

    # Validate and prepare points for binary mode
    if binary and points.dtype != c_double:
        warn(f"Binary Gmsh needs c_double points (got {points.dtype}). Converting.")
        points = points.astype(c_double)

    # Write preamble
    writer.write_array([num_blocks, n, min_tag, max_tag], c_size_t)
    if not binary:
        fh.write("\n")

    # Write node blocks
    for j in range(num_blocks):
        dim, tag = node_dim_tags[j]
        node_tags = np.where(reverse_index_map == j)[0]
        _write_node_block(writer, dim, tag, node_tags, points, float_fmt)

    writer.newline()
    writer.write_section_footer("Nodes")


def _write_element_block(
    writer: GmshWriter,
    cell_block: CellBlock,
    tag_data: Dict,
    block_index: int,
    tag0: int
) -> int:
    """Write a single element entity block.

    Args:
        writer: GmshWriter instance
        cell_block: CellBlock to write
        tag_data: Tag data dictionary
        block_index: Index of this cell block
        tag0: Starting element tag

    Returns:
        Updated tag counter for next block
    """
    node_idcs = _meshio_to_gmsh_order(cell_block.type, cell_block.data)

    # Get entity tag
    if "gmsh:geometrical" in tag_data:
        entity_tag = tag_data["gmsh:geometrical"][block_index][0]
    else:
        # Note: Binary uses 0, ASCII uses 1 as default (preserving original behavior)
        entity_tag = 0 if writer.binary else 1

    cell_type = _meshio_to_gmsh_type[cell_block.type]
    n = len(cell_block.data)

    # Write block header
    writer.write_array([cell_block.dim, entity_tag, cell_type], c_int)
    writer.write_array([n], c_size_t)

    # Write element data
    if writer.binary:
        if node_idcs.dtype != c_size_t:
            warn(f"Binary Gmsh cells need c_size_t (got {node_idcs.dtype}). Converting.")
            node_idcs = node_idcs.astype(c_size_t)

        np.column_stack([
            np.arange(tag0, tag0 + n, dtype=c_size_t),
            node_idcs + GMSH_NODE_TAG_OFFSET,
        ]).tofile(writer.fh)
    else:
        np.savetxt(
            writer.fh,
            np.column_stack([
                np.arange(tag0, tag0 + n),
                node_idcs + GMSH_NODE_TAG_OFFSET
            ]),
            "%d",
            " ",
        )

    return tag0 + n


def _write_elements(fh: FileHandle, cells: List[CellBlock], tag_data: Dict, binary: bool) -> None:
    """Write the $Elements block.

    $Elements
      numEntityBlocks(size_t)
      numElements(size_t) minElementTag(size_t) maxElementTag(size_t)
      entityDim(int) entityTag(int) elementType(int) numElementsInBlock(size_t)
        elementTag(size_t) nodeTag(size_t) ...
        ...
      ...
    $EndElements
    """
    writer = GmshWriter(fh, binary)
    writer.write_section_header("Elements")

    total_num_cells = sum(len(c) for c in cells)
    num_blocks = len(cells)
    min_element_tag = GMSH_NODE_TAG_OFFSET
    max_element_tag = total_num_cells

    writer.write_array(
        [num_blocks, total_num_cells, min_element_tag, max_element_tag],
        c_size_t
    )
    if not binary:
        fh.write("\n")

    tag0 = GMSH_NODE_TAG_OFFSET
    for ci, cell_block in enumerate(cells):
        tag0 = _write_element_block(writer, cell_block, tag_data, ci, tag0)

    writer.newline()
    writer.write_section_footer("Elements")


def _write_periodic(fh: FileHandle, periodic, float_fmt: str, binary: bool) -> None:
    """Write the $Periodic block.

    Specified as:

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
    writer = GmshWriter(fh, binary)

    writer.write_section_header("Periodic")
    writer.write_array(len(periodic), c_size_t)

    for dim, (stag, mtag), affine, slave_master in periodic:
        writer.write_array([dim, stag, mtag], c_int)

        if affine is None or len(affine) == 0:
            writer.write_array(0, c_size_t)
        else:
            writer.write_array(len(affine), c_size_t, sep=" ")
            writer.write_array(affine, c_double, fmt=float_fmt)

        slave_master = np.array(slave_master, dtype=c_size_t)
        slave_master = slave_master.reshape(-1, 2)
        slave_master = slave_master + GMSH_NODE_TAG_OFFSET  # Gmsh is 1-based
        writer.write_array(len(slave_master), c_size_t)
        writer.write_array(slave_master, c_size_t)

    writer.newline()
    writer.write_section_footer("Periodic")


def _determine_component_count(cell_blocks_data: List[npt.NDArray]) -> Optional[int]:
    """Determine number of components from cell_point_data shape.

    Args:
        cell_blocks_data: List of cell block data arrays

    Returns:
        Number of components, or None if shape is invalid
    """
    first_block_data = cell_blocks_data[0]

    if len(first_block_data.shape) == 2:
        # Shape: (n_elements, n_nodes_per_element) - single component
        return 1
    elif len(first_block_data.shape) == 3:
        # Shape: (n_elements, n_nodes_per_element, n_components)
        return first_block_data.shape[2]
    else:
        return None


def _write_element_node_data_header(
    writer: GmshWriter,
    field_name: str,
    num_components: int,
    total_elements: int
) -> None:
    """Write ElementNodeData section header.

    Args:
        writer: GmshWriter instance
        field_name: Name of the data field
        num_components: Number of components per node
        total_elements: Total number of elements
    """
    writer.write_section_header("ElementNodeData")

    # String tags
    writer.write_string(f"{1}\n")
    writer.write_string(f'"{field_name}"\n')

    # Real tags
    writer.write_string(f"{1}\n")
    writer.write_string(f"{0.0}\n")

    # Integer tags: time step, num components, num elements
    writer.write_string(f"{3}\n")
    writer.write_string(f"{0}\n")  # time step
    writer.write_string(f"{num_components}\n")
    writer.write_string(f"{total_elements}\n")


def _write_element_node_values(
    writer: GmshWriter,
    elem_id: int,
    elem_data: npt.NDArray,
    num_components: int
) -> None:
    """Write nodal data for a single element.

    Args:
        writer: GmshWriter instance
        elem_id: Element ID
        elem_data: Nodal data for this element
        num_components: Number of components per node
    """
    if num_components == 1:
        # Single component: elem_data is 1D array
        num_nodes = len(elem_data)
        writer.write_array([elem_id, num_nodes], c_int)

        if writer.binary:
            elem_data.astype(c_double).tofile(writer.fh)
        else:
            for val in elem_data:
                writer.fh.write(f" {float(val)}")
            writer.fh.write("\n")
    else:
        # Multi-component: elem_data is 2D array (n_nodes, n_components)
        num_nodes = elem_data.shape[0]
        writer.write_array([elem_id, num_nodes], c_int)

        if writer.binary:
            # Flatten the data: all components for node 1, then node 2, etc.
            elem_data.astype(c_double).flatten().tofile(writer.fh)
        else:
            for node_vals in elem_data:
                for val in node_vals:
                    writer.fh.write(f" {float(val)}")
            writer.fh.write("\n")


def _write_cell_point_data(fh: FileHandle, mesh, binary: bool) -> None:
    """Write cell_point_data (element nodal data) to $ElementNodeData sections.

    The cell_point_data structure is:
        {name: [array_for_cell_block_0, array_for_cell_block_1, ...]}
    where each array has shape (n_elements, n_nodes_per_element) for single
    component or (n_elements, n_nodes_per_element, n_components) for multi-
    component data.

    Args:
        fh: File handle to write to
        mesh: Mesh object containing cell_point_data
        binary: Whether to write in binary mode
    """
    # Validate element_id exists
    if 'element_id' not in mesh.cell_data:
        logger.warning("Cannot write cell_point_data: mesh.cell_data['element_id'] not found")
        return

    element_ids = mesh.cell_data['element_id']
    writer = GmshWriter(fh, binary)

    # Process each field
    for field_name, cell_blocks_data in mesh.cell_point_data.items():
        # Determine component count
        num_components = _determine_component_count(cell_blocks_data)
        if num_components is None:
            logger.warning(
                f"Unexpected shape for cell_point_data '{field_name}': "
                f"{cell_blocks_data[0].shape}"
            )
            continue

        total_elements = sum(len(block_data) for block_data in cell_blocks_data)

        # Write header
        _write_element_node_data_header(writer, field_name, num_components, total_elements)

        # Write data for each element
        for block_idx, block_data in enumerate(cell_blocks_data):
            block_element_ids = element_ids[block_idx]

            for elem_idx, elem_data in enumerate(block_data):
                elem_id = int(block_element_ids[elem_idx])
                _write_element_node_values(writer, elem_id, elem_data, num_components)

        # Write footer
        writer.newline()
        writer.write_section_footer("ElementNodeData")
