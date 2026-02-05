from meshio import Mesh, CellBlock
from typing import Dict, Tuple, Union
import numpy as np

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

    #     # Additional SG-specific attributes
    #     self.material_properties = {}
    #     self.element_materials = {}  # Mapping of element IDs to material IDs
    #     self.local_reference_systems = {}  # Local reference coordinate systems for materials
    #     self.analysis_config = {}  # Other configurations for analysis
        
    # def add_material_property(self, material_id, property_name, value):
    #     """Add a material property.
        
    #     Args:
    #         material_id: Identifier for the material
    #         property_name: Name of the property
    #         value: Value of the property
    #     """
    #     if material_id not in self.material_properties:
    #         self.material_properties[material_id] = {}
    #     self.material_properties[material_id][property_name] = value
        
    # def assign_material_to_element(self, element_id, material_id):
    #     """Assign a material to an element.
        
    #     Args:
    #         element_id: Identifier for the element
    #         material_id: Identifier for the material
    #     """
    #     self.element_materials[element_id] = material_id
        
    # def set_local_reference_system(self, element_id, reference_system):
    #     """Set the local reference coordinate system for an element.
        
    #     Args:
    #         element_id: Identifier for the element
    #         reference_system: The reference coordinate system (e.g., a 3x3 matrix)
    #     """
    #     self.local_reference_systems[element_id] = reference_system
        
    # def set_analysis_config(self, config_name, config_value):
    #     """Set analysis configuration.
        
    #     Args:
    #         config_name: Name of the configuration
    #         config_value: Value of the configuration
    #     """
    #     self.analysis_config[config_name] = config_value




def check_isolated_nodes(mesh: Union[SGMesh, Mesh]):
    """
    Check if there are isolated/unconnected nodes in the mesh.

    Go through all cells and check if every node is used at least once.

    Create a list of cell ids for each node:
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


def check_cell_ordering(mesh: Union[SGMesh, Mesh]) -> Dict[Tuple[int, str], np.ndarray]:
    """Check node ordering for supported cell types.

    Parameters
    ----------
    mesh : SGMesh or meshio.Mesh
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
    mesh: Union[SGMesh, Mesh]
) -> Dict[Tuple[int, str], np.ndarray]:
    """Return invalid element IDs for supported cell types.

    Parameters
    ----------
    mesh : SGMesh or meshio.Mesh
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


def fix_cell_ordering(mesh: Union[SGMesh, Mesh]) -> Dict[Tuple[int, str], np.ndarray]:
    """Fix node ordering for supported cell types.

    Parameters
    ----------
    mesh : SGMesh or meshio.Mesh
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


# def renumber_nodes(mesh: Union[SGMesh, Mesh]):
#     """
#     """


def renumber_elements(mesh: Union[SGMesh, Mesh]):
    """
    """
    eid = 0
    for cb_id, _cb in enumerate(mesh.cell_data['element_id']):
        count = np.asarray(_cb).shape[0]
        element_ids = np.arange(eid + 1, eid + 1 + count, dtype=int)
        mesh.cell_data['element_id'][cb_id] = element_ids
        eid += count
