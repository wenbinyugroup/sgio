"""Test mesh validation and auto-numbering for VABS/SwiftComp write operations.

Phase 4 behavior: numbering is handled automatically by the library; users do not
pass renumber/sequential flags.
"""
import pytest
import numpy as np
from io import StringIO

from sgio.core.mesh import SGMesh
from sgio.core.numbering import validate_node_ids
from sgio.iofunc.vabs._mesh import write_buffer as vabs_write_buffer
from sgio.iofunc.swiftcomp._mesh import write_buffer as sc_write_buffer


# ---------------------------------------------------------------------------
# validate_node_ids (replaces the old _validate_consecutive_numbering)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_node_ids_valid():
    """Test validation passes for consecutive node IDs from 1."""
    node_ids = [1, 2, 3, 4, 5]
    n_nodes = 5
    # Should not raise
    validate_node_ids(node_ids, n_nodes=n_nodes, format='vabs')


@pytest.mark.unit
def test_validate_node_ids_empty():
    """Test validation passes for empty node ID list."""
    node_ids = []
    n_nodes = 5
    # Empty list means nothing to validate
    validate_node_ids(node_ids, n_nodes=n_nodes, format='vabs')


@pytest.mark.unit
def test_validate_node_ids_missing_ids():
    """Test validation fails when node IDs are missing (non-consecutive)."""
    node_ids = [1, 2, 4, 5]  # Missing 3
    n_nodes = 5
    with pytest.raises(ValueError, match="[Mm]issing"):
        validate_node_ids(node_ids, n_nodes=n_nodes, format='vabs')


@pytest.mark.unit
def test_validate_node_ids_extra_ids():
    """Test validation fails when node IDs contain unexpected values."""
    node_ids = [1, 2, 3, 4, 6]  # Has 6 instead of 5
    n_nodes = 5
    with pytest.raises(ValueError):
        validate_node_ids(node_ids, n_nodes=n_nodes, format='vabs')


@pytest.mark.unit
def test_validate_node_ids_wrong_count():
    """Test validation fails when node ID count doesn't match."""
    node_ids = [1, 2, 3]
    n_nodes = 5
    with pytest.raises(ValueError, match="[Mm]issing"):
        validate_node_ids(node_ids, n_nodes=n_nodes, format='vabs')


@pytest.mark.unit
def test_validate_node_ids_starts_from_zero():
    """Test validation fails when node IDs start from 0 (forbidden for vabs)."""
    node_ids = [0, 1, 2, 3, 4]
    n_nodes = 5
    with pytest.raises(ValueError, match="[Ff]orbidden"):
        validate_node_ids(node_ids, n_nodes=n_nodes, format='vabs')


@pytest.mark.unit
def test_validate_node_ids_duplicates():
    """Test validation fails when node IDs have duplicates."""
    node_ids = [1, 2, 2, 3, 4]  # Duplicate 2, missing 5
    n_nodes = 5
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        validate_node_ids(node_ids, n_nodes=n_nodes, format='vabs')


# ---------------------------------------------------------------------------
# VABS write_buffer — auto-renumber tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.vabs
def test_vabs_write_auto_renumbers_invalid_numbering():
    """Test VABS write auto-renumbers non-consecutive node IDs (Phase 4 behavior)."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([1, 3, 4])}  # non-consecutive
    cell_data = {'property_id': [np.array([1])]}
    mesh = SGMesh(points, cells, point_data=point_data, cell_data=cell_data)

    f = StringIO()
    vabs_write_buffer(f, mesh, sgdim=2, model_space='xy')

    # Auto-renumber should produce consecutive 1-based IDs
    assert np.array_equal(mesh.point_data['node_id'], np.array([1, 2, 3]))


@pytest.mark.unit
@pytest.mark.vabs
def test_vabs_write_with_valid_numbering():
    """Test VABS write succeeds with consecutive node IDs."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([1, 2, 3])}
    cell_data = {'property_id': [np.array([1])]}
    mesh = SGMesh(points, cells, point_data=point_data, cell_data=cell_data)

    f = StringIO()
    vabs_write_buffer(f, mesh, sgdim=2, model_space='xy')
    # No exception means success
    assert np.array_equal(mesh.point_data['node_id'], np.array([1, 2, 3]))


# ---------------------------------------------------------------------------
# SwiftComp write_buffer — auto-renumber tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.swiftcomp
def test_swiftcomp_write_auto_renumbers_invalid_numbering():
    """Test SwiftComp write auto-renumbers non-consecutive node IDs (Phase 4 behavior)."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([1, 3, 4])}  # non-consecutive
    cell_data = {'property_id': [np.array([1])]}
    mesh = SGMesh(points, cells, point_data=point_data, cell_data=cell_data)

    f = StringIO()
    sc_write_buffer(f, mesh, sgdim=2, model_space='xy')

    assert np.array_equal(mesh.point_data['node_id'], np.array([1, 2, 3]))


@pytest.mark.unit
@pytest.mark.swiftcomp
def test_swiftcomp_write_with_valid_numbering():
    """Test SwiftComp write succeeds with consecutive node IDs."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [('triangle', np.array([[0, 1, 2]]))]
    point_data = {'node_id': np.array([1, 2, 3])}
    cell_data = {'property_id': [np.array([1])]}
    mesh = SGMesh(points, cells, point_data=point_data, cell_data=cell_data)

    f = StringIO()
    sc_write_buffer(f, mesh, sgdim=2, model_space='xy')
    assert np.array_equal(mesh.point_data['node_id'], np.array([1, 2, 3]))
