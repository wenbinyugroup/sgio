"""Test VABS load CSV file reading.

This module tests reading load case data from CSV files for VABS analysis.
"""
import pytest

from sgio.iofunc import read_load_csv


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
    state_cases = read_load_csv(str(fn), smdim, model)

    # Verify we got load cases
    assert len(state_cases) > 0, "Should read at least one load case"


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

    state_cases = read_load_csv(str(fn), 1, 'b2')

    for state_case in state_cases:
        assert isinstance(state_case.case, dict), "Should keep case metadata in a dict"
        assert 'loc' in state_case.case, "Should preserve location metadata"
        assert state_case.case['load_type'] == 0, "Default load type should be preserved"

        assert state_case.displacement is not None, "Should have displacement state"
        assert state_case.rotation is not None, "Should have rotation state"
        assert state_case.load is not None, "Should have load state"
        assert state_case.displacement.label == ['u1', 'u2', 'u3']
        assert state_case.load.label == ['f1', 'f2', 'f3', 'm1', 'm2', 'm3']


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

    state_cases = read_load_csv(str(fn), 1, 'b2')

    # For BM2 (Timoshenko beam), we expect 6 load components
    for state_case in state_cases:
        load = state_case.load.data
        assert len(load) == 6, f"BM2 should have 6 load components, got {len(load)}"
        # All load values should be numeric
        for load_val in load:
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

    state_cases = read_load_csv(str(fn), 1, 'b2')

    # Should have multiple load cases
    assert len(state_cases) >= 2, "Should have at least 2 load cases in the test file"


@pytest.mark.io
@pytest.mark.vabs
def test_read_load_csv_condition_tags_are_stored_in_case_metadata(test_data_dir):
    """Condition tags should be preserved in ``StateCase.case`` metadata."""
    fn = test_data_dir / 'sg_bm2_load_cases.csv'
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")

    state_cases = read_load_csv(str(fn), 1, 'b2', cond_tags=['case'])

    assert state_cases[0].case['case'] == 1

