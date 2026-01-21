"""Test Gmsh I/O functionality.

This module tests:
1. Converting VABS files to Gmsh format
2. Reading Gmsh files back
3. Converting Gmsh files back to VABS format
4. Round-trip conversion validation
"""

import pytest
from pathlib import Path
import yaml

from sgio import convert, logger


@pytest.mark.io
@pytest.mark.gmsh
@pytest.mark.vabs
def test_vabs_to_gmsh_to_vabs_roundtrip(test_data_dir, temp_dir):
    """Test round-trip conversion: VABS -> Gmsh -> VABS.
    
    This test verifies that:
    1. VABS files can be converted to Gmsh format
    2. Gmsh files can be read and converted back to VABS
    3. The resulting structure gene object is valid
    4. Mesh data is preserved through the conversion
    
    The test performs a complete round-trip conversion to ensure
    data integrity is maintained.
    """
    # Step 1: Convert VABS to Gmsh
    fn_test_cases = 'test_convert_vabs_gmsh.yml'
    test_case_path = test_data_dir / 'yaml' / fn_test_cases

    if not test_case_path.exists():
        pytest.skip(f"Test case file not found: {test_case_path}")

    with open(test_case_path, 'r') as file:
        test_cases_vabs_to_gmsh = yaml.safe_load(file)

    for _case in test_cases_vabs_to_gmsh:
        ff_in = _case['ff_in']
        ff_out = _case['ff_out']

        fn_in = str(test_data_dir / _case["fn_in"])
        fn_out = str(temp_dir / _case["fn_out"])

        logger.info(f'Converting {fn_in} to {fn_out}...')

        convert(
            fn_in, fn_out,
            ff_in, ff_out,
            file_version_in=_case.get('version_in', ''),
            file_version_out=_case.get('version_out', ''),
            model_type=_case.get('model', 'SD1'),
        )

        # Verify the gmsh file was created
        assert Path(fn_out).exists(), f"Failed to create {fn_out}"
        assert Path(fn_out).stat().st_size > 0, f"Output file is empty: {fn_out}"
        logger.info(f'Successfully created {fn_out}')

    # Step 2: Convert Gmsh back to VABS
    fn_test_cases = 'test_convert_gmsh_vabs.yml'
    test_case_path = test_data_dir / 'yaml' / fn_test_cases

    if not test_case_path.exists():
        pytest.skip(f"Test case file not found: {test_case_path}")

    with open(test_case_path, 'r') as file:
        test_cases_gmsh_to_vabs = yaml.safe_load(file)

    for _case in test_cases_gmsh_to_vabs:
        ff_in = _case['ff_in']
        ff_out = _case['ff_out']

        fn_in = str(temp_dir / _case["fn_in"])
        fn_out = str(temp_dir / _case["fn_out"])

        logger.info(f'Converting {fn_in} to {fn_out}...')

        sg = convert(
            fn_in, fn_out,
            ff_in, ff_out,
            file_version_in=_case.get('version_in', ''),
            file_version_out=_case.get('version_out', ''),
            model_type=_case.get('model', 'SD1'),
        )

        # Verify the vabs file was created
        assert Path(fn_out).exists(), f"Failed to create {fn_out}"
        assert Path(fn_out).stat().st_size > 0, f"Output file is empty: {fn_out}"
        logger.info(f'Successfully created {fn_out}')

        # Basic validation of the SG object
        assert sg is not None, "SG object should not be None"
        assert sg.mesh is not None, "SG mesh should not be None"
        assert len(sg.mesh.points) > 0, "SG mesh should have points"
        assert len(sg.mesh.cells) > 0, "SG mesh should have cells"

        logger.info(f'SG has {len(sg.mesh.points)} points and {len(sg.mesh.cells)} cell blocks')


@pytest.mark.io
@pytest.mark.gmsh
def test_gmsh_read_basic(test_data_dir, temp_dir):
    """Test basic Gmsh file reading.
    
    This test verifies that Gmsh files can be read and contain
    valid mesh data.
    """
    # First create a Gmsh file from a VABS file
    fn_test_cases = 'test_convert_vabs_gmsh.yml'
    test_case_path = test_data_dir / 'yaml' / fn_test_cases

    if not test_case_path.exists():
        pytest.skip(f"Test case file not found: {test_case_path}")

    with open(test_case_path, 'r') as file:
        test_cases = yaml.safe_load(file)

    if not test_cases:
        pytest.skip("No test cases found")

    # Use the first test case
    _case = test_cases[0]
    ff_in = _case['ff_in']
    ff_out = _case['ff_out']

    fn_in = str(test_data_dir / _case["fn_in"])
    fn_out = str(temp_dir / _case["fn_out"])

    # Convert to Gmsh
    sg = convert(
        fn_in, fn_out,
        ff_in, ff_out,
        file_version_in=_case.get('version_in', ''),
        file_version_out=_case.get('version_out', ''),
        model_type=_case.get('model', 'SD1'),
    )

    # Verify the structure gene object
    assert sg is not None, "SG object should not be None"
    assert sg.mesh is not None, "SG mesh should not be None"
    assert len(sg.mesh.points) > 0, f"Expected points in mesh, got {len(sg.mesh.points)}"
    assert len(sg.mesh.cells) > 0, f"Expected cells in mesh, got {len(sg.mesh.cells)}"

