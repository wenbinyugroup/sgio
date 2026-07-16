"""Mesh data structures for Structure Genome I/O.

Provides the ``SGMesh`` class (a backend-neutral mesh container that adds
``cell_point_data`` for element-nodal fields) plus a few mesh-level helpers
(isolated-node detection, cell-ordering checks).

``SGMesh`` stores only geometry and standard mesh data (points, cell blocks,
point/cell data). It has **no** ``meshio`` dependency: the core IR can be
used without ``meshio`` installed. Interop with ``meshio`` is provided by the
:meth:`SGMesh.from_meshio` / :meth:`SGMesh.to_meshio` bridge methods, which
import ``meshio`` lazily only when called.

The optional ``point_data['node_id']`` / ``cell_data['element_id']`` fields
that enable round-trip preservation of original node/element IDs are
operated on by :mod:`sgio.core.numbering` (validation, mapping,
renumbering, format-specific requirements).

See also
--------
sgio.core.numbering : Dual numbering validation / renumbering utilities.
dev-notes/architecture/io.md : Background on the dual numbering contract.
"""
from __future__ import annotations

import copy
from typing import Dict, Tuple, Union

import numpy as np


# Topological dimension per cell type. Copied from meshio's canonical table so
# the core IR can build ``CellBlock`` / ``SGMesh`` without importing meshio.
topological_dimension = {
    "line": 1, "polygon": 2, "triangle": 2, "quad": 2, "tetra": 3,
    "hexahedron": 3, "wedge": 3, "pyramid": 3, "line3": 1, "triangle6": 2,
    "quad9": 2, "tetra10": 3, "hexahedron27": 3, "wedge18": 3, "pyramid14": 3,
    "vertex": 0, "quad8": 2, "hexahedron20": 3, "triangle10": 2,
    "triangle15": 2, "triangle21": 2, "line4": 1, "line5": 1, "line6": 1,
    "tetra20": 3, "tetra35": 3, "tetra56": 3, "quad16": 2, "quad25": 2,
    "quad36": 2, "triangle28": 2, "triangle36": 2, "triangle45": 2,
    "triangle55": 2, "triangle66": 2, "quad49": 2, "quad64": 2, "quad81": 2,
    "quad100": 2, "quad121": 2, "line7": 1, "line8": 1, "line9": 1,
    "line10": 1, "line11": 1, "tetra84": 3, "tetra120": 3, "tetra165": 3,
    "tetra220": 3, "tetra286": 3, "wedge40": 3, "wedge75": 3, "hexahedron64": 3,
    "hexahedron125": 3, "hexahedron216": 3, "hexahedron343": 3,
    "hexahedron512": 3, "hexahedron729": 3, "hexahedron1000": 3, "wedge126": 3,
    "wedge196": 3, "wedge288": 3, "wedge405": 3, "wedge550": 3,
    "VTK_LAGRANGE_CURVE": 1, "VTK_LAGRANGE_TRIANGLE": 2,
    "VTK_LAGRANGE_QUADRILATERAL": 2, "VTK_LAGRANGE_TETRAHEDRON": 3,
    "VTK_LAGRANGE_HEXAHEDRON": 3, "VTK_LAGRANGE_WEDGE": 3,
    "VTK_LAGRANGE_PYRAMID": 3,
}


class CellBlock:
    """A block of cells of a single type.

    Backend-neutral counterpart of ``meshio.CellBlock``; carries the same
    ``type`` / ``data`` / ``dim`` / ``tags`` attributes so adapters and the
    meshio bridge can treat the two interchangeably.

    Parameters
    ----------
    cell_type : str
        Cell type identifier (e.g. ``'triangle'``, ``'tetra10'``).
    data : list or numpy.ndarray
        Connectivity array of shape ``(n_cells, n_nodes_per_cell)``.
    tags : list of str, optional
        Optional tags carried through from the source format.
    """

    def __init__(self, cell_type: str, data, tags: list | None = None):
        self.type = cell_type
        self.data = data

        if cell_type.startswith("polyhedron"):
            self.dim = 3
        else:
            self.data = np.asarray(self.data)
            self.dim = topological_dimension[cell_type]

        self.tags = [] if tags is None else tags

    def __repr__(self):
        items = [
            "sgio CellBlock",
            f"type: {self.type}",
            f"num cells: {len(self.data)}",
            f"tags: {self.tags}",
        ]
        return "<" + ", ".join(items) + ">"

    def __len__(self):
        return len(self.data)


def _is_element_node_data(dict_data: dict) -> bool:
    """Check if dict represents element-node data (nested) or element data (flat)."""
    first_eid = next(iter(dict_data))
    first_data = dict_data[first_eid]
    return (
        isinstance(first_data, list)
        and len(first_data) > 0
        and isinstance(first_data[0], list)
    )


def _build_single_component_cell_data(dict_data, cell_data_eid):
    """Group {eid: value} into cell-block-major list, single component."""
    out = []
    for typei_ids in cell_data_eid:
        typei_data = [dict_data[eid] for eid in typei_ids]
        out.append(typei_data)
    return out


def _build_multi_component_cell_data(names, dict_data, cell_data_eid):
    """Group {eid: [c0, c1, ...]} into per-component cell-block-major lists."""
    ncomps = len(names)
    by_comp = [[] for _ in range(ncomps)]
    for typei_ids in cell_data_eid:
        typei_by_comp = [[] for _ in range(ncomps)]
        for eid in typei_ids:
            data_all = dict_data[eid]
            for k, data in enumerate(data_all):
                typei_by_comp[k].append(data)
        for k in range(ncomps):
            by_comp[k].append(typei_by_comp[k])
    return {name: by_comp[i] for i, name in enumerate(names)}


def _build_single_component_cell_point_data(dict_data, cell_data_eid):
    """Group {eid: [v_node0, v_node1, ...]} into cell-block-major arrays."""
    out = []
    for typei_ids in cell_data_eid:
        typei_data = [dict_data[eid] for eid in typei_ids]
        out.append(np.array(typei_data))
    return out


def _build_multi_component_cell_point_data(names, dict_data, cell_data_eid):
    """Group {eid: [[c0,c1,...]_node0, ...]} into per-component arrays."""
    result = {}
    for comp_idx, comp_name in enumerate(names):
        per_block = []
        for typei_ids in cell_data_eid:
            typei_data = []
            for eid in typei_ids:
                elem_node_data = dict_data[eid]
                comp_values = [node_data[comp_idx] for node_data in elem_node_data]
                typei_data.append(comp_values)
            per_block.append(np.array(typei_data))
        result[comp_name] = per_block
    return result

class SGMesh:
    """Backend-neutral mesh container for Structure Genome I/O.

    Stores geometry (points, cell blocks) and standard mesh data, plus
    ``cell_point_data`` for element-nodal fields. Attribute layout mirrors
    ``meshio.Mesh`` so adapters can access ``points`` / ``cells`` /
    ``point_data`` / ``cell_data`` / ``field_data`` / ``point_sets`` /
    ``cell_sets`` / ``gmsh_periodic`` / ``info`` uniformly. Interop with
    ``meshio`` goes through :meth:`from_meshio` / :meth:`to_meshio`.

    Attributes
    ----------
    cell_point_data : dict[str, list[np.ndarray]]
        Dictionary of element nodal data (data at nodes of each element).
        Structure: {name: [array_for_cell_block_0, array_for_cell_block_1, ...]}
        where each array has shape (n_elements, n_nodes_per_element, n_components).
        This is used for storing element_node data like strain/stress at element nodes.
    """

    def __init__(
        self,
        points, cells,
        point_data=None,
        cell_data=None,
        field_data=None,
        point_sets=None,
        cell_sets=None,
        gmsh_periodic=None,
        info=None,
        cell_point_data=None,
        ):

        self.points = np.asarray(points)

        # Normalize cells to a list of CellBlock (accept dict or (type, data)
        # tuples for backward compatibility with the meshio.Mesh signature).
        if isinstance(cells, dict):
            cells = list(cells.items())

        self.cells = []
        for cell_block in cells:
            if isinstance(cell_block, tuple):
                cell_type, data = cell_block
                cell_block = CellBlock(
                    cell_type,
                    data if cell_type.startswith("polyhedron") else np.asarray(data),
                )
            self.cells.append(cell_block)

        self.point_data = {} if point_data is None else point_data
        self.cell_data = {} if cell_data is None else cell_data
        self.field_data = {} if field_data is None else field_data
        self.point_sets = {} if point_sets is None else point_sets
        self.cell_sets = {} if cell_sets is None else cell_sets
        self.gmsh_periodic = gmsh_periodic
        self.info = info

        # Assert point-data consistency and convert to numpy arrays.
        for key, item in self.point_data.items():
            self.point_data[key] = np.asarray(item)
            if len(self.point_data[key]) != len(self.points):
                raise ValueError(
                    f"len(points) = {len(self.points)}, "
                    f'but len(point_data["{key}"]) = {len(self.point_data[key])}'
                )

        # Assert cell-data consistency and convert to numpy arrays.
        for key, data in self.cell_data.items():
            if len(data) != len(self.cells):
                raise ValueError(
                    f"Incompatible cell data '{key}'. "
                    f"{len(self.cells)} cell blocks, but '{key}' has {len(data)} blocks."
                )
            for k in range(len(data)):
                data[k] = np.asarray(data[k])
                if len(data[k]) != len(self.cells[k]):
                    raise ValueError(
                        "Incompatible cell data. "
                        + f"Cell block {k} ('{self.cells[k].type}') "
                        + f"has length {len(self.cells[k])}, but "
                        + f"corresponding cell data item has length {len(data[k])}."
                    )

        # Initialize cell_point_data (element nodal data)
        self.cell_point_data = {} if cell_point_data is None else cell_point_data

        # Validate cell_point_data consistency
        for key, data in self.cell_point_data.items():
            if len(data) != len(self.cells):
                raise ValueError(
                    f"Incompatible cell_point_data '{key}'. "
                    f"{len(self.cells)} cell blocks, but '{key}' has {len(data)} blocks."
                )

            for k in range(len(data)):
                data[k] = np.asarray(data[k])
                if len(data[k]) != len(self.cells[k]):
                    raise ValueError(
                        "Incompatible cell_point_data. "
                        + f"Cell block {k} ('{self.cells[k].type}') "
                        + f"has {len(self.cells[k])} elements, but "
                        + f"corresponding cell_point_data item has {len(data[k])} elements."
                    )


    def __repr__(self):
        lines = ["<sgio SGMesh object>", f"  Number of points: {len(self.points)}"]
        if len(self.cells) > 0:
            lines.append("  Number of cells:")
            for cell_block in self.cells:
                lines.append(f"    {cell_block.type}: {len(cell_block)}")
        else:
            lines.append("  No cells.")
        for label, container in (
            ("Point data", self.point_data),
            ("Cell data", self.cell_data),
            ("Field data", self.field_data),
            ("Cell point data", self.cell_point_data),
        ):
            if container:
                lines.append(f"  {label}: {', '.join(container.keys())}")
        return "\n".join(lines)

    def copy(self) -> "SGMesh":
        """Return a deep copy of this mesh."""
        return copy.deepcopy(self)

    @classmethod
    def from_meshio(cls, mesh) -> "SGMesh":
        """Build an :class:`SGMesh` from a ``meshio.Mesh``.

        Copies geometry and all standard data containers, converting each
        meshio cell block into an sgio :class:`CellBlock`. ``meshio`` need not
        be importable here; only the passed object's attributes are read.

        Parameters
        ----------
        mesh : meshio.Mesh
            Source mesh.

        Returns
        -------
        SGMesh
            New mesh with copied data.
        """
        cells = [
            CellBlock(cb.type, np.asarray(cb.data), list(getattr(cb, "tags", []) or []))
            for cb in mesh.cells
        ]
        return cls(
            points=np.asarray(mesh.points),
            cells=cells,
            point_data={k: np.asarray(v) for k, v in dict(mesh.point_data).items()},
            cell_data={k: list(v) for k, v in dict(mesh.cell_data).items()},
            field_data=dict(getattr(mesh, "field_data", {}) or {}),
            point_sets=dict(getattr(mesh, "point_sets", {}) or {}),
            cell_sets=dict(getattr(mesh, "cell_sets", {}) or {}),
            gmsh_periodic=getattr(mesh, "gmsh_periodic", None),
            info=getattr(mesh, "info", None),
        )

    def to_meshio(self):
        """Export this mesh to a ``meshio.Mesh``.

        Imports ``meshio`` lazily. Element-nodal ``cell_point_data`` has no
        meshio counterpart and is dropped; all other containers are passed
        through. Used at the I/O boundary when handing a mesh to a meshio
        writer for a format sgio does not own.

        Returns
        -------
        meshio.Mesh
            Equivalent meshio mesh.
        """
        import meshio

        cells = [
            meshio.CellBlock(cb.type, cb.data, list(getattr(cb, "tags", []) or []))
            for cb in self.cells
        ]
        return meshio.Mesh(
            self.points,
            cells,
            point_data=dict(self.point_data),
            cell_data={k: list(v) for k, v in self.cell_data.items()},
            field_data=dict(self.field_data),
            point_sets=dict(self.point_sets),
            cell_sets=dict(self.cell_sets),
            gmsh_periodic=self.gmsh_periodic,
            info=self.info,
        )

    def get_cell_block_by_type(self, cell_type):
        """
        """
        for _cb in self.cells:
            if _cb.type == cell_type:
                return _cb
        return None

    def add_point_data_from_dict(
        self,
        name: Union[str, list],
        dict_data: Dict[int, list],
    ) -> None:
        """Attach per-node data (given as ``{node_id: value}``) to ``point_data``.

        Parameters
        ----------
        name : str or list of str
            Field name(s). A list activates the multi-component path where
            ``dict_data[nid]`` must be a list of ``len(name)`` components.
        dict_data : dict[int, list or float]
            Mapping from 1-based node ID to value(s). Node IDs are converted
            to 0-based positions internally (``nid - 1``).

        Examples
        --------
        >>> mesh.add_point_data_from_dict('temperature', {1: 1.5, 2: 2.5})
        >>> mesh.add_point_data_from_dict(['u', 'v'], {1: [1.0, 2.0], 2: [3.0, 4.0]})
        """
        npoints = len(self.points)

        if isinstance(name, str):
            data = [dict_data[i + 1] for i in range(npoints)]
            self.point_data[name] = np.array(data)
            return

        ncomps = len(name)
        per_comp = [[] for _ in range(ncomps)]
        for i in range(npoints):
            values = dict_data[i + 1]
            for j in range(ncomps):
                per_comp[j].append(values[j])
        for j, field_name in enumerate(name):
            self.point_data[field_name] = np.array(per_comp[j])

    def add_cell_data_from_dict(
        self,
        name: Union[str, list],
        dict_data: Dict[int, list],
    ) -> None:
        """Attach per-element data (given as ``{element_id: value}``) to the mesh.

        Routes to ``cell_data`` for flat-list values, or ``cell_point_data``
        for nested-list values (element-node data). Detection is automatic
        based on ``dict_data`` shape.

        Requires ``self.cell_data['element_id']`` to be populated.

        Parameters
        ----------
        name : str or list of str
            Field name(s). A list activates the multi-component path.
        dict_data : dict[int, list]
            Element data:

            * Element-level (flat): ``{eid: [c0, c1, ...]}`` → ``cell_data``
            * Element-node (nested): ``{eid: [[c0,...]_node0, ...]}``
              → ``cell_point_data``

        Examples
        --------
        >>> mesh.add_cell_data_from_dict('material_id', {1: [100.0], 2: [200.0]})
        >>> mesh.add_cell_data_from_dict(
        ...     ['stress_x', 'stress_y'],
        ...     {1: [[1.0, 2.0], [3.0, 4.0]], 2: [[5.0, 6.0], [7.0, 8.0]]},
        ... )
        """
        cell_data_eid = self.cell_data['element_id']

        if _is_element_node_data(dict_data):
            if isinstance(name, str):
                self.cell_point_data[name] = _build_single_component_cell_point_data(
                    dict_data, cell_data_eid
                )
            elif isinstance(name, list):
                result = _build_multi_component_cell_point_data(
                    name, dict_data, cell_data_eid
                )
                for field_name, data in result.items():
                    self.cell_point_data[field_name] = data
            return

        if isinstance(name, str):
            self.cell_data[name] = _build_single_component_cell_data(
                dict_data, cell_data_eid
            )
        elif isinstance(name, list):
            result = _build_multi_component_cell_data(
                name, dict_data, cell_data_eid
            )
            for field_name, data in result.items():
                self.cell_data[field_name] = data


def get_cell_data_arrays(mesh: SGMesh, key: str, default_value: int) -> list[np.ndarray]:
    """Return one integer cell-data array per cell block."""
    if key in mesh.cell_data:
        return [np.asarray(array, dtype=np.int32).copy() for array in mesh.cell_data[key]]

    return [
        np.full(len(cell_block.data), default_value, dtype=np.int32)
        for cell_block in mesh.cells
    ]


def merge_field_data(
    merged_field_data: dict[str, np.ndarray],
    field_data: dict[str, np.ndarray],
) -> None:
    """Merge field-data dictionaries, keeping the first value per name."""
    for name, value in field_data.items():
        if name not in merged_field_data:
            merged_field_data[name] = np.asarray(value).copy()




def check_isolated_nodes(mesh: SGMesh):
    """
    Check if there are isolated/unconnected nodes in the mesh.

    Go through all cells and check if every node is used at least once.

    Create a list of cell ids for each node:

    ..  code-block::

        node_cell_ids = [
            [
                (cell_block_id, cell_id_in_block),
                ...
            ],
            ...
        ]
    """
    # print(f'len(mesh.points): {len(mesh.points)}')
    nodes_in_cells = []
    node_cell_ids = [[] for _ in mesh.points]
    # print(f'len(node_cell_ids): {len(node_cell_ids)}')
    for _cb_id, _cb in enumerate(mesh.cells):
        for _ci, _nis in enumerate(_cb.data):
            for _ni in _nis:
                node_cell_ids[_ni].append((_cb_id, _ci))
                nodes_in_cells.append(_ni)

    nodes_in_cells = list(set(nodes_in_cells))
    nodes_in_cells.sort()

    # Check if any node is not in any cell
    isolated_nodes = [i for i, _ncids in enumerate(node_cell_ids) if not _ncids]
    if isolated_nodes:
        raise ValueError(f"Isolated nodes found: {isolated_nodes}")

    return node_cell_ids, nodes_in_cells


def _check_tetra4_ordering(points: np.ndarray, cells: np.ndarray) -> np.ndarray:
    """Return indices of tetra4 cells with invalid ordering."""
    points = np.asarray(points)
    cells = np.asarray(cells)
    if cells.size == 0:
        return np.array([], dtype=int)
    if cells.ndim != 2 or cells.shape[1] != 4:
        raise ValueError(
            f"Expected tetra4 cells with shape (n, 4), got {cells.shape}"
        )
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(
            f"Expected point coordinates with shape (n, 3), got {points.shape}"
        )

    cell_points = points[cells]
    p0 = cell_points[:, 0, :]
    p1 = cell_points[:, 1, :]
    p2 = cell_points[:, 2, :]
    p3 = cell_points[:, 3, :]
    normal = np.cross(p1 - p0, p2 - p0)
    dot = np.einsum("ij,ij->i", normal, p3 - p0)
    return np.where(dot <= 0.0)[0]


def _check_cell_ordering_placeholder(
    points: np.ndarray,
    cells: np.ndarray,
    cell_type: str,
) -> np.ndarray:
    """Placeholder for future cell ordering checks."""
    _ = points
    _ = cells
    _ = cell_type
    return np.array([], dtype=int)


def check_cell_ordering(mesh: SGMesh) -> Dict[Tuple[int, str], np.ndarray]:
    """Check node ordering for supported cell types.

    Parameters
    ----------
    mesh : SGMesh
        Mesh containing cell blocks to validate.

    Returns
    -------
    dict[tuple[int, str], np.ndarray]
        Mapping of (cell_block_id, cell_type) to arrays of invalid cell indices.

    Raises
    ------
    ValueError
        If any invalid cell ordering is detected.
    """
    invalid_cells = {}
    placeholder_cell_types = {
        "line",
        "triangle",
        "quad",
        "tetra10",
        "hexahedron",
        "wedge",
        "pyramid",
    }

    for cb_id, cell_block in enumerate(mesh.cells):
        cell_type = cell_block.type
        if cell_type == "tetra":
            invalid = _check_tetra4_ordering(mesh.points, cell_block.data)
        elif cell_type in placeholder_cell_types:
            invalid = _check_cell_ordering_placeholder(
                mesh.points,
                cell_block.data,
                cell_type,
            )
        else:
            continue

        if invalid.size > 0:
            invalid_cells[(cb_id, cell_type)] = invalid

    if invalid_cells:
        details = ", ".join(
            f"block {cb_id} '{cell_type}': {len(indices)} invalid"
            for (cb_id, cell_type), indices in invalid_cells.items()
        )
        raise ValueError(f"Invalid cell ordering found: {details}")

    return invalid_cells


def get_invalid_cell_ordering_element_ids(
    mesh: SGMesh
) -> Dict[Tuple[int, str], np.ndarray]:
    """Return invalid element IDs for supported cell types.

    Parameters
    ----------
    mesh : SGMesh
        Mesh containing cell blocks to validate.

    Returns
    -------
    dict[tuple[int, str], np.ndarray]
        Mapping of (cell_block_id, cell_type) to arrays of invalid element IDs.
    """
    invalid_element_ids = {}
    placeholder_cell_types = {
        "line",
        "triangle",
        "quad",
        "tetra10",
        "hexahedron",
        "wedge",
        "pyramid",
    }
    element_offset = 0

    for cb_id, cell_block in enumerate(mesh.cells):
        cell_type = cell_block.type
        count = len(cell_block.data)
        if "element_id" in mesh.cell_data and cb_id < len(mesh.cell_data["element_id"]):
            element_ids = np.asarray(mesh.cell_data["element_id"][cb_id], dtype=int)
            if element_ids.shape[0] != count:
                raise ValueError(
                    "Incompatible element_id cell_data for block "
                    f"{cb_id} ('{cell_type}'): expected {count}, got {element_ids.shape[0]}"
                )
        else:
            element_ids = np.arange(
                element_offset + 1,
                element_offset + 1 + count,
                dtype=int,
            )

        if cell_type == "tetra":
            invalid = _check_tetra4_ordering(mesh.points, cell_block.data)
        elif cell_type in placeholder_cell_types:
            invalid = _check_cell_ordering_placeholder(
                mesh.points,
                cell_block.data,
                cell_type,
            )
        else:
            invalid = np.array([], dtype=int)

        if invalid.size > 0:
            invalid_element_ids[(cb_id, cell_type)] = element_ids[invalid]

        element_offset += count

    return invalid_element_ids


def fix_cell_ordering(mesh: SGMesh) -> Dict[Tuple[int, str], np.ndarray]:
    """Fix node ordering for supported cell types.

    Parameters
    ----------
    mesh : SGMesh
        Mesh containing cell blocks to validate and fix.

    Returns
    -------
    dict[tuple[int, str], np.ndarray]
        Mapping of (cell_block_id, cell_type) to arrays of fixed cell indices.
    """
    fixed_cells = {}
    placeholder_cell_types = {
        "line",
        "triangle",
        "quad",
        "tetra10",
        "hexahedron",
        "wedge",
        "pyramid",
    }

    for cb_id, cell_block in enumerate(mesh.cells):
        cell_type = cell_block.type
        if cell_type == "tetra":
            invalid = _check_tetra4_ordering(mesh.points, cell_block.data)
            if invalid.size > 0:
                data = cell_block.data
                temp = data[invalid, 0].copy()
                data[invalid, 0] = data[invalid, 1]
                data[invalid, 1] = temp
                fixed_cells[(cb_id, cell_type)] = invalid
        elif cell_type in placeholder_cell_types:
            continue
        else:
            continue

    return fixed_cells


