"""Test SwiftComp output state reading.

This module tests:
1. Reading SwiftComp output state data (displacement/strain/stress)
2. Adding state data to mesh for visualization
3. Writing mesh with state data to output files
"""

import pytest
from pathlib import Path
import yaml

from sgio import (
    read,
    readOutputState,
    addCellDictDataToMesh,
    write,
    logger,
)
from sgio.iofunc.swiftcomp._output import _read_output_node_strain_stress_case_global_gmsh
from sgio.core.sg import StructureGene


# Component labels for visualization (must match the order in State labels)
NAME_E = ['e11', 'e22', 'e33', '2e23', '2e13', '2e12']  # Strain in global coordinate
NAME_EM = ['e11m', 'e22m', 'e33m', '2e23m', '2e13m', '2e12m']  # Strain in material coordinate
NAME_S = ['s11', 's22', 's33', 's23', 's13', 's12']  # Stress in global coordinate
NAME_SM = ['s11m', 's22m', 's33m', 's23m', 's13m', 's12m']  # Stress in material coordinate


@pytest.mark.io
@pytest.mark.swiftcomp
@pytest.mark.parametrize("fn_test_cases", [
    'test_io_sc_out_d.yml',
])
def test_swiftcomp_output_state_dehomogenization(fn_test_cases, test_data_dir, temp_dir):
    """Test reading SwiftComp output state data (dehomogenization).
    
    This test verifies that:
    1. SwiftComp output state files can be read
    2. State data contains strain and stress components
    3. State data can be added to mesh for visualization
    4. Mesh with state data can be written to output files
    
    Args:
        fn_test_cases: Name of YAML file containing test cases
        test_data_dir: Fixture providing test data directory
        temp_dir: Fixture providing temporary output directory
    """
    test_case_path = test_data_dir / fn_test_cases

    if not test_case_path.exists():
        pytest.skip(f"Test case file not found: {test_case_path}")

    with open(test_case_path, 'r') as file:
        test_cases = yaml.safe_load(file)

    for _case in test_cases:
        fn_in = str(test_data_dir / _case["fn_in"])
        ff_in = _case['ff_in']
        sgdim = _case['sgdim']
        model_type = _case['model_type']
        version_in = _case['version_in']
        num_cases = _case.get('num_cases', 1)
        extension = _case.get('extension', ['sn', 'snm'])
        
        logger.info(f'Reading {fn_in} with {num_cases} state cases')

        # Read the cross-section model
        sg = read(fn_in, ff_in, sgdim=sgdim, model_type=model_type)
        
        assert sg is not None, "Structure gene object should not be None"
        assert sg.mesh is not None, "Mesh should not be None"

        # Read the output state
        state_cases = readOutputState(
            fn_in, ff_in, 'd', sg=sg,
            tool_version=version_in, num_cases=num_cases, extension=extension)

        # Verify state cases were read
        assert len(state_cases) > 0, "No state cases were read"
        assert len(state_cases) == num_cases, f"Expected {num_cases} state cases, got {len(state_cases)}"
        
        logger.info(f'Successfully read {len(state_cases)} state cases')

        # Add data to the mesh
        for j, state_case in enumerate(state_cases):
            logger.info(f'Processing state case {j+1}')
            
            # Element strain in global coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_E]
            addCellDictDataToMesh(_name, state_case.getState('e').data, sg.mesh)
            
            # Element strain in material coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_EM]
            addCellDictDataToMesh(_name, state_case.getState('em').data, sg.mesh)
            
            # Element stress in global coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_S]
            addCellDictDataToMesh(_name, state_case.getState('s').data, sg.mesh)
            
            # Element stress in material coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_SM]
            addCellDictDataToMesh(_name, state_case.getState('sm').data, sg.mesh)

        # Write output if specified
        if 'fn_out' in _case.keys():
            fn_out = str(temp_dir / _case["fn_out"])
            ff_out = _case['ff_out']
            format_version = _case['format_version']

            # Write the mesh to a file
            write(sg, fn_out, ff_out, format_version=format_version)

            # Verify output file was created
            assert Path(fn_out).exists(), f"Output file was not created: {fn_out}"
            assert Path(fn_out).stat().st_size > 0, f"Output file is empty: {fn_out}"
            
            logger.info(f'Successfully wrote output to {fn_out}')


@pytest.mark.io
@pytest.mark.swiftcomp
def test_swiftcomp_state_data_structure():
    """Test that SwiftComp state data has the expected structure.

    This test verifies the structure of state data without requiring
    actual output files.
    """
    # Verify component name constants
    assert len(NAME_E) == 6, "Should have 6 strain components in global coordinates"
    assert len(NAME_EM) == 6, "Should have 6 strain components in material coordinates"
    assert len(NAME_S) == 6, "Should have 6 stress components in global coordinates"
    assert len(NAME_SM) == 6, "Should have 6 stress components in material coordinates"

    # Verify naming conventions - check that names are non-empty strings
    assert all(isinstance(name, str) and len(name) > 0 for name in NAME_E), "Global strain names should be non-empty strings"
    assert all(isinstance(name, str) and len(name) > 0 for name in NAME_EM), "Material strain names should be non-empty strings"
    assert all(isinstance(name, str) and len(name) > 0 for name in NAME_S), "Global stress names should be non-empty strings"
    assert all(isinstance(name, str) and len(name) > 0 for name in NAME_SM), "Material stress names should be non-empty strings"


@pytest.mark.io
@pytest.mark.swiftcomp
def test_read_output_node_strain_stress_gmsh_format(test_data_dir):
    """Test reading element node strain and stress data in Gmsh format.

    This test verifies that the _read_output_node_strain_stress_case_global_gmsh function correctly:
    1. Reads 12 blocks of data (6 strain components + 6 stress components)
    2. Transforms the data from component-based to element-based structure
    3. Returns two dictionaries (strains and stresses)
    4. Each element has the correct number of nodes
    5. Each node has 6 components

    This is a low-level test of the internal parsing function.
    """
    # Path to the test file
    test_file = test_data_dir / "swiftcomp" / "sg31t_hex20_sc21.sg.sn"

    if not test_file.exists():
        pytest.skip(f"Test file not found: {test_file}")

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

    logger.info(f"✓ Successfully read {nelem} elements")
    logger.info(f"✓ Each element has 20 nodes")
    logger.info(f"✓ Each node has 6 strain and 6 stress components")
    logger.info(f"✓ Data structure matches specification")

