"""Test file format conversion functionality."""
import os
from pathlib import Path
import pytest
import yaml

from sgio import convert, run, configure_logging, logger

configure_logging(cout_level='info')


@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "files"


@pytest.fixture(scope="module")
def output_dir(tmp_path_factory):
    """Fixture to provide a temporary output directory for test results."""
    return tmp_path_factory.mktemp("conversion_output")


@pytest.mark.parametrize("fn_test_cases", [
    'test_convert_vabs_abaqus.yml',
    'test_convert_vabs_gmsh.yml',
    'test_convert_sc_abaqus.yml',
])
def test_file_format_conversion(fn_test_cases, test_data_dir, output_dir, capsys):
    """Test file format conversion for each test case file.

    Note: Uses capsys.disabled() to allow vendor code (inprw) to write to stdout.
    """
    # Disable pytest's output capture to allow vendor code to write to stdout
    with capsys.disabled():
        test_case_path = test_data_dir / fn_test_cases

        if not test_case_path.exists():
            pytest.skip(f"Test case file not found: {test_case_path}")

        with open(test_case_path, 'r') as file:
            test_cases = yaml.safe_load(file)

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        for _i, _case in enumerate(test_cases):
            ff_in = _case['ff_in']
            ff_out = _case['ff_out']

            fn_in = str(test_data_dir / _case["fn_in"])
            fn_out = str(output_dir / _case["fn_out"])

            logger.info(f'Converting {fn_in} to {fn_out}...')

            convert(
                fn_in, fn_out,
                ff_in, ff_out,
                file_version_in=_case.get('version_in', None),
                file_version_out=_case.get('version_out', None),
                model_type=_case.get('model', None),
            )

            # Verify output file was created
            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"
            assert os.path.getsize(fn_out) > 0, f"Output file is empty: {fn_out}"

            # Optionally run solver if specified
            _solver = _case.get('solver', None)
            if _solver:
                pytest.skip(f"Solver execution skipped for {_solver} (requires external tool)")

