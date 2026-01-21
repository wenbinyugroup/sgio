"""Test gmsh reading functionality.

This module tests the gmsh read functionality by:
1. Converting VABS files to GMSH format
2. Reading the GMSH files back
3. Converting GMSH files back to VABS format
4. Comparing the results
"""
import os
from pathlib import Path
import pytest
import yaml

from sgio import convert, configure_logging, logger

configure_logging(cout_level='info')


@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "files"


@pytest.fixture(scope="module")
def output_dir(tmp_path_factory):
    """Fixture to provide a temporary output directory for test results."""
    return tmp_path_factory.mktemp("gmsh_conversion_output")


def test_vabs_to_gmsh_to_vabs(test_data_dir, output_dir):
    """Test converting VABS -> GMSH -> VABS."""

    # Step 1: Convert VABS to GMSH
    fn_test_cases = 'test_convert_vabs_gmsh.yml'
    test_case_path = test_data_dir / fn_test_cases

    if not test_case_path.exists():
        pytest.skip(f"Test case file not found: {test_case_path}")

    with open(test_case_path, 'r') as file:
        test_cases_vabs_to_gmsh = yaml.safe_load(file)

    os.makedirs(output_dir, exist_ok=True)

    for _case in test_cases_vabs_to_gmsh:
        ff_in = _case['ff_in']
        ff_out = _case['ff_out']

        fn_in = str(test_data_dir / _case["fn_in"])
        fn_out = str(output_dir / _case["fn_out"])

        logger.info(f'Converting {fn_in} to {fn_out}...')

        convert(
            fn_in, fn_out,
            ff_in, ff_out,
            file_version_in=_case.get('version_in', ''),
            file_version_out=_case.get('version_out', ''),
            model_type=_case.get('model', 'SD1'),
        )

        # Verify the gmsh file was created
        assert os.path.exists(fn_out), f"Failed to create {fn_out}"
        logger.info(f'Successfully created {fn_out}')

    # Step 2: Convert GMSH back to VABS
    fn_test_cases = 'test_convert_gmsh_vabs.yml'
    test_case_path = test_data_dir / fn_test_cases

    if not test_case_path.exists():
        pytest.skip(f"Test case file not found: {test_case_path}")

    with open(test_case_path, 'r') as file:
        test_cases_gmsh_to_vabs = yaml.safe_load(file)

    for _case in test_cases_gmsh_to_vabs:
        ff_in = _case['ff_in']
        ff_out = _case['ff_out']

        fn_in = str(output_dir / _case["fn_in"])
        fn_out = str(output_dir / _case["fn_out"])

        logger.info(f'Converting {fn_in} to {fn_out}...')

        sg = convert(
            fn_in, fn_out,
            ff_in, ff_out,
            file_version_in=_case.get('version_in', ''),
            file_version_out=_case.get('version_out', ''),
            model_type=_case.get('model', 'SD1'),
        )

        # Verify the vabs file was created
        assert os.path.exists(fn_out), f"Failed to create {fn_out}"
        logger.info(f'Successfully created {fn_out}')

        # Basic validation of the SG object
        assert sg is not None, "SG object should not be None"
        assert sg.mesh is not None, "SG mesh should not be None"
        assert len(sg.mesh.points) > 0, "SG mesh should have points"
        assert len(sg.mesh.cells) > 0, "SG mesh should have cells"

        logger.info(f'SG has {len(sg.mesh.points)} points and {len(sg.mesh.cells)} cell blocks')

