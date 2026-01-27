"""Test VABS output state reading.

This module tests reading VABS output state data including:
- Displacement, strain, and stress (dehomogenization)
- Failure indices
- Multiple load cases
"""
import os
from pathlib import Path
import pytest
import yaml

from sgio import (
    read,
    readOutputState,
    addCellDictDataToMesh,
    write,
    configure_logging,
    logger,
)

configure_logging(cout_level='info')

# Component labels for visualization
NAME_E = ['e11', '2e12', '2e13', 'e22', '2e23', 'e33']  # Strain in global coordinate
NAME_EM = ['e11m', '2e12m', '2e13m', 'e22m', '2e23m', 'e33m']  # Strain in material coordinate
NAME_S = ['s11', '2s12', '2s13', 's22', '2s23', 's33']  # Stress in global coordinate
NAME_SM = ['s11m', 's12m', 's13m', 's22m', 's23m', 's33m']  # Stress in material coordinate


@pytest.mark.io
@pytest.mark.vabs
@pytest.mark.parametrize("fn_test_cases", [
    'test_io_vabs_out_d.yml',
])
def test_vabs_output_state_dehomogenization(fn_test_cases, test_data_dir, tmp_path):
    """Test reading VABS output state data (displacement/strain/stress).
    
    This test verifies:
    1. VABS output state files can be read
    2. Strain and stress data are extracted correctly
    3. Data can be added to mesh for visualization
    4. Results can be written to output formats
    
    Args:
        fn_test_cases: Name of YAML test case file
        test_data_dir: Fixture providing test data directory
        tmp_path: Pytest fixture for temporary directory
    """
    # Look for test case file in yaml subdirectory first, then root fixtures, then legacy
    test_case_path = test_data_dir / "yaml" / fn_test_cases
    if not test_case_path.exists():
        test_case_path = test_data_dir / fn_test_cases
    if not test_case_path.exists():
        # Try legacy location
        legacy_path = Path(__file__).parent.parent.parent / "files" / fn_test_cases
        if legacy_path.exists():
            test_case_path = legacy_path
        else:
            pytest.skip(f"Test case file not found: {fn_test_cases}")

    with open(test_case_path, 'r') as file:
        test_cases = yaml.safe_load(file)

    # Create output directory
    output_dir = tmp_path / "vabs_out_state_d_output"
    os.makedirs(output_dir, exist_ok=True)

    for _case in test_cases:
        # Resolve input file path
        fn_in_rel = _case["fn_in"]
        fn_in = str(test_data_dir / fn_in_rel)
        if not Path(fn_in).exists():
            # Try legacy location
            fn_in = str(Path(__file__).parent.parent.parent / "files" / fn_in_rel)
        
        ff_in = _case['ff_in']
        version_in = _case['version_in']
        num_cases = _case.get('num_cases', 1)
        logger.info(f'num_cases: {num_cases}')

        # Read the cross-section model
        sg = read(fn_in, ff_in)

        # Read the output state
        state_cases = readOutputState(
            fn_in, ff_in, 'd', sg=sg, tool_version=version_in, num_cases=num_cases)
        logger.info(state_cases)
        logger.info(f'{len(state_cases)} state cases')

        # Verify state cases were read
        assert len(state_cases) > 0, "No state cases were read"
        assert len(state_cases) == num_cases, f"Expected {num_cases} cases, got {len(state_cases)}"

        # Add data to the mesh
        for j, state_case in enumerate(state_cases):
            logger.info(f'state case {j+1}')
            
            # Element strain in global coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_E]
            addCellDictDataToMesh(_name, state_case.getState('ee').data, sg.mesh)
            
            # Element strain in material coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_EM]
            addCellDictDataToMesh(_name, state_case.getState('eem').data, sg.mesh)
            
            # Element stress in global coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_S]
            addCellDictDataToMesh(_name, state_case.getState('es').data, sg.mesh)
            
            # Element stress in material coordinate
            _name = [f'case{j+1}_{name}' for name in NAME_SM]
            addCellDictDataToMesh(_name, state_case.getState('esm').data, sg.mesh)

        if 'fn_out' in _case.keys():
            fn_out = str(output_dir / _case["fn_out"])
            ff_out = _case['ff_out']
            format_version = _case['format_version']

            # Write the mesh to a file
            write(sg, fn_out, ff_out, format_version=format_version)

            # Verify output file was created
            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"
            assert os.path.getsize(fn_out) > 0, f"Output file is empty: {fn_out}"


@pytest.mark.io
@pytest.mark.vabs
@pytest.mark.parametrize("fn_test_cases", [
    'test_io_vabs_out_fi.yml',
])
def test_vabs_output_state_failure(fn_test_cases, test_data_dir, tmp_path):
    """Test reading VABS output failure index state data.
    
    This test verifies:
    1. VABS failure index output can be read
    2. Failure indices and strength ratios are extracted
    3. Data can be added to mesh for visualization
    4. Results can be written to output formats
    
    Args:
        fn_test_cases: Name of YAML test case file
        test_data_dir: Fixture providing test data directory
        tmp_path: Pytest fixture for temporary directory
    """
    # Look for test case file in yaml subdirectory first, then root fixtures, then legacy
    test_case_path = test_data_dir / "yaml" / fn_test_cases
    if not test_case_path.exists():
        test_case_path = test_data_dir / fn_test_cases
    if not test_case_path.exists():
        legacy_path = Path(__file__).parent.parent.parent / "files" / fn_test_cases
        if legacy_path.exists():
            test_case_path = legacy_path
        else:
            pytest.skip(f"Test case file not found: {fn_test_cases}")

    with open(test_case_path, 'r') as file:
        test_cases = yaml.safe_load(file)

    # Create output directory
    output_dir = tmp_path / "vabs_out_state_f_output"
    os.makedirs(output_dir, exist_ok=True)

    for _case in test_cases:
        # Resolve input file path
        fn_in_rel = _case["fn_in"]
        fn_in = str(test_data_dir / fn_in_rel)
        if not Path(fn_in).exists():
            fn_in = str(Path(__file__).parent.parent.parent / "files" / fn_in_rel)

        ff_in = _case['ff_in']
        version_in = _case['version_in']
        num_cases = _case.get('num_cases', 1)
        logger.info(f'num_cases: {num_cases}')

        # Read the cross-section model
        sg = read(fn_in, ff_in)

        # Read the output state (failure indices)
        state_cases = readOutputState(
            fn_in, ff_in, 'fi', sg=sg, tool_version=version_in, num_cases=num_cases)
        logger.info(state_cases)

        # Verify state cases were read
        assert len(state_cases) > 0, "No state cases were read"
        assert len(state_cases) == num_cases, f"Expected {num_cases} cases, got {len(state_cases)}"

        # Add data to the mesh
        for j, state_case in enumerate(state_cases):
            logger.info(f'state case {j+1}')

            # Add failure index data
            addCellDictDataToMesh(
                f'case{j+1}_fi', state_case.getState('fi').data, sg.mesh)

            # Add strength ratio data
            addCellDictDataToMesh(
                f'case{j+1}_sr', state_case.getState('sr').data, sg.mesh)

        if 'fn_out' in _case.keys():
            fn_out = str(output_dir / _case["fn_out"])
            ff_out = _case['ff_out']
            format_version = _case['format_version']

            # Write the mesh to a file
            write(sg, fn_out, ff_out, format_version=format_version)

            # Verify output file was created
            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"
            assert os.path.getsize(fn_out) > 0, f"Output file is empty: {fn_out}"

