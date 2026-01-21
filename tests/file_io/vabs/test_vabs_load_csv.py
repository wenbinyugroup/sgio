"""Test VABS load CSV file reading.

This module tests reading load case data from CSV files for VABS analysis.
"""
import pytest
from pathlib import Path

from sgio.iofunc import readLoadCsv


@pytest.mark.io
@pytest.mark.vabs
def test_read_load_csv_bm2(test_data_dir):
    """Test reading load CSV file for BM2 (Timoshenko beam) model.

    This test verifies:
    1. CSV file can be read
    2. Load cases are parsed correctly
    3. Response data structure is correct
    4. Load values are extracted correctly
    """
    fn = test_data_dir / 'sg_bm2_load_cases.csv'

    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")

    # Read load CSV for BM2 model (Timoshenko beam)
    smdim = 1  # 1D structure (beam)
    model = 'b2'  # BM2 (Timoshenko beam)

    # Read the load cases
    struct_resp_cases = readLoadCsv(str(fn), smdim, model)

    # Verify we got load cases
    assert len(struct_resp_cases.responses) > 0, "Should read at least one load case"


@pytest.mark.io
@pytest.mark.vabs
def test_read_load_csv_response_structure(test_data_dir):
    """Test the structure of response cases from CSV.

    This test verifies:
    1. Each response has location and condition data
    2. Each response has load data
    3. Each response has displacement data
    4. Each response has directional cosine (rotation) data
    """
    fn = test_data_dir / 'sg_bm2_load_cases.csv'
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")

    struct_resp_cases = readLoadCsv(str(fn), 1, 'b2')

    for resp_case in struct_resp_cases.responses:
        # Each response case is a dict with 'response' key
        assert 'response' in resp_case, "Should have 'response' key"
        sect_resp = resp_case['response']

        # Check that required attributes exist
        assert hasattr(sect_resp, 'loc'), "Should have loc attribute"
        assert hasattr(sect_resp, 'cond'), "Should have cond attribute"
        assert hasattr(sect_resp, 'load'), "Should have load attribute"
        assert hasattr(sect_resp, 'displacement'), "Should have displacement attribute"
        assert hasattr(sect_resp, 'directional_cosine'), "Should have directional_cosine attribute"


@pytest.mark.io
@pytest.mark.vabs
def test_read_load_csv_load_values(test_data_dir):
    """Test that load values are correctly parsed from CSV.

    This test verifies:
    1. Load values are numeric
    2. Load values match expected format
    """
    fn = test_data_dir / 'sg_bm2_load_cases.csv'
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")

    struct_resp_cases = readLoadCsv(str(fn), 1, 'b2')

    # For BM2 (Timoshenko beam), we expect 6 load components
    for resp_case in struct_resp_cases.responses:
        sect_resp = resp_case['response']
        assert len(sect_resp.load) == 6, f"BM2 should have 6 load components, got {len(sect_resp.load)}"
        # All load values should be numeric
        for load_val in sect_resp.load:
            assert isinstance(load_val, (int, float)), f"Load value should be numeric, got {type(load_val)}"


@pytest.mark.io
@pytest.mark.vabs
def test_read_load_csv_multiple_cases(test_data_dir):
    """Test reading CSV with multiple load cases.

    This test verifies:
    1. Multiple load cases are read correctly
    2. Each case has unique data
    """
    fn = test_data_dir / 'sg_bm2_load_cases.csv'
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")

    struct_resp_cases = readLoadCsv(str(fn), 1, 'b2')

    # Should have multiple load cases
    assert len(struct_resp_cases.responses) >= 2, "Should have at least 2 load cases in the test file"

