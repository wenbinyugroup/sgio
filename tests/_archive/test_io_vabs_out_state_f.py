"""Test VABS output state reading (failure indices)."""
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


@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "files"


@pytest.fixture(scope="module")
def output_dir(tmp_path_factory):
    """Fixture to provide a temporary output directory for test results."""
    return tmp_path_factory.mktemp("vabs_out_state_f_output")


@pytest.mark.parametrize("fn_test_cases", [
    'test_io_vabs_out_fi.yml',
])
def test_io_vabs_out_state_f(fn_test_cases, test_data_dir, output_dir):
    """Test reading VABS output failure index state data."""
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
        version_in = _case['version_in']
        num_cases = _case.get('num_cases', 1)
        logger.info(f'num_cases: {num_cases}')

        # Read the cross-section model
        sg = read(fn_in, ff_in)

        # Read the output state
        state_cases = readOutputState(
            fn_in, ff_in, 'fi', sg=sg, tool_version=version_in, num_cases=num_cases)
        logger.info(state_cases)

        # Verify state cases were read
        assert len(state_cases) > 0, "No state cases were read"

        # Add data to the mesh
        for j, state_case in enumerate(state_cases):
            logger.info(f'state case {j+1}')

            add_cell_dict_data_to_mesh(
                f'case{j+1}_fi', state_case.getState('fi').data, sg.mesh)
            add_cell_dict_data_to_mesh(
                f'case{j+1}_sr', state_case.getState('sr').data, sg.mesh)

        if 'fn_out' in _case.keys():
            fn_out = str(output_dir / _case["fn_out"])
            ff_out = _case['ff_out']
            format_version = _case['format_version']

            # Write the mesh to a file
            write(sg, fn_out, ff_out, format_version=format_version)

            # Verify output file was created
            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"

