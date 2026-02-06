"""
Test Abaqus reader node/element numbering handling.

Critical test for the bug fix: Abaqus files with non-consecutive node IDs
must be converted to 0-based array indices in cell connectivity.
"""
import pytest
import numpy as np
from pathlib import Path

from sgio.iofunc.abaqus import read


FIXTURES_DIR = Path(__file__).parent.parent.parent / 'fixtures' / 'abaqus'


def test_abaqus_node_id_to_index_conversion():
    """
    Test that Abaqus reader converts original node IDs to 0-based array indices.
    
    This is a critical test for the bug fix in process_mesh() where element
    connectivity must use array indices (0-based) not original node IDs.
    
    The bug was: _nids = list(map(int, _elem.data[1:]))  # Kept original IDs
    The fix: _nids = [nid2pid[nid] for nid in _nids_original]  # Convert to indices
    """
    # Read an Abaqus file - any file will work for this test
    inp_file = FIXTURES_DIR / 'box_cus' / 'box_cus.inp'
    
    if not inp_file.exists():
        pytest.skip(f"Test fixture not found: {inp_file}")
    
    # Read the Abaqus file
    sg = read(str(inp_file), sgdim=2, model='pl1')
    mesh = sg.mesh
    
    # Verify data structure correctness
    assert hasattr(mesh, 'points'), "Mesh should have points"
    assert hasattr(mesh, 'cells'), "Mesh should have cells"
    assert 'node_id' in mesh.point_data, "Mesh should preserve original node IDs"
    
    # Critical test: Cell connectivity should use 0-based array indices
    for cell_block in mesh.cells:
        connectivity = cell_block.data
        
        # All indices in connectivity should be valid array indices (0-based)
        max_index = np.max(connectivity)
        min_index = np.min(connectivity)
        
        # Indices must be in range [0, len(points))
        assert min_index >= 0, \
            f"Cell connectivity contains negative index: {min_index}"
        assert max_index < len(mesh.points), \
            f"Cell connectivity index {max_index} exceeds points array size {len(mesh.points)}"
        
        # Verify we can actually access all referenced points without IndexError
        for element_nodes in connectivity:
            for node_idx in element_nodes:
                # This should NOT raise IndexError
                point = mesh.points[node_idx]
                assert point is not None, f"Cannot access point at index {node_idx}"


def test_abaqus_preserves_original_node_ids():
    """
    Test that original node IDs from Abaqus file are preserved in point_data.
    
    This ensures we can round-trip the data while maintaining the dual numbering system:
    - Internal: 0-based array indices for processing
    - External: Original IDs preserved for writing back to file
    """
    inp_file = FIXTURES_DIR / 'box_cus' / 'box_cus.inp'
    
    if not inp_file.exists():
        pytest.skip(f"Test fixture not found: {inp_file}")
    
    sg = read(str(inp_file), sgdim=2, model='pl1')
    mesh = sg.mesh
    
    # Original node IDs should be stored
    node_ids = mesh.point_data.get('node_id', [])
    assert len(node_ids) > 0, "Original node IDs should be preserved"
    assert len(node_ids) == len(mesh.points), \
        "Should have one node ID for each point"
    
    # Original element IDs should be stored
    elem_ids = mesh.cell_data.get('element_id', [])
    assert len(elem_ids) > 0, "Original element IDs should be preserved"
    assert len(elem_ids) == len(mesh.cells), \
        "Should have element IDs for each cell block"


def test_abaqus_arbitrary_node_numbering():
    """
    Test handling of arbitrary (non-consecutive) node numbering.
    
    Abaqus allows arbitrary node numbering like [100, 200, 300].
    This test creates a minimal example to verify the fix works for such cases.
    """
    import tempfile
    import os
    
    # Create a minimal Abaqus input file with non-consecutive node IDs
    abaqus_content = """*Heading
Test file with non-consecutive node IDs
*Node
100, 0.0, 0.0, 0.0
200, 1.0, 0.0, 0.0
300, 0.0, 1.0, 0.0
*Element, type=CPS3, elset=test_elset
5000, 100, 200, 300
*Material, name=test_mat
*Elastic, type=isotropic
210000.0, 0.3
*Solid Section, elset=test_elset, material=test_mat
"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.inp', delete=False) as f:
        f.write(abaqus_content)
        temp_file = f.name
    
    try:
        # Read the file
        sg = read(temp_file, sgdim=2, model='pl1')
        mesh = sg.mesh
        
        # Verify node IDs are preserved
        assert list(mesh.point_data['node_id']) == [100, 200, 300], \
            "Original node IDs should be preserved"
        
        # Verify we have 3 points
        assert len(mesh.points) == 3, "Should have 3 nodes"
        
        # CRITICAL TEST: Cell connectivity should use array indices [0, 1, 2]
        # NOT original node IDs [100, 200, 300]
        assert len(mesh.cells) > 0, "Should have at least one cell block"
        connectivity = mesh.cells[0].data[0]  # First element
        
        # The connectivity should be [0, 1, 2] (array indices)
        # If the bug still exists, it would be [100, 200, 300] (original IDs)
        expected = [0, 1, 2]
        actual = connectivity.tolist()
        
        assert actual == expected, \
            f"Cell connectivity should use 0-based indices {expected}, got {actual}. " \
            f"If this is [100, 200, 300], the bug fix failed!"
        
        # Verify element ID is preserved
        assert mesh.cell_data['element_id'][0][0] == 5000, \
            "Original element ID should be preserved"
        
        # Verify we can access all points using the connectivity indices
        for idx in connectivity:
            point = mesh.points[idx]  # Should not raise IndexError
            assert point.shape == (3,), f"Point at index {idx} should be 3D"
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file)


def test_abaqus_node_id_mapping_consistency():
    """
    Test that the nid2pid mapping is consistent and complete.
    
    Every node ID in the file should map to a unique array index.
    """
    inp_file = FIXTURES_DIR / 'box_cus' / 'box_cus.inp'
    
    if not inp_file.exists():
        pytest.skip(f"Test fixture not found: {inp_file}")
    
    sg = read(str(inp_file), sgdim=2, model='pl1')
    mesh = sg.mesh
    
    node_ids = mesh.point_data['node_id']
    
    # Create the mapping that should have been used internally
    nid2pid = {nid: i for i, nid in enumerate(node_ids)}
    
    # Verify all node IDs are unique
    assert len(node_ids) == len(set(node_ids)), \
        "Node IDs should be unique"
    
    # Verify mapping is correct: for each position, nid2pid[node_id] should equal position
    for i, nid in enumerate(node_ids):
        assert nid2pid[nid] == i, \
            f"Mapping mismatch: nid2pid[{nid}] = {nid2pid[nid]}, expected {i}"
    
    # Verify all cell connectivity uses valid mapped indices
    for cell_block in mesh.cells:
        for element_nodes in cell_block.data:
            for node_idx in element_nodes:
                assert 0 <= node_idx < len(node_ids), \
                    f"Invalid node index {node_idx}, should be in [0, {len(node_ids)})"
                # The node at this index should exist
                assert node_idx in range(len(mesh.points)), \
                    f"Node index {node_idx} not in points array"
