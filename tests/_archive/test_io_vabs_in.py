"""Test module for VABS input/output format conversion."""

import pytest
from pathlib import Path
from typing import List, Dict, Any

from sgio import convert, run, logger, configure_logging


# Configure logging for tests
configure_logging(cout_level='info')


@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "files"


@pytest.fixture(scope="module")
def output_dir(tmp_path_factory):
    """Fixture to provide a temporary output directory for test results."""
    return tmp_path_factory.mktemp("vabs_conversion_output")


@pytest.fixture(scope="module")
def vabs_format_test_cases() -> List[Dict[str, Any]]:
    """Fixture providing VABS format conversion test cases."""
    return [
        {
            'fn_in': 'vabs/version_4_1/3cells.sg',
            'ff_in': 'vabs',
            'version_in': '4.1',
            'fn_out': '3cells.sg',
            'ff_out': 'vabs',
            'version_out': '4.1',
            'format_flag_out': 1,
            'model': 'BM2',
            # 'solver': 'vabs',  # Uncomment if solver testing is needed
        },
        # Add more test cases here as needed
        # {
        #     'fn_in': 'vabs/version_4_0/another_file.sg',
        #     'ff_in': 'vabs',
        #     'version_in': '4.0',
        #     'fn_out': 'another_file_converted.sg',
        #     'ff_out': 'vabs',
        #     'version_out': '4.1',
        #     'format_flag_out': 1,
        #     'model': 'BM1',
        # },
    ]


@pytest.mark.parametrize("case", [
    {
        'fn_in': 'vabs/version_4_1/3cells.sg',
        'ff_in': 'vabs',
        'version_in': '4.1',
        'fn_out': '3cells.sg',
        'ff_out': 'vabs',
        'version_out': '4.1',
        'format_flag_out': 1,
        'model': 'BM2',
    },
    # Add more test cases here as needed
])
def test_vabs_format_conversion_parametrized(case, test_data_dir, output_dir):
    """Test VABS format conversion for a specific test case."""
    # Extract test case parameters
    ff_in = case['ff_in']
    ff_out = case['ff_out']

    fn_in = test_data_dir / case["fn_in"]
    fn_out = output_dir / case["fn_out"]

    # Ensure input file exists
    if not fn_in.exists():
        pytest.skip(f"Input file not found: {fn_in}")

    logger.info(f'Converting {fn_in} to {fn_out}...')

    # Perform the conversion
    convert(
        str(fn_in), str(fn_out),
        ff_in, ff_out,
        file_version_in=case.get('version_in', None),
        file_version_out=case.get('version_out', None),
        model_type=case.get('model', None),
        vabs_format_version=case.get('format_flag_out', 1),
    )

    # Verify output file was created
    assert fn_out.exists(), f"Output file was not created: {fn_out}"
    assert fn_out.stat().st_size > 0, f"Output file is empty: {fn_out}"


def test_vabs_format_conversion_from_fixture(vabs_format_test_cases, test_data_dir, output_dir):
    """Test VABS format conversion for all test cases from fixture."""
    for case_index, case in enumerate(vabs_format_test_cases):
        # Extract test case parameters
        ff_in = case['ff_in']
        ff_out = case['ff_out']

        fn_in = test_data_dir / case["fn_in"]
        fn_out = output_dir / f"{case_index}_{case['fn_out']}"  # Add index to avoid conflicts

        # Ensure input file exists
        if not fn_in.exists():
            pytest.skip(f"Input file not found: {fn_in}")

        logger.info(f'Converting {fn_in} to {fn_out}...')

        # Perform the conversion
        convert(
            str(fn_in), str(fn_out),
            ff_in, ff_out,
            file_version_in=case.get('version_in', None),
            file_version_out=case.get('version_out', None),
            model_type=case.get('model', None),
            vabs_format_version=case.get('format_flag_out', 1),
        )

        # Verify output file was created
        assert fn_out.exists(), f"Output file was not created: {fn_out}"
        assert fn_out.stat().st_size > 0, f"Output file is empty: {fn_out}"


def test_vabs_solver_execution(vabs_format_test_cases, test_data_dir, output_dir):
    """Test VABS solver execution for test cases that specify a solver."""
    for case_index, case in enumerate(vabs_format_test_cases):
        solver = case.get('solver', None)

        if not solver:
            continue  # Skip cases without solver instead of failing the whole test

        # First ensure the conversion was done
        fn_out = output_dir / f"{case_index}_{case['fn_out']}"
        if not fn_out.exists():
            # Run conversion first
            test_vabs_format_conversion_from_fixture(vabs_format_test_cases, test_data_dir, output_dir)

        logger.info(f'Running solver {solver} on {fn_out}...')

        # Run the solver
        run(solver, str(fn_out), analysis='h', smdim=case.get('model', None))


def test_vabs_format_test_cases_structure(vabs_format_test_cases):
    """Test that the test cases fixture has the expected structure."""
    assert isinstance(vabs_format_test_cases, list), "Test cases should be a list"
    assert len(vabs_format_test_cases) > 0, "Test cases list should not be empty"

    # Check required fields in each test case
    required_fields = ['fn_in', 'ff_in', 'fn_out', 'ff_out']
    for i, case in enumerate(vabs_format_test_cases):
        assert isinstance(case, dict), f"Test case {i} should be a dictionary"
        for field in required_fields:
            assert field in case, f"Test case {i} missing required field: {field}"



