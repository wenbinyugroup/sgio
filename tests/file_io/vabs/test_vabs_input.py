"""Test module for VABS input file reading and format conversion.

This module tests:
1. VABS input file reading
2. VABS format conversion (v4.0 <-> v4.1)
3. VABS file validation
"""

import pytest
from pathlib import Path

from sgio import convert, run, logger


@pytest.mark.io
@pytest.mark.vabs
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
])
def test_vabs_format_conversion(case, test_data_dir, temp_dir):
    """Test VABS format conversion for a specific test case.
    
    This test verifies that:
    1. VABS files can be read correctly
    2. VABS files can be converted between versions
    3. Output files are created and non-empty
    
    Args:
        case: Test case dictionary with conversion parameters
        test_data_dir: Fixture providing test data directory
        temp_dir: Fixture providing temporary output directory
    """
    # Extract test case parameters
    ff_in = case['ff_in']
    ff_out = case['ff_out']

    fn_in = test_data_dir / case["fn_in"]
    fn_out = temp_dir / case["fn_out"]

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
    
    logger.info(f'Successfully converted {fn_in} to {fn_out}')


@pytest.mark.io
@pytest.mark.vabs
def test_vabs_format_conversion_multiple_cases(test_data_dir, temp_dir):
    """Test VABS format conversion for multiple test cases.
    
    This test verifies that multiple VABS files can be converted
    in sequence without errors.
    """
    test_cases = [
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
    ]
    
    for case_index, case in enumerate(test_cases):
        # Extract test case parameters
        ff_in = case['ff_in']
        ff_out = case['ff_out']

        fn_in = test_data_dir / case["fn_in"]
        fn_out = temp_dir / f"{case_index}_{case['fn_out']}"  # Add index to avoid conflicts

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


@pytest.mark.io
@pytest.mark.vabs
@pytest.mark.requires_solver
@pytest.mark.slow
def test_vabs_solver_execution(test_data_dir, temp_dir):
    """Test VABS solver execution.
    
    This test verifies that the VABS solver can be executed on
    converted files. Requires VABS to be installed.
    
    Note: This test is marked as 'requires_solver' and 'slow' and
    will be skipped unless explicitly requested.
    """
    test_cases = [
        {
            'fn_in': 'vabs/version_4_1/3cells.sg',
            'ff_in': 'vabs',
            'version_in': '4.1',
            'fn_out': '3cells.sg',
            'ff_out': 'vabs',
            'version_out': '4.1',
            'format_flag_out': 1,
            'model': 'BM2',
            'solver': 'vabs',
        },
    ]
    
    for case_index, case in enumerate(test_cases):
        solver = case.get('solver', None)

        if not solver:
            continue  # Skip cases without solver

        # First ensure the conversion was done
        fn_out = temp_dir / f"{case_index}_{case['fn_out']}"

        if not fn_out.exists():
            # Run conversion first
            ff_in = case['ff_in']
            ff_out = case['ff_out']
            fn_in = test_data_dir / case["fn_in"]

            convert(
                str(fn_in), str(fn_out),
                ff_in, ff_out,
                file_version_in=case.get('version_in', None),
                file_version_out=case.get('version_out', None),
                model_type=case.get('model', None),
                vabs_format_version=case.get('format_flag_out', 1),
            )

        logger.info(f'Running solver {solver} on {fn_out}...')

        # Run the solver
        run(solver, str(fn_out), analysis='h', smdim=case.get('model', None))

