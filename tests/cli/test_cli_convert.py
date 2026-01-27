"""Test CLI conversion functionality using subprocess."""
import logging
import os
import subprocess as sbp
import sys
from pathlib import Path
import pytest
import yaml


@pytest.mark.cli
@pytest.mark.parametrize("fn_test_cases", [
    'test_convert_vabs_abaqus.yml',
    'test_convert_vabs_gmsh.yml',
    'test_convert_sc_abaqus.yml',
])
def test_cli_convert(fn_test_cases, test_data_dir, tmp_path, capsys):
    """Test CLI conversion for each test case file.

    This test verifies:
    1. CLI convert command executes successfully
    2. Output files are created
    3. Conversion works for multiple format combinations

    Args:
        fn_test_cases: Name of YAML test case file
        test_data_dir: Fixture providing test data directory
        tmp_path: Pytest fixture for temporary directory
        capsys: Pytest fixture for output capture

    Note:
        Uses capsys.disabled() to allow vendor code (inprw) to write to stdout.
    """
    # Disable output capture to allow vendor code to write to stdout
    with capsys.disabled():
        # Look for test case file in yaml subdirectory first, then root fixtures, then legacy
        test_case_path = test_data_dir / "yaml" / fn_test_cases
        if not test_case_path.exists():
            test_case_path = test_data_dir / fn_test_cases
        if not test_case_path.exists():
            # Try legacy location
            legacy_path = Path(__file__).parent.parent / "files" / fn_test_cases
            if legacy_path.exists():
                test_case_path = legacy_path
            else:
                pytest.skip(f"Test case file not found: {fn_test_cases}")

        with open(test_case_path, 'r') as file:
            test_cases = yaml.safe_load(file)

        # Create output directory
        output_dir = tmp_path / "cli_conversion_output"
        os.makedirs(output_dir, exist_ok=True)

        for _i, _case in enumerate(test_cases):
            ff_in = _case['ff_in']
            ff_out = _case['ff_out']

            # Resolve input file path
            fn_in_rel = _case["fn_in"]
            fn_in = str(test_data_dir / fn_in_rel)
            if not Path(fn_in).exists():
                # Try legacy location
                fn_in = str(Path(__file__).parent.parent / "files" / fn_in_rel)
            
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


@pytest.mark.cli
def test_cli_convert_help():
    """Test that CLI convert help command works."""
    cmd = [sys.executable, '-m', 'sgio', 'convert', '--help']
    result = sbp.run(cmd, check=True, capture_output=True, text=True)
    assert result.returncode == 0
    assert 'convert' in result.stdout.lower()


@pytest.mark.cli
def test_cli_convert_invalid_format():
    """Test that CLI convert rejects invalid format."""
    cmd = [
        sys.executable, '-m', 'sgio', 'convert',
        'dummy.txt', 'output.txt',
        '-ff', 'invalid_format',
        '-tf', 'vabs'
    ]
    result = sbp.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0  # Should fail

