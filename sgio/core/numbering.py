"""Node and element numbering validation and utilities.

This module provides functions for validating and managing node and element
numbering in mesh data structures. It supports format-specific validation
for VABS, SwiftComp, Abaqus, and generic mesh formats.
"""
from __future__ import annotations

import logging
from typing import Optional, Union, Literal, Dict, List, Tuple, Set
import warnings
import numpy as np
from numpy.typing import ArrayLike

from .format_requirements import FormatNumberingRequirements, get_numbering_requirements


_module_logger = logging.getLogger(__name__)


def _handle_deprecated_parameter(
    old_name: str,
    new_name: str,
    old_value: Optional[bool],
    new_value: Optional[bool],
    default_value: bool = False
) -> bool:
    """Handle deprecated parameter with backward compatibility.
    
    This helper function manages the transition from old parameter names to new ones,
    issuing deprecation warnings when old names are used while maintaining backward
    compatibility.
    
    Parameters
    ----------
    old_name : str
        Name of the deprecated parameter (e.g., 'renumber_nodes').
    new_name : str
        Name of the new parameter (e.g., 'use_sequential_node_ids').
    old_value : bool or None
        Value passed to the deprecated parameter.
    new_value : bool or None
        Value passed to the new parameter.
    default_value : bool, default False
        Default value to use if neither parameter is specified.
        
    Returns
    -------
    bool
        The resolved parameter value.
        
    Raises
    ------
    ValueError
        If both old and new parameters are specified with conflicting values.
        
    Warns
    -----
    DeprecationWarning
        If the old parameter name is used.
        
    Examples
    --------
    >>> # In a function signature
    >>> def write_mesh(renumber_nodes=None, use_sequential_node_ids=None):
    ...     renumber = _handle_deprecated_parameter(
    ...         'renumber_nodes', 'use_sequential_node_ids',
    ...         renumber_nodes, use_sequential_node_ids, default_value=False
    ...     )
    """
    # Both None - use default
    if old_value is None and new_value is None:
        return default_value
    
    # Only new parameter specified - use it directly
    if old_value is None and new_value is not None:
        return new_value
    
    # Only old parameter specified - issue deprecation warning
    if old_value is not None and new_value is None:
        warnings.warn(
            f"Parameter '{old_name}' is deprecated and will be removed in a future version. "
            f"Use '{new_name}' instead.",
            DeprecationWarning,
            stacklevel=3
        )
        return old_value
    
    # Both specified - check for conflicts
    if old_value != new_value:
        raise ValueError(
            f"Conflicting values for '{old_name}' ({old_value}) and '{new_name}' ({new_value}). "
            f"Please use only '{new_name}' as '{old_name}' is deprecated."
        )
    
    # Both specified with same value - issue warning but accept
    warnings.warn(
        f"Parameter '{old_name}' is deprecated and will be removed in a future version. "
        f"Use only '{new_name}' instead.",
        DeprecationWarning,
        stacklevel=3
    )
    return new_value


def validate_node_ids(
    node_ids: Union[List[int], ArrayLike],
    n_nodes: Optional[int] = None,
    format: Literal['generic', 'vabs', 'swiftcomp', 'abaqus'] = 'generic'
) -> None:
    """Validate node ID numbering according to format requirements.
    
    Validates that node IDs meet the requirements for the specified format:
    - generic: No specific requirements (always passes)
    - vabs/swiftcomp: Must be consecutive integers from 1 to n_nodes, no duplicates
    - abaqus: Must be positive integers (>= 1), no duplicates, ID=0 forbidden
    
    Parameters
    ----------
    node_ids : list of int or array-like
        List or array of node IDs to validate.
    n_nodes : int, optional
        Expected number of nodes. If None, uses len(node_ids).
    format : {'generic', 'vabs', 'swiftcomp', 'abaqus'}, default 'generic'
        Format to validate against:
        - 'generic': No validation (always passes)
        - 'vabs': Requires consecutive integers from 1
        - 'swiftcomp': Requires consecutive integers from 1
        - 'abaqus': Requires positive integers, no ID=0
        
    Raises
    ------
    ValueError
        If node IDs do not meet format requirements (duplicates, forbidden IDs, 
        or non-consecutive numbering).
        
    Examples
    --------
    >>> # Valid consecutive numbering for VABS
    >>> validate_node_ids([1, 2, 3, 4, 5], format='vabs')
    
    >>> # Invalid - missing node 3
    >>> validate_node_ids([1, 2, 4, 5], format='vabs')
    ValueError: Node IDs must be consecutive integers from 1 to 4
    
    >>> # Invalid - duplicate IDs
    >>> validate_node_ids([1, 2, 2, 3], format='vabs')
    ValueError: Duplicate Node IDs found: [2]
    
    >>> # Invalid - forbidden ID=0 for Abaqus
    >>> validate_node_ids([0, 1, 2, 3], format='abaqus')
    ValueError: Forbidden Node IDs found: [0]
    
    >>> # Generic format always passes
    >>> validate_node_ids([10, 20, 30], format='generic')
    """
    # Convert to list if needed
    if isinstance(node_ids, np.ndarray):
        node_ids_list = node_ids.astype(int).tolist()
    else:
        node_ids_list = list(node_ids) if node_ids else []
    
    # Determine expected count
    if n_nodes is None:
        n_nodes = len(node_ids_list)
    
    # Format-specific validation
    if format == 'generic':
        # No specific requirements for generic format
        return
    
    # Check for duplicates (all formats except generic)
    duplicates = check_duplicate_ids(node_ids_list, 'Node')
    if duplicates:
        msg = f"Duplicate Node IDs found: {duplicates[:10]}"
        if len(duplicates) > 10:
            msg += f" ... and {len(duplicates) - 10} more"
        raise ValueError(msg)
    
    # Check for forbidden IDs
    forbidden = check_forbidden_ids(node_ids_list, format=format, id_type='Node')
    if forbidden:
        msg = f"Forbidden Node IDs found: {forbidden[:10]}"
        if len(forbidden) > 10:
            msg += f" ... and {len(forbidden) - 10} more"
        if format == 'abaqus':
            msg += "\nAbaqus requires node IDs to be positive integers (>= 1)"
        else:
            msg += f"\n{format.upper()} requires node IDs to be positive integers (>= 1)"
        raise ValueError(msg)
    
    if format in ('vabs', 'swiftcomp'):
        # VABS and SwiftComp require consecutive numbering from 1
        _validate_consecutive_from_one(node_ids_list, n_nodes, 'Node')
    
    elif format == 'abaqus':
        # Abaqus just requires positive IDs (checked above), no consecutive requirement
        pass
    
    else:
        raise ValueError(f"Unknown format: {format}")


def validate_element_ids(
    element_ids: Union[List[List[int]], List[ArrayLike]],
    format: Literal['generic', 'vabs', 'swiftcomp', 'abaqus'] = 'generic'
) -> None:
    """Validate element ID numbering according to format requirements.
    
    Validates that element IDs meet the requirements for the specified format:
    - generic: No specific requirements (always passes)
    - vabs/swiftcomp: Must be consecutive integers from 1 across all cell blocks, no duplicates
    - abaqus: Must be positive integers (>= 1), no duplicates, ID=0 forbidden
    
    Parameters
    ----------
    element_ids : list of lists or list of arrays
        Element IDs organized by cell block. Each item is a list/array of
        element IDs for that cell type.
    format : {'generic', 'vabs', 'swiftcomp', 'abaqus'}, default 'generic'
        Format to validate against:
        - 'generic': No validation (always passes)
        - 'vabs': Requires consecutive integers from 1
        - 'swiftcomp': Requires consecutive integers from 1
        - 'abaqus': Requires positive integers, no ID=0
        
    Raises
    ------
    ValueError
        If element IDs do not meet format requirements (duplicates, forbidden IDs,
        or non-consecutive numbering).
        
    Examples
    --------
    >>> # Valid consecutive numbering across blocks
    >>> element_ids = [[1, 2, 3], [4, 5, 6]]
    >>> validate_element_ids(element_ids, format='vabs')
    
    >>> # Invalid - missing element 4
    >>> element_ids = [[1, 2, 3], [5, 6, 7]]
    >>> validate_element_ids(element_ids, format='vabs')
    ValueError: Element IDs must be consecutive integers from 1 to 7
    
    >>> # Invalid - duplicate IDs
    >>> element_ids = [[1, 2, 3], [3, 4, 5]]
    >>> validate_element_ids(element_ids, format='vabs')
    ValueError: Duplicate Element IDs found: [3]
    
    >>> # Invalid - forbidden ID=0 for Abaqus
    >>> element_ids = [[0, 1, 2], [3, 4, 5]]
    >>> validate_element_ids(element_ids, format='abaqus')
    ValueError: Forbidden Element IDs found: [0]
    """
    if format == 'generic':
        # No specific requirements for generic format
        return
    
    # Flatten all element IDs
    all_elem_ids = []
    for block_ids in element_ids:
        if isinstance(block_ids, np.ndarray):
            all_elem_ids.extend(block_ids.astype(int).tolist())
        else:
            all_elem_ids.extend(block_ids)
    
    # Check for duplicates (all formats except generic)
    duplicates = check_duplicate_ids(all_elem_ids, 'Element')
    if duplicates:
        msg = f"Duplicate Element IDs found: {duplicates[:10]}"
        if len(duplicates) > 10:
            msg += f" ... and {len(duplicates) - 10} more"
        raise ValueError(msg)
    
    # Check for forbidden IDs
    forbidden = check_forbidden_ids(all_elem_ids, format=format, id_type='Element')
    if forbidden:
        msg = f"Forbidden Element IDs found: {forbidden[:10]}"
        if len(forbidden) > 10:
            msg += f" ... and {len(forbidden) - 10} more"
        if format == 'abaqus':
            msg += "\nAbaqus requires element IDs to be positive integers (>= 1)"
        else:
            msg += f"\n{format.upper()} requires element IDs to be positive integers (>= 1)"
        raise ValueError(msg)
    
    if format in ('vabs', 'swiftcomp'):
        # VABS and SwiftComp require consecutive numbering from 1
        n_elements = len(all_elem_ids)
        _validate_consecutive_from_one(all_elem_ids, n_elements, 'Element')
    
    elif format == 'abaqus':
        # Abaqus just requires positive IDs (checked above), no consecutive requirement
        pass
    
    else:
        raise ValueError(f"Unknown format: {format}")


def get_node_id_mapping(mesh) -> Dict[int, int]:
    """Extract node ID mapping from mesh.
    
    Returns a dictionary mapping from original node IDs (from mesh.point_data['node_id'])
    to array indices (0-based positions in mesh.points).
    
    Parameters
    ----------
    mesh : SGMesh
        Mesh object with optional point_data['node_id'].
        
    Returns
    -------
    dict[int, int]
        Mapping from original node ID to array index.
        If mesh has no 'node_id', returns identity mapping {1: 0, 2: 1, 3: 2, ...}.
        
    Examples
    --------
    >>> mesh = SGMesh(points, cells, point_data={'node_id': [10, 20, 30]})
    >>> get_node_id_mapping(mesh)
    {10: 0, 20: 1, 30: 2}
    
    >>> # Mesh without node_id
    >>> mesh = SGMesh(points, cells)
    >>> get_node_id_mapping(mesh)
    {1: 0, 2: 1, 3: 2}
    """
    n_nodes = len(mesh.points)
    
    if 'node_id' in mesh.point_data:
        node_ids = mesh.point_data['node_id']
        if isinstance(node_ids, np.ndarray):
            node_ids = node_ids.astype(int).tolist()
        else:
            node_ids = list(node_ids)
        
        # Create mapping from node ID to array index
        return {node_id: idx for idx, node_id in enumerate(node_ids)}
    else:
        # No node_id, use 1-based sequential numbering
        return {i + 1: i for i in range(n_nodes)}


def ensure_node_ids(mesh) -> None:
    """Ensure mesh has node IDs in point_data.

    If mesh.point_data does not contain ``'node_id'`` (or it is empty),
    generates sequential node IDs starting from 1.

    This is a Phase 4 utility intended to make node IDs always present so
    format-specific writers/readers can rely on them.

    Parameters
    ----------
    mesh : SGMesh
        Mesh object to ensure has node IDs.

    Raises
    ------
    ValueError
        If ``mesh.point_data['node_id']`` exists but its length does not match
        the number of points.
    """
    # Ensure point_data exists
    if not hasattr(mesh, "point_data") or mesh.point_data is None:
        mesh.point_data = {}

    n_nodes = len(mesh.points)
    node_ids = mesh.point_data.get("node_id", None)

    if node_ids is None or len(node_ids) == 0:
        mesh.point_data["node_id"] = np.arange(1, n_nodes + 1, dtype=int)
        return

    node_ids_arr = np.asarray(node_ids, dtype=int).reshape(-1)
    if node_ids_arr.shape[0] != n_nodes:
        raise ValueError(
            "Incompatible node_id point_data: expected "
            f"{n_nodes}, got {node_ids_arr.shape[0]}"
        )

    # Normalize storage type
    mesh.point_data["node_id"] = node_ids_arr


def auto_renumber_for_format(
    mesh,
    format: str,
    logger: Optional[logging.Logger] = None,
) -> tuple[bool, bool]:
    """Automatically renumber nodes/elements to meet format requirements.

    Uses the Phase 4.1 numbering requirements registry to check whether the
    current ``point_data['node_id']`` and ``cell_data['element_id']`` satisfy
    the target format. If not, renumbers them sequentially to comply.

    Parameters
    ----------
    mesh : SGMesh
        Mesh to validate and potentially renumber (modified in-place).
    format : str
        Target format string (e.g., 'vabs', 'swiftcomp', 'abaqus', 'gmsh').
    logger : logging.Logger, optional
        Logger used to emit warnings. If None, uses this module's logger.
        A :class:`UserWarning` is also emitted for easy capture in tests.

    Returns
    -------
    tuple[bool, bool]
        ``(nodes_renumbered, elements_renumbered)``
    """
    requirements = get_numbering_requirements(format)
    if requirements is None:
        # Unknown format: nothing to enforce.
        return False, False

    # Make sure IDs exist before checking requirements.
    ensure_node_ids(mesh)
    ensure_element_ids(mesh)

    nodes_renumbered = False
    elements_renumbered = False

    # Nodes
    node_ids = mesh.point_data.get("node_id", [])
    if not _meets_requirements(node_ids, requirements, "nodes"):
        _renumber_nodes_sequential(mesh, requirements)
        nodes_renumbered = True
        _emit_numbering_warning(
            logger,
            f"Node IDs renumbered to meet {requirements.name} format requirements "
            f"(consecutive from {requirements.nodes_start_from})",
        )

    # Elements
    element_ids = mesh.cell_data.get("element_id", []) if hasattr(mesh, "cell_data") else []
    if not _meets_requirements(element_ids, requirements, "elements"):
        _renumber_elements_sequential(mesh, requirements)
        elements_renumbered = True
        _emit_numbering_warning(
            logger,
            f"Element IDs renumbered to meet {requirements.name} format requirements "
            f"(consecutive from {requirements.elements_start_from})",
        )

    return nodes_renumbered, elements_renumbered


def ensure_element_ids(mesh) -> None:
    """Ensure mesh has element IDs in cell_data.
    
    If mesh.cell_data does not contain 'element_id', generates sequential
    element IDs starting from 1 for all cell blocks.
    
    Modifies mesh.cell_data['element_id'] in-place.
    
    Parameters
    ----------
    mesh : SGMesh
        Mesh object to ensure has element IDs.
        
    Examples
    --------
    >>> mesh = SGMesh(points, cells)
    >>> ensure_element_ids(mesh)
    >>> assert 'element_id' in mesh.cell_data
    >>> print(mesh.cell_data['element_id'])
    [[1, 2, 3], [4, 5, 6, 7]]
    """
    if 'element_id' not in mesh.cell_data:
        mesh.cell_data['element_id'] = []
    
    elem_ids = mesh.cell_data['element_id']
    
    # Check if we need to generate element IDs
    if len(elem_ids) == 0:
        # Generate sequential IDs for all blocks
        current_id = 1
        for cell_block in mesh.cells:
            n_elements = len(cell_block.data)
            block_ids = list(range(current_id, current_id + n_elements))
            elem_ids.append(block_ids)
            current_id += n_elements
    else:
        # Fill in missing blocks
        current_max_id = 0
        
        # Find the maximum existing ID
        for block_ids in elem_ids:
            if len(block_ids) > 0:
                block_max = max(block_ids) if isinstance(block_ids, list) else int(np.max(block_ids))
                current_max_id = max(current_max_id, block_max)
        
        # Generate IDs for missing blocks
        while len(elem_ids) < len(mesh.cells):
            block_idx = len(elem_ids)
            n_elements = len(mesh.cells[block_idx].data)
            block_ids = list(range(current_max_id + 1, current_max_id + 1 + n_elements))
            elem_ids.append(block_ids)
            current_max_id += n_elements


def _emit_numbering_warning(log: Optional[logging.Logger], message: str) -> None:
    """Emit a numbering warning.

    If a logger is provided, logs via ``logger.warning``; also emits a
    :class:`UserWarning` so tests and callers can capture it via
    ``pytest.warns``.
    """
    active_logger = log if log is not None else _module_logger
    active_logger.warning(message)
    warnings.warn(message, UserWarning, stacklevel=3)


def _meets_requirements(
    ids: Union[list, np.ndarray],
    requirements: FormatNumberingRequirements,
    id_type: str,  # 'nodes' or 'elements'
) -> bool:
    """Return True if IDs meet the given format numbering requirements."""
    if ids is None:
        return True

    if id_type == "nodes":
        ids_array = np.asarray(ids, dtype=int).reshape(-1)
        if ids_array.size == 0:
            return True

        # Basic validity
        if np.any(ids_array < 0):
            return False
        if not requirements.allows_zero_id and np.any(ids_array == 0):
            return False
        if np.any(ids_array < requirements.nodes_start_from):
            return False
        if np.unique(ids_array).size != ids_array.size:
            return False

        # Consecutive requirement
        if requirements.nodes_consecutive:
            start = requirements.nodes_start_from
            expected = np.arange(start, start + ids_array.size, dtype=int)
            return np.array_equal(np.sort(ids_array), expected)

        return True

    if id_type == "elements":
        all_ids = _flatten_element_ids(ids)
        if all_ids.size == 0:
            return True

        if np.any(all_ids < 0):
            return False
        if not requirements.allows_zero_id and np.any(all_ids == 0):
            return False
        if np.any(all_ids < requirements.elements_start_from):
            return False
        if np.unique(all_ids).size != all_ids.size:
            return False

        if requirements.elements_consecutive:
            start = requirements.elements_start_from
            expected = np.arange(start, start + all_ids.size, dtype=int)
            return np.array_equal(np.sort(all_ids), expected)

        return True

    raise ValueError(f"Unknown id_type: {id_type!r}")


def _flatten_element_ids(ids: Union[list, np.ndarray]) -> np.ndarray:
    """Flatten element IDs across cell blocks into a 1D int array."""
    if ids is None:
        return np.array([], dtype=int)

    # Some callers may pass a flat ndarray already.
    if isinstance(ids, np.ndarray):
        return np.asarray(ids, dtype=int).reshape(-1)

    parts: list[np.ndarray] = []
    for block in ids:
        if block is None:
            continue
        arr = np.asarray(block, dtype=int).reshape(-1)
        if arr.size:
            parts.append(arr)

    if not parts:
        return np.array([], dtype=int)
    return np.concatenate(parts)


def _renumber_nodes_sequential(mesh, requirements: FormatNumberingRequirements) -> None:
    """Renumber nodes sequentially according to format requirements."""
    n_nodes = len(mesh.points)
    start = requirements.nodes_start_from
    mesh.point_data["node_id"] = np.arange(start, start + n_nodes, dtype=int)


def _renumber_elements_sequential(mesh, requirements: FormatNumberingRequirements) -> None:
    """Renumber elements sequentially according to format requirements."""
    ensure_element_ids(mesh)

    start = requirements.elements_start_from
    eid = start
    for cb_id, cell_block in enumerate(mesh.cells):
        count = len(cell_block.data)
        element_ids = np.arange(eid, eid + count, dtype=int)
        mesh.cell_data["element_id"][cb_id] = element_ids
        eid += count


def check_duplicate_ids(ids: Union[List[int], ArrayLike], id_type: str = 'ID') -> List[int]:
    """Check for duplicate IDs in a list.
    
    Parameters
    ----------
    ids : list of int or array-like
        List or array of IDs to check for duplicates.
    id_type : str, default 'ID'
        Type of ID being checked (e.g., 'Node', 'Element') for error messages.
        
    Returns
    -------
    list of int
        List of duplicate IDs found (empty if no duplicates).
        
    Examples
    --------
    >>> check_duplicate_ids([1, 2, 3, 2, 4])
    [2]
    
    >>> check_duplicate_ids([1, 2, 3, 4, 5])
    []
    """
    # Convert to list if needed
    if isinstance(ids, np.ndarray):
        ids_list = ids.astype(int).tolist()
    else:
        ids_list = list(ids) if ids else []
    
    # Find duplicates
    seen: Set[int] = set()
    duplicates: Set[int] = set()
    
    for id_val in ids_list:
        if id_val in seen:
            duplicates.add(id_val)
        else:
            seen.add(id_val)
    
    return sorted(list(duplicates))


def check_forbidden_ids(
    ids: Union[List[int], ArrayLike],
    format: Literal['generic', 'vabs', 'swiftcomp', 'abaqus'] = 'generic',
    id_type: str = 'ID'
) -> List[int]:
    """Check for forbidden IDs according to format requirements.
    
    Different formats have different restrictions on allowed ID values:
    - generic: No restrictions
    - vabs/swiftcomp: IDs must be positive (>= 1)
    - abaqus: IDs must be positive (>= 1), ID=0 is forbidden
    
    Parameters
    ----------
    ids : list of int or array-like
        List or array of IDs to check.
    format : {'generic', 'vabs', 'swiftcomp', 'abaqus'}, default 'generic'
        Format to check against.
    id_type : str, default 'ID'
        Type of ID being checked (e.g., 'Node', 'Element') for error messages.
        
    Returns
    -------
    list of int
        List of forbidden IDs found (empty if none found).
        
    Examples
    --------
    >>> check_forbidden_ids([0, 1, 2, 3], format='abaqus')
    [0]
    
    >>> check_forbidden_ids([-1, 0, 1, 2], format='vabs')
    [-1, 0]
    
    >>> check_forbidden_ids([0, -5, 1, 2], format='generic')
    []
    """
    # Convert to list if needed
    if isinstance(ids, np.ndarray):
        ids_list = ids.astype(int).tolist()
    else:
        ids_list = list(ids) if ids else []
    
    forbidden: Set[int] = set()
    
    if format == 'generic':
        # No restrictions for generic format
        return []
    
    elif format in ('vabs', 'swiftcomp', 'abaqus'):
        # These formats require positive IDs (>= 1)
        for id_val in ids_list:
            if id_val <= 0:
                forbidden.add(id_val)
    
    else:
        raise ValueError(f"Unknown format: {format}")
    
    return sorted(list(forbidden))


def _validate_consecutive_from_one(ids: List[int], n_expected: int, id_type: str) -> None:
    """Validate that IDs are consecutive integers from 1 to n_expected.
    
    Helper function used by validate_node_ids and validate_element_ids.
    
    Parameters
    ----------
    ids : list of int
        List of IDs to validate.
    n_expected : int
        Expected number of IDs.
    id_type : str
        Type of ID being validated (e.g., 'Node', 'Element') for error messages.
        
    Raises
    ------
    ValueError
        If IDs are not consecutive integers from 1 to n_expected.
    """
    if len(ids) == 0:
        return  # No validation needed if empty
    
    expected = set(range(1, n_expected + 1))
    actual = set(ids)
    
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        
        msg = f"{id_type} IDs must be consecutive integers from 1 to {n_expected}"
        if missing:
            msg += f"\nMissing IDs: {missing[:10]}"  # Show first 10
            if len(missing) > 10:
                msg += f" ... and {len(missing) - 10} more"
        if extra:
            msg += f"\nUnexpected IDs: {extra[:10]}"  # Show first 10
            if len(extra) > 10:
                msg += f" ... and {len(extra) - 10} more"
        msg += "\nConsider setting renumber_nodes=True or renumber_elements=True to automatically renumber."
        
        raise ValueError(msg)
