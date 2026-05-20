"""Mesh data structures for Structure Genome I/O.

Provides the ``SGMesh`` class (a ``meshio.Mesh`` extension that adds
``cell_point_data`` for element-nodal fields) plus a few mesh-level helpers
(isolated-node detection, cell-ordering checks).

``SGMesh`` itself stores only geometry and standard meshio-style data.
The optional ``point_data['node_id']`` / ``cell_data['element_id']`` fields
that enable round-trip preservation of original node/element IDs are
operated on by :mod:`sgio.core.numbering` (validation, mapping,
renumbering, format-specific requirements).

See also
--------
sgio.core.numbering : Dual numbering validation / renumbering utilities.
dev-notes/architecture/io.md : Background on the dual numbering contract.
"""
from meshio import Mesh, CellBlock
from typing import Dict, Tuple, Union
import numpy as np


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

class SGMesh(Mesh):
    """Extended mesh class that inherits from meshio.Mesh.

    This class provides additional functionality and custom format support
    while maintaining compatibility with the original meshio.Mesh class.

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

        super().__init__(
            points, cells,
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data,
            point_sets=point_sets,
            cell_sets=cell_sets,
            gmsh_periodic=gmsh_periodic,
            info=info,
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


