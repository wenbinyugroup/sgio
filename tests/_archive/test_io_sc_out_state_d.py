"""Test SwiftComp output state reading (displacement/strain/stress)."""
import os
from pathlib import Path
import pytest
import yaml

from sgio import (
    read,
    readOutputState,
    add_cell_dict_data_to_mesh,
    write,
    configure_logging,
    logger,
    )

configure_logging(cout_level='info')

# Component labels in visualization (must match the order in State labels)
name_e = ['e11', 'e22', 'e33', '2e23', '2e13', '2e12']  # Strain in global coordinate
name_em = ['e11m', 'e22m', 'e33m', '2e23m', '2e13m', '2e12m']  # Strain in material coordinate
name_s = ['s11', 's22', 's33', 's23', 's13', 's12']  # Stress in global coordinate (SwiftComp doesn't use '2' prefix)
name_sm = ['s11m', 's22m', 's33m', 's23m', 's13m', 's12m']  # Stress in material coordinate


@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "files"


@pytest.fixture(scope="module")
def output_dir(tmp_path_factory):
    """Fixture to provide a temporary output directory for test results."""
    return tmp_path_factory.mktemp("sc_out_state_d_output")


@pytest.mark.parametrize("fn_test_cases", [
    'test_io_sc_out_d.yml',
])
def test_io_sc_out_state_d(fn_test_cases, test_data_dir, output_dir):
    """Test reading SwiftComp output state data."""
    test_case_path = test_data_dir / fn_test_cases

    if not test_case_path.exists():
        pytest.skip(f"Test case file not found: {test_case_path}")

    with open(test_case_path, 'r') as file:
        test_cases = yaml.safe_load(file)

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for _case in test_cases:
        fn_in = str(test_data_dir / _case["fn_in"])
        ff_in = _case['ff_in']
        sgdim = _case['sgdim']
        model_type = _case['model_type']
        version_in = _case['version_in']
        num_cases = _case.get('num_cases', 1)
        extension = _case.get('extension', ['sn', 'snm'])
        logger.info(f'num_cases: {num_cases}')

        # Read the cross-section model
        sg = read(fn_in, ff_in, sgdim=sgdim, model_type=model_type)

        # Read the output state
        state_cases = readOutputState(
            fn_in, ff_in, 'd', sg=sg,
            tool_version=version_in, num_cases=num_cases, extension=extension)
        # logger.info(state_cases)
        # logger.info(f'{len(state_cases)} state cases')

        # Verify state cases were read
        assert len(state_cases) > 0, "No state cases were read"

        # Add data to the mesh
        for j, state_case in enumerate(state_cases):
            logger.info(f'state case {j+1}')
            # Element strain in global coordinate
            _name = [f'case{j+1}_{name}' for name in name_e]
            add_cell_dict_data_to_mesh(_name, state_case.getState('e').data, sg.mesh)
            # Element strain in material coordinate
            _name = [f'case{j+1}_{name}' for name in name_em]
            add_cell_dict_data_to_mesh(_name, state_case.getState('em').data, sg.mesh)
            # Element stress in global coordinate
            _name = [f'case{j+1}_{name}' for name in name_s]
            add_cell_dict_data_to_mesh(_name, state_case.getState('s').data, sg.mesh)
            # Element stress in material coordinate
            _name = [f'case{j+1}_{name}' for name in name_sm]
            add_cell_dict_data_to_mesh(_name, state_case.getState('sm').data, sg.mesh)

        if 'fn_out' in _case.keys():
            fn_out = str(output_dir / _case["fn_out"])
            ff_out = _case['ff_out']
            format_version = _case['format_version']

            # Write the mesh to a file
            write(sg, fn_out, ff_out, format_version=format_version)

            # Verify output file was created
            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"

