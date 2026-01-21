"""Test for _read_output_node_strain_stress_case_global_gmsh function."""
import pytest
from pathlib import Path

from sgio.iofunc.swiftcomp._output import _read_output_node_strain_stress_case_global_gmsh
from sgio.core.sg import StructureGene


@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "files" / "swiftcomp"


def test_read_output_node_strain_stress_case_global_gmsh(test_data_dir):
    """Test reading element node strain and stress data in Gmsh format.
    
    This test verifies that the function correctly:
    1. Reads 12 blocks of data (6 strain components + 6 stress components)
    2. Transforms the data from component-based to element-based structure
    3. Returns two dictionaries (strains and stresses)
    4. Each element has the correct number of nodes
    5. Each node has 6 components
    """
    # Path to the test file
    test_file = test_data_dir / "sg31t_hex20_sc21.sg.sn"
    
    # Create a minimal StructureGene object (not used in current implementation but required by signature)
    sg = StructureGene()
    
    # Number of elements in the test file (from line 9 of sg31t_hex20_sc21.sg: nelem=100)
    nelem = 100
    
    # Open the file and read the data
    with open(test_file, 'r') as file:
        strains, stresses = _read_output_node_strain_stress_case_global_gmsh(file, nelem, sg)
    
    # Verify that both dictionaries are returned
    assert strains is not None, "Strains dictionary should not be None"
    assert stresses is not None, "Stresses dictionary should not be None"
    
    # Verify that we have the correct number of elements
    assert len(strains) == nelem, f"Expected {nelem} elements in strains, got {len(strains)}"
    assert len(stresses) == nelem, f"Expected {nelem} elements in stresses, got {len(stresses)}"
    
    # Verify that both dictionaries have the same element IDs
    assert set(strains.keys()) == set(stresses.keys()), "Strain and stress dictionaries should have the same element IDs"
    
    # Check the first element (element ID 1)
    assert 1 in strains, "Element 1 should be in strains dictionary"
    assert 1 in stresses, "Element 1 should be in stresses dictionary"
    
    # Verify that element 1 has 20 nodes (hex20 element)
    assert len(strains[1]) == 20, f"Element 1 should have 20 nodes, got {len(strains[1])}"
    assert len(stresses[1]) == 20, f"Element 1 should have 20 nodes, got {len(stresses[1])}"
    
    # Verify that each node has 6 components
    for node_idx in range(20):
        assert len(strains[1][node_idx]) == 6, f"Node {node_idx} of element 1 should have 6 strain components"
        assert len(stresses[1][node_idx]) == 6, f"Node {node_idx} of element 1 should have 6 stress components"
    
    # Verify the first node of element 1 has the expected strain values
    # From the file:
    # - e11: line 1, value 1 = 3.6550836E-006
    # - e22: line 102, value 1 = -1.3534571E-006
    # - e33: line 203, value 1 = -2.1347957E-006
    # - 2e23: line 304, value 1 = -2.8264526E-006
    # - 2e13: line 405, value 1 = -7.5999034E-007
    # - 2e12: line 506, value 1 = -5.2931058E-007
    expected_strain_node1 = [
        3.6550836E-006,   # e11
        -1.3534571E-006,  # e22
        -2.1347957E-006,  # e33
        -2.8264526E-006,  # 2e23
        -7.5999034E-007,  # 2e13
        -5.2931058E-007,  # 2e12
    ]

    for i, expected_val in enumerate(expected_strain_node1):
        actual_val = strains[1][0][i]
        assert abs(actual_val - expected_val) < 1e-12, \
            f"Strain component {i} of node 0 in element 1: expected {expected_val}, got {actual_val}"
    
    # Verify the first node of element 1 has the expected stress values
    # From the file:
    # - s11: line 607, value 1 = 5.0989044E+005
    # - s22: line 708, value 1 = 1.2568821E+003
    # - s33: line 809, value 1 = 2.6222317E+003
    # - s23: line 910, value 1 = 2.0110459E+003
    # - s13: line 1011, value 1 = 8.8529496E+004
    # - s12: line 1112, value 1 = 6.6900720E+004
    expected_stress_node1 = [
        5.0989044E+005,  # s11
        1.2568821E+003,  # s22
        2.6222317E+003,  # s33
        2.0110459E+003,  # s23
        8.8529496E+004,  # s13
        6.6900720E+004,  # s12
    ]
    
    for i, expected_val in enumerate(expected_stress_node1):
        actual_val = stresses[1][0][i]
        assert abs(actual_val - expected_val) < 1e-12, \
            f"Stress component {i} of node 0 in element 1: expected {expected_val}, got {actual_val}"
    
    # Verify all elements have 20 nodes (hex20)
    for eid in strains.keys():
        assert len(strains[eid]) == 20, f"Element {eid} should have 20 nodes in strains"
        assert len(stresses[eid]) == 20, f"Element {eid} should have 20 nodes in stresses"
        
        # Verify each node has 6 components
        for node_idx in range(20):
            assert len(strains[eid][node_idx]) == 6, \
                f"Node {node_idx} of element {eid} should have 6 strain components"
            assert len(stresses[eid][node_idx]) == 6, \
                f"Node {node_idx} of element {eid} should have 6 stress components"
    
    print(f"✓ Successfully read {nelem} elements")
    print(f"✓ Each element has 20 nodes")
    print(f"✓ Each node has 6 strain and 6 stress components")
    print(f"✓ Data structure matches docstring specification")


if __name__ == "__main__":
    # Allow running the test directly
    test_data_dir = Path(__file__).parent / "files" / "swiftcomp"
    test_read_output_node_strain_stress_case_global_gmsh(test_data_dir)
    print("\nAll tests passed!")

