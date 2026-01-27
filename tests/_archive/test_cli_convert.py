"""Test CLI conversion functionality using subprocess."""
import logging
import os
import subprocess as sbp
import sys
from pathlib import Path
import pytest
import yaml


@pytest.fixture(scope="module")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "files"


@pytest.fixture(scope="module")
def output_dir(tmp_path_factory):
    """Fixture to provide a temporary output directory for test results."""
    return tmp_path_factory.mktemp("cli_conversion_output")


@pytest.fixture(scope="module")
def test_case_files():
    """Fixture providing list of test case files."""
    return [
        'test_convert_vabs_abaqus.yml',
        'test_convert_vabs_gmsh.yml',
        'test_convert_sc_abaqus.yml',
    ]


@pytest.mark.parametrize("fn_test_cases", [
    'test_convert_vabs_abaqus.yml',
    'test_convert_vabs_gmsh.yml',
    'test_convert_sc_abaqus.yml',
])
def test_cli_convert(fn_test_cases, test_data_dir, output_dir, capsys):
    """Test CLI conversion for each test case file.

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

            logging.info(f'Converting {fn_in} to {fn_out}...')

            cmd = [
                sys.executable, '-m', 'sgio', 'convert',
                fn_in,
                fn_out,
                '-ff', ff_in,
                '-tf', ff_out,
            ]

            logging.info(' '.join(cmd))

            if 'version_in' in _case:
                cmd.append('-ffv')
                cmd.append(_case['version_in'])

            if 'version_out' in _case:
                cmd.append('-tfv')
                cmd.append(_case['version_out'])

            if 'model' in _case:
                cmd.append('-m')
                cmd.append(_case['model'])

            result = sbp.run(cmd, check=True, capture_output=False, text=True)

            # Verify output file was created
            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"

