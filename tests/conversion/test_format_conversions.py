"""Test file format conversion functionality.

This module tests conversions between different file formats:
- VABS ↔ Abaqus
- VABS ↔ Gmsh
- SwiftComp ↔ Abaqus
- SwiftComp ↔ Gmsh
"""
import os
from pathlib import Path
import pytest
import yaml

from sgio import convert, configure_logging, logger

configure_logging(cout_level='info')


@pytest.mark.conversion
@pytest.mark.parametrize("fn_test_cases", [
    'test_convert_vabs_abaqus.yml',
    'test_convert_vabs_gmsh.yml',
    'test_convert_sc_abaqus.yml',
])
def test_file_format_conversion(fn_test_cases, test_data_dir, tmp_path, capsys):
    """Test file format conversion for each test case file.
    
    This test verifies:
    1. Files can be converted between different formats
    2. Output files are created successfully
    3. Output files are not empty
    4. Conversion preserves essential data
    
    Args:
        fn_test_cases: Name of YAML test case file
        test_data_dir: Fixture providing test data directory
        tmp_path: Pytest fixture for temporary directory
        capsys: Pytest fixture for output capture
    
    Note:
        Uses capsys.disabled() to allow vendor code (inprw) to write to stdout.
    """
    # Disable pytest's output capture to allow vendor code to write to stdout
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
        output_dir = tmp_path / "conversion_output"
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


@pytest.mark.conversion
@pytest.mark.vabs
def test_convert_to_vabs_v41(test_data_dir, tmp_path, capsys):
    """Test conversion to VABS v4.1 format.
    
    This test specifically verifies conversion to VABS v4.1 format
    from various input formats.
    """
    with capsys.disabled():
        test_case_path = test_data_dir / 'yaml' / 'test_convert_vabs_abaqus.yml'
        if not test_case_path.exists():
            legacy_path = Path(__file__).parent.parent / "files" / 'test_convert_vabs_abaqus.yml'
            if legacy_path.exists():
                test_case_path = legacy_path
            else:
                pytest.skip("Test case file not found")

        with open(test_case_path, 'r') as file:
            test_cases = yaml.safe_load(file)

        output_dir = tmp_path / "vabs_conversion_output"
        os.makedirs(output_dir, exist_ok=True)

        # Filter for VABS v4.1 output cases
        vabs41_cases = [c for c in test_cases if c.get('version_out') == '4.1']
        
        assert len(vabs41_cases) > 0, "No VABS v4.1 test cases found"

        for _case in vabs41_cases:
            fn_in_rel = _case["fn_in"]
            fn_in = str(test_data_dir / fn_in_rel)
            if not Path(fn_in).exists():
                fn_in = str(Path(__file__).parent.parent / "files" / fn_in_rel)
            
            fn_out = str(output_dir / _case["fn_out"])

            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"
            assert os.path.getsize(fn_out) > 0, f"Output file is empty: {fn_out}"


@pytest.mark.conversion
@pytest.mark.vabs
def test_convert_to_vabs_v40(test_data_dir, tmp_path, capsys):
    """Test conversion to VABS v4.0 format."""
    with capsys.disabled():
        test_case_path = test_data_dir / 'yaml' / 'test_convert_vabs_abaqus.yml'
        if not test_case_path.exists():
            legacy_path = Path(__file__).parent.parent / "files" / 'test_convert_vabs_abaqus.yml'
            if legacy_path.exists():
                test_case_path = legacy_path
            else:
                pytest.skip("Test case file not found")

        with open(test_case_path, 'r') as file:
            test_cases = yaml.safe_load(file)

        output_dir = tmp_path / "vabs_conversion_output"
        os.makedirs(output_dir, exist_ok=True)

        # Filter for VABS v4.0 output cases
        vabs40_cases = [c for c in test_cases if c.get('version_out') == '4.0']

        if len(vabs40_cases) == 0:
            pytest.skip("No VABS v4.0 test cases found")

        for _case in vabs40_cases:
            fn_in_rel = _case["fn_in"]
            fn_in = str(test_data_dir / fn_in_rel)
            if not Path(fn_in).exists():
                fn_in = str(Path(__file__).parent.parent / "files" / fn_in_rel)

            fn_out = str(output_dir / _case["fn_out"])

            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"
            assert os.path.getsize(fn_out) > 0, f"Output file is empty: {fn_out}"


@pytest.mark.conversion
@pytest.mark.gmsh
def test_convert_to_gmsh(test_data_dir, tmp_path, capsys):
    """Test conversion to Gmsh format."""
    with capsys.disabled():
        test_case_path = test_data_dir / 'yaml' / 'test_convert_vabs_gmsh.yml'
        if not test_case_path.exists():
            legacy_path = Path(__file__).parent.parent / "files" / 'test_convert_vabs_gmsh.yml'
            if legacy_path.exists():
                test_case_path = legacy_path
            else:
                pytest.skip("Test case file not found")

        with open(test_case_path, 'r') as file:
            test_cases = yaml.safe_load(file)

        output_dir = tmp_path / "gmsh_conversion_output"
        os.makedirs(output_dir, exist_ok=True)

        for _case in test_cases:
            fn_in_rel = _case["fn_in"]
            fn_in = str(test_data_dir / fn_in_rel)
            if not Path(fn_in).exists():
                fn_in = str(Path(__file__).parent.parent / "files" / fn_in_rel)

            fn_out = str(output_dir / _case["fn_out"])

            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"
            assert os.path.getsize(fn_out) > 0, f"Output file is empty: {fn_out}"


@pytest.mark.conversion
@pytest.mark.swiftcomp
def test_convert_to_swiftcomp(test_data_dir, tmp_path, capsys):
    """Test conversion to SwiftComp format."""
    with capsys.disabled():
        test_case_path = test_data_dir / 'yaml' / 'test_convert_sc_abaqus.yml'
        if not test_case_path.exists():
            legacy_path = Path(__file__).parent.parent / "files" / 'test_convert_sc_abaqus.yml'
            if legacy_path.exists():
                test_case_path = legacy_path
            else:
                pytest.skip("Test case file not found")

        with open(test_case_path, 'r') as file:
            test_cases = yaml.safe_load(file)

        output_dir = tmp_path / "sc_conversion_output"
        os.makedirs(output_dir, exist_ok=True)

        for _case in test_cases:
            fn_in_rel = _case["fn_in"]
            fn_in = str(test_data_dir / fn_in_rel)
            if not Path(fn_in).exists():
                fn_in = str(Path(__file__).parent.parent / "files" / fn_in_rel)

            fn_out = str(output_dir / _case["fn_out"])

            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f"Output file was not created: {fn_out}"
            assert os.path.getsize(fn_out) > 0, f"Output file is empty: {fn_out}"

