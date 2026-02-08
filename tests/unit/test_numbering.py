"""Test numbering validation and utilities.

This module tests functions for validating and managing node/element numbering.
"""
import pytest
import numpy as np
import warnings

from sgio.core.mesh import SGMesh
from sgio.core.numbering import (
    validate_node_ids,
    validate_element_ids,
    get_node_id_mapping,
    ensure_node_ids,
    ensure_element_ids,
    auto_renumber_for_format,
    check_duplicate_ids,
    check_forbidden_ids,
)


# ============================================================================
# Test validate_node_ids
# ============================================================================

@pytest.mark.unit
def test_validate_node_ids_generic_format():
    """Test that generic format accepts any numbering."""
    # Any numbering should be valid for generic format
    validate_node_ids([10, 20, 30], format='generic')
    validate_node_ids([1, 3, 5], format='generic')
    validate_node_ids([], format='generic')


@pytest.mark.unit
def test_validate_node_ids_vabs_valid():
    """Test VABS format with valid consecutive numbering."""
    validate_node_ids([1, 2, 3, 4, 5], format='vabs')
    validate_node_ids(np.array([1, 2, 3]), format='vabs')


@pytest.mark.unit
def test_validate_node_ids_swiftcomp_valid():
    """Test SwiftComp format with valid consecutive numbering."""
    validate_node_ids([1, 2, 3, 4, 5], format='swiftcomp')
    validate_node_ids(np.array([1, 2, 3]), format='swiftcomp')


@pytest.mark.unit
def test_validate_node_ids_vabs_missing():
    """Test VABS format with missing node IDs."""
    with pytest.raises(ValueError, match="Node IDs must be consecutive integers from 1 to 4"):
        validate_node_ids([1, 2, 4, 5], format='vabs')
    
    with pytest.raises(ValueError, match="Missing IDs: \\[3\\]"):
        validate_node_ids([1, 2, 4, 5], format='vabs')


@pytest.mark.unit
def test_validate_node_ids_swiftcomp_extra():
    """Test SwiftComp format with unexpected node IDs."""
    with pytest.raises(ValueError, match="Node IDs must be consecutive integers from 1 to 4"):
        validate_node_ids([1, 2, 3, 5], format='swiftcomp')
    
    with pytest.raises(ValueError, match="Unexpected IDs: \\[5\\]"):
        validate_node_ids([1, 2, 3, 5], format='swiftcomp')


@pytest.mark.unit
def test_validate_node_ids_starts_from_zero():
    """Test validation fails when node IDs start from 0."""
    # Now catches forbidden ID first
    with pytest.raises(ValueError, match="Forbidden Node IDs found: \\[0\\]"):
        validate_node_ids([0, 1, 2], format='vabs')


@pytest.mark.unit
def test_validate_node_ids_with_n_nodes():
    """Test validation with explicit n_nodes parameter."""
    # Valid when n_nodes matches
    validate_node_ids([1, 2, 3], n_nodes=3, format='vabs')
    
    # Invalid when n_nodes doesn't match
    with pytest.raises(ValueError, match="Node IDs must be consecutive integers from 1 to 5"):
        validate_node_ids([1, 2, 3], n_nodes=5, format='vabs')


@pytest.mark.unit
def test_validate_node_ids_empty():
    """Test validation with empty list."""
    # Empty list should pass for all formats
    validate_node_ids([], format='generic')
    validate_node_ids([], format='vabs')
    validate_node_ids([], format='swiftcomp')


@pytest.mark.unit
def test_validate_node_ids_unknown_format():
    """Test validation with unknown format."""
    with pytest.raises(ValueError, match="Unknown format: invalid"):
        validate_node_ids([1, 2, 3], format='invalid')


# ============================================================================
# Test validate_element_ids
# ============================================================================

@pytest.mark.unit
def test_validate_element_ids_generic_format():
    """Test that generic format accepts any numbering."""
    validate_element_ids([[10, 20], [30, 40]], format='generic')
    validate_element_ids([[1, 3], [5, 7]], format='generic')
    validate_element_ids([], format='generic')


@pytest.mark.unit
def test_validate_element_ids_vabs_valid():
    """Test VABS format with valid consecutive numbering."""
    # Consecutive across blocks
    validate_element_ids([[1, 2, 3], [4, 5, 6]], format='vabs')
    validate_element_ids([np.array([1, 2]), np.array([3, 4])], format='vabs')


@pytest.mark.unit
def test_validate_element_ids_swiftcomp_valid():
    """Test SwiftComp format with valid consecutive numbering."""
    validate_element_ids([[1, 2, 3], [4, 5, 6]], format='swiftcomp')


@pytest.mark.unit
def test_validate_element_ids_vabs_missing():
    """Test VABS format with missing element IDs."""
    with pytest.raises(ValueError, match="Element IDs must be consecutive integers from 1 to 6"):
        validate_element_ids([[1, 2, 3], [5, 6, 7]], format='vabs')
    
    with pytest.raises(ValueError, match="Missing IDs: \\[4\\]"):
        validate_element_ids([[1, 2, 3], [5, 6, 7]], format='vabs')


@pytest.mark.unit
def test_validate_element_ids_swiftcomp_extra():
    """Test SwiftComp format with unexpected element IDs."""
    with pytest.raises(ValueError, match="Element IDs must be consecutive integers from 1 to 7"):
        validate_element_ids([[1, 2, 3], [4, 5, 6, 10]], format='swiftcomp')


@pytest.mark.unit
def test_validate_element_ids_unordered_blocks():
    """Test validation with element IDs not in order across blocks."""
    # IDs don't need to be ordered, just consecutive when collected
    validate_element_ids([[4, 5, 6], [1, 2, 3]], format='vabs')


@pytest.mark.unit
def test_validate_element_ids_empty():
    """Test validation with empty list."""
    validate_element_ids([], format='generic')
    validate_element_ids([], format='vabs')
    validate_element_ids([], format='swiftcomp')


@pytest.mark.unit
def test_validate_element_ids_unknown_format():
    """Test validation with unknown format."""
    with pytest.raises(ValueError, match="Unknown format: invalid"):
        validate_element_ids([[1, 2, 3]], format='invalid')


# ============================================================================
# Test get_node_id_mapping
# ============================================================================

@pytest.mark.unit
def test_get_node_id_mapping_with_node_ids():
    """Test mapping extraction when mesh has node_id."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([10, 20, 30])}
    
    mesh = SGMesh(points, cells, point_data=point_data)
    mapping = get_node_id_mapping(mesh)
    
    assert mapping == {10: 0, 20: 1, 30: 2}


@pytest.mark.unit
def test_get_node_id_mapping_without_node_ids():
    """Test mapping when mesh has no node_id (uses default 1-based)."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    
    mesh = SGMesh(points, cells)
    mapping = get_node_id_mapping(mesh)
    
    assert mapping == {1: 0, 2: 1, 3: 2}


@pytest.mark.unit
def test_get_node_id_mapping_with_list():
    """Test mapping extraction with node_id as list."""
    points = np.array([[0, 0, 0], [1, 0, 0]], dtype=float)
    cells = [('line', np.array([[0, 1]]))]
    point_data = {'node_id': [100, 200]}
    
    mesh = SGMesh(points, cells, point_data=point_data)
    mapping = get_node_id_mapping(mesh)
    
    assert mapping == {100: 0, 200: 1}


# ============================================================================
# Test ensure_node_ids
# ============================================================================


@pytest.mark.unit
def test_ensure_node_ids_creates_ids_when_missing():
    """Test ensure_node_ids creates sequential IDs when missing."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    mesh = SGMesh(points, cells)

    assert 'node_id' not in mesh.point_data

    ensure_node_ids(mesh)

    assert 'node_id' in mesh.point_data
    assert np.array_equal(mesh.point_data['node_id'], np.array([1, 2, 3]))


@pytest.mark.unit
def test_ensure_node_ids_preserves_existing_values():
    """Test ensure_node_ids does not modify existing IDs (except normalization)."""
    points = np.array([[0, 0, 0], [1, 0, 0]], dtype=float)
    cells = [('line', np.array([[0, 1]]))]
    mesh = SGMesh(points, cells, point_data={'node_id': [10, 20]})

    ensure_node_ids(mesh)

    assert mesh.point_data['node_id'].tolist() == [10, 20]


@pytest.mark.unit
def test_ensure_node_ids_length_mismatch_raises():
    """Test ensure_node_ids raises if node_id length doesn't match points."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]

    # meshio validates point_data length on construction, so create a valid mesh
    # first and then corrupt the node_id length.
    mesh = SGMesh(points, cells, point_data={'node_id': [1, 2, 3]})
    mesh.point_data['node_id'] = [1, 2]

    with pytest.raises(ValueError, match="Incompatible node_id point_data"):
        ensure_node_ids(mesh)


# ============================================================================
# Test auto_renumber_for_format
# ============================================================================


@pytest.mark.unit
def test_auto_renumber_for_format_vabs_renumbers_nonconsecutive_ids():
    """Test auto_renumber_for_format renumbers to VABS requirements."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    mesh = SGMesh(
        points,
        cells,
        point_data={'node_id': [10, 50, 100]},
        cell_data={'element_id': [[100]]},
    )

    with pytest.warns(UserWarning) as rec:
        nodes_ren, elems_ren = auto_renumber_for_format(mesh, 'vabs')

    assert (nodes_ren, elems_ren) == (True, True)
    assert mesh.point_data['node_id'].tolist() == [1, 2, 3]
    assert np.asarray(mesh.cell_data['element_id'][0], dtype=int).tolist() == [1]

    messages = [str(w.message) for w in rec]
    assert any('Node IDs renumbered' in m for m in messages)
    assert any('Element IDs renumbered' in m for m in messages)


@pytest.mark.unit
def test_auto_renumber_for_format_abaqus_allows_nonconsecutive():
    """Test Abaqus requirements do not force consecutive renumbering."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    mesh = SGMesh(
        points,
        cells,
        point_data={'node_id': [10, 50, 100]},
        cell_data={'element_id': [[7]]},
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        nodes_ren, elems_ren = auto_renumber_for_format(mesh, 'abaqus')

    assert (nodes_ren, elems_ren) == (False, False)
    assert len(w) == 0
    assert mesh.point_data['node_id'].tolist() == [10, 50, 100]
    assert np.asarray(mesh.cell_data['element_id'][0], dtype=int).tolist() == [7]


@pytest.mark.unit
def test_auto_renumber_for_format_unknown_format_noop():
    """Test unknown format returns False/False and does not warn."""
    points = np.array([[0, 0, 0], [1, 0, 0]], dtype=float)
    cells = [('line', np.array([[0, 1]]))]
    mesh = SGMesh(points, cells)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        nodes_ren, elems_ren = auto_renumber_for_format(mesh, 'unknown-format')

    assert (nodes_ren, elems_ren) == (False, False)
    assert len(w) == 0


# ============================================================================
# Test ensure_element_ids
# ============================================================================

@pytest.mark.unit
def test_ensure_element_ids_creates_ids():
    """Test that ensure_element_ids creates IDs when missing."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=float)
    cells = [
        ('triangle', np.array([[0, 1, 2]])),
        ('triangle', np.array([[1, 3, 2]]))
    ]
    
    mesh = SGMesh(points, cells)
    
    # Should not have element_id initially
    assert 'element_id' not in mesh.cell_data
    
    ensure_element_ids(mesh)
    
    # Should now have element_id
    assert 'element_id' in mesh.cell_data
    assert len(mesh.cell_data['element_id']) == 2
    assert mesh.cell_data['element_id'][0] == [1]
    assert mesh.cell_data['element_id'][1] == [2]


@pytest.mark.unit
def test_ensure_element_ids_preserves_existing():
    """Test that ensure_element_ids preserves existing IDs."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    cell_data = {'element_id': [[100]]}
    
    mesh = SGMesh(points, cells, cell_data=cell_data)
    ensure_element_ids(mesh)
    
    # Should preserve existing ID
    assert mesh.cell_data['element_id'][0] == [100]


@pytest.mark.unit
def test_ensure_element_ids_fills_missing_blocks():
    """Test that ensure_element_ids fills in missing blocks."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=float)
    cells = [
        ('triangle', np.array([[0, 1, 2]])),
        ('triangle', np.array([[1, 3, 2], [0, 3, 1]]))
    ]
    
    # Create mesh without cell_data first
    mesh = SGMesh(points, cells)
    
    # Manually add element_id for first block only
    mesh.cell_data['element_id'] = [[10]]
    
    ensure_element_ids(mesh)
    
    # First block preserved, second block generated
    assert mesh.cell_data['element_id'][0] == [10]
    assert mesh.cell_data['element_id'][1] == [11, 12]


@pytest.mark.unit
def test_ensure_element_ids_multiple_blocks():
    """Test ensure_element_ids with multiple cell blocks."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=float)
    cells = [
        ('line', np.array([[0, 1], [1, 2]])),
        ('triangle', np.array([[0, 1, 2], [1, 3, 2]]))
    ]
    
    mesh = SGMesh(points, cells)
    ensure_element_ids(mesh)
    
    assert len(mesh.cell_data['element_id']) == 2
    assert mesh.cell_data['element_id'][0] == [1, 2]
    assert mesh.cell_data['element_id'][1] == [3, 4]


@pytest.mark.unit
def test_ensure_element_ids_empty_cell_data():
    """Test ensure_element_ids when cell_data is empty."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    
    mesh = SGMesh(points, cells, cell_data={})
    ensure_element_ids(mesh)
    
    assert 'element_id' in mesh.cell_data
    assert mesh.cell_data['element_id'][0] == [1]


@pytest.mark.unit
def test_ensure_element_ids_idempotent():
    """Test that calling ensure_element_ids multiple times is safe."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    
    mesh = SGMesh(points, cells)
    
    ensure_element_ids(mesh)
    first_ids = mesh.cell_data['element_id'][0].copy()
    
    ensure_element_ids(mesh)
    second_ids = mesh.cell_data['element_id'][0]
    
    # Should not change existing IDs
    assert first_ids == second_ids


# ============================================================================
# Integration tests
# ============================================================================

@pytest.mark.unit
def test_validate_and_mapping_integration():
    """Test that validation and mapping work together."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([1, 2, 3])}
    
    mesh = SGMesh(points, cells, point_data=point_data)
    
    # Validate node IDs
    validate_node_ids(mesh.point_data['node_id'], format='vabs')
    
    # Get mapping
    mapping = get_node_id_mapping(mesh)
    
    # Verify mapping is correct
    assert mapping[1] == 0
    assert mapping[2] == 1
    assert mapping[3] == 2


@pytest.mark.unit
def test_ensure_and_validate_elements_integration():
    """Test that ensure and validate work together."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2], [0, 2, 1]]))]
    
    mesh = SGMesh(points, cells)
    
    # Ensure element IDs exist
    ensure_element_ids(mesh)
    
    # Validate element IDs
    validate_element_ids(mesh.cell_data['element_id'], format='vabs')


# ============================================================================
# Test check_duplicate_ids
# ============================================================================

@pytest.mark.unit
def test_check_duplicate_ids_none():
    """Test check_duplicate_ids with no duplicates."""
    result = check_duplicate_ids([1, 2, 3, 4, 5])
    assert result == []


@pytest.mark.unit
def test_check_duplicate_ids_single():
    """Test check_duplicate_ids with single duplicate."""
    result = check_duplicate_ids([1, 2, 3, 2, 4])
    assert result == [2]


@pytest.mark.unit
def test_check_duplicate_ids_multiple():
    """Test check_duplicate_ids with multiple duplicates."""
    result = check_duplicate_ids([1, 2, 3, 2, 4, 3, 5, 1])
    assert result == [1, 2, 3]


@pytest.mark.unit
def test_check_duplicate_ids_numpy_array():
    """Test check_duplicate_ids with numpy array."""
    result = check_duplicate_ids(np.array([1, 2, 3, 2, 4]))
    assert result == [2]


@pytest.mark.unit
def test_check_duplicate_ids_empty():
    """Test check_duplicate_ids with empty list."""
    result = check_duplicate_ids([])
    assert result == []


# ============================================================================
# Test check_forbidden_ids
# ============================================================================

@pytest.mark.unit
def test_check_forbidden_ids_generic():
    """Test that generic format allows all IDs."""
    result = check_forbidden_ids([0, -1, 1, 2], format='generic')
    assert result == []


@pytest.mark.unit
def test_check_forbidden_ids_vabs_zero():
    """Test VABS format forbids ID=0."""
    result = check_forbidden_ids([0, 1, 2, 3], format='vabs')
    assert result == [0]


@pytest.mark.unit
def test_check_forbidden_ids_vabs_negative():
    """Test VABS format forbids negative IDs."""
    result = check_forbidden_ids([-1, 0, 1, 2], format='vabs')
    assert result == [-1, 0]


@pytest.mark.unit
def test_check_forbidden_ids_swiftcomp():
    """Test SwiftComp format forbids non-positive IDs."""
    result = check_forbidden_ids([-5, 0, 1, 2], format='swiftcomp')
    assert result == [-5, 0]


@pytest.mark.unit
def test_check_forbidden_ids_abaqus():
    """Test Abaqus format forbids ID=0 and negative IDs."""
    result = check_forbidden_ids([0, 1, 2, 3], format='abaqus')
    assert result == [0]
    
    result = check_forbidden_ids([-1, 0, 1, 2], format='abaqus')
    assert result == [-1, 0]


@pytest.mark.unit
def test_check_forbidden_ids_valid():
    """Test check_forbidden_ids with all valid IDs."""
    result = check_forbidden_ids([1, 2, 3, 4, 5], format='vabs')
    assert result == []


@pytest.mark.unit
def test_check_forbidden_ids_numpy():
    """Test check_forbidden_ids with numpy array."""
    result = check_forbidden_ids(np.array([0, 1, 2]), format='abaqus')
    assert result == [0]


# ============================================================================
# Test validate_node_ids with duplicates and forbidden IDs
# ============================================================================

@pytest.mark.unit
def test_validate_node_ids_duplicate_vabs():
    """Test VABS validation catches duplicate node IDs."""
    with pytest.raises(ValueError, match="Duplicate Node IDs found: \\[2\\]"):
        validate_node_ids([1, 2, 2, 3], format='vabs')


@pytest.mark.unit
def test_validate_node_ids_duplicate_swiftcomp():
    """Test SwiftComp validation catches duplicate node IDs."""
    with pytest.raises(ValueError, match="Duplicate Node IDs found: \\[1, 2\\]"):
        validate_node_ids([1, 2, 3, 1, 2], format='swiftcomp')


@pytest.mark.unit
def test_validate_node_ids_forbidden_vabs():
    """Test VABS validation catches forbidden ID=0."""
    with pytest.raises(ValueError, match="Forbidden Node IDs found: \\[0\\]"):
        validate_node_ids([0, 1, 2, 3], format='vabs')


@pytest.mark.unit
def test_validate_node_ids_forbidden_negative():
    """Test validation catches negative IDs."""
    with pytest.raises(ValueError, match="Forbidden Node IDs found: \\[-1, 0\\]"):
        validate_node_ids([-1, 0, 1, 2], format='vabs')


@pytest.mark.unit
def test_validate_node_ids_abaqus_valid():
    """Test Abaqus format allows non-consecutive but positive IDs."""
    # Abaqus allows non-consecutive IDs as long as they're positive and unique
    validate_node_ids([1, 5, 10, 15], format='abaqus')


@pytest.mark.unit
def test_validate_node_ids_abaqus_forbidden_zero():
    """Test Abaqus validation catches forbidden ID=0."""
    with pytest.raises(ValueError, match="Forbidden Node IDs found: \\[0\\]"):
        validate_node_ids([0, 1, 2, 3], format='abaqus')
    
    with pytest.raises(ValueError, match="Abaqus requires node IDs to be positive"):
        validate_node_ids([0, 1, 2, 3], format='abaqus')


@pytest.mark.unit
def test_validate_node_ids_abaqus_duplicate():
    """Test Abaqus validation catches duplicate IDs."""
    with pytest.raises(ValueError, match="Duplicate Node IDs found: \\[5\\]"):
        validate_node_ids([1, 5, 10, 5, 15], format='abaqus')


# ============================================================================
# Test validate_element_ids with duplicates and forbidden IDs
# ============================================================================

@pytest.mark.unit
def test_validate_element_ids_duplicate_vabs():
    """Test VABS validation catches duplicate element IDs."""
    with pytest.raises(ValueError, match="Duplicate Element IDs found: \\[3\\]"):
        validate_element_ids([[1, 2, 3], [3, 4, 5]], format='vabs')


@pytest.mark.unit
def test_validate_element_ids_forbidden_vabs():
    """Test VABS validation catches forbidden ID=0."""
    with pytest.raises(ValueError, match="Forbidden Element IDs found: \\[0\\]"):
        validate_element_ids([[0, 1, 2], [3, 4, 5]], format='vabs')


@pytest.mark.unit
def test_validate_element_ids_abaqus_valid():
    """Test Abaqus format allows non-consecutive but positive IDs."""
    validate_element_ids([[1, 5, 10], [20, 30, 40]], format='abaqus')


@pytest.mark.unit
def test_validate_element_ids_abaqus_forbidden_zero():
    """Test Abaqus validation catches forbidden ID=0."""
    with pytest.raises(ValueError, match="Forbidden Element IDs found: \\[0\\]"):
        validate_element_ids([[0, 1, 2], [3, 4, 5]], format='abaqus')
    
    with pytest.raises(ValueError, match="Abaqus requires element IDs to be positive"):
        validate_element_ids([[0, 1, 2]], format='abaqus')


@pytest.mark.unit
def test_validate_element_ids_abaqus_duplicate():
    """Test Abaqus validation catches duplicate IDs."""
    with pytest.raises(ValueError, match="Duplicate Element IDs found: \\[5\\]"):
        validate_element_ids([[1, 5, 10], [5, 20, 30]], format='abaqus')
