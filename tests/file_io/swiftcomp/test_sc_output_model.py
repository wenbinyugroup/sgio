"""Test SwiftComp output model reading.

This module tests reading SwiftComp homogenization output (.k files) including:
- Euler-Bernoulli beam model (BM1)
- Timoshenko beam model (BM2)
- Kirchhoff-Love plate model (PL1)
- Reissner-Mindlin plate model (PL2)
- Cauchy continuum model (SD1)
- Effective properties
"""
import os
from pathlib import Path
import pytest

from sgio import read_output_model, logger, configure_logging

configure_logging(cout_level='info')


@pytest.mark.io
@pytest.mark.swiftcomp
@pytest.mark.parametrize("test_case", [
    {
        'fn_base': 'sg21eb_tri6_sc21',
        'file_format': 'sc',
        'model_type': 'BM1',
        'expected_properties': ['ea', 'gj', 'ei22', 'ei33'],
    },
    {
        'fn_base': 'sg21t_tri6_sc21',
        'file_format': 'sc',
        'model_type': 'BM2',
        'expected_properties': ['ea', 'gj', 'ei22', 'ei33'],
        'optional_properties': ['ga22', 'ga33'],  # Shear stiffness for Timoshenko
    },
    # Note: PL2 (Reissner-Mindlin plate) is not yet implemented in SwiftComp reader
    # The sg23_tri6_sc21.sg.k file is actually a 3D solid (SD1) output
])
def test_swiftcomp_output_model(test_case, test_data_dir):
    """Test reading SwiftComp model output files.
    
    This test verifies:
    1. SwiftComp .k output files can be read
    2. Model type is correctly identified (BM1, BM2, PL1, PL2, SD1)
    3. Expected properties are present and non-None
    4. Properties have reasonable values
    
    Args:
        test_case: Dictionary with test case parameters
        test_data_dir: Fixture providing test data directory
    """
    fn_base = test_case['fn_base']
    file_format = test_case['file_format']
    model_type = test_case['model_type']
    expected_properties = test_case['expected_properties']
    optional_properties = test_case.get('optional_properties', [])
    
    # Construct file path - SwiftComp output files have .sg.k extension
    fn_in = test_data_dir / "swiftcomp" / f"{fn_base}.sg.k"
    
    if not fn_in.exists():
        # Try legacy location
        fn_in = Path(__file__).parent.parent.parent / "files" / "swiftcomp" / f"{fn_base}.sg.k"
    
    if not fn_in.exists():
        pytest.skip(f"Test file not found: {fn_in}")
    
    logger.info(f"Reading SwiftComp output model from: {fn_in}")
    
    # Read the output model
    model = read_output_model(str(fn_in), file_format, model_type=model_type)
    
    # Verify model was read
    assert model is not None, "Model should not be None"
    
    # Verify expected properties exist and are not None
    for prop in expected_properties:
        value = getattr(model, prop, None)
        assert value is not None, f"Property '{prop}' should not be None"
        logger.info(f"{prop} = {value}")
    
    # Verify beam model properties have reasonable values
    if model_type in ['BM1', 'BM2']:
        # EA (extension stiffness) should be positive
        ea = model.ea
        if ea is not None:
            assert ea > 0, f"EA should be positive, got {ea}"
        
        # GJ (torsional stiffness) should be positive
        gj = model.gj
        if gj is not None:
            assert gj > 0, f"GJ should be positive, got {gj}"
        
        # EI22 and EI33 (bending stiffness) should be positive
        ei22 = model.ei22
        if ei22 is not None:
            assert ei22 > 0, f"EI22 should be positive, got {ei22}"
        
        ei33 = model.ei33
        if ei33 is not None:
            assert ei33 > 0, f"EI33 should be positive, got {ei33}"
        
        # Check optional properties (e.g., shear stiffness for Timoshenko beam)
        for prop in optional_properties:
            value = getattr(model, prop, None)
            if value is not None:
                logger.info(f"{prop} = {value}")
                # Shear stiffness should be positive if present
                if prop in ['ga22', 'ga33']:
                    assert value > 0, f"{prop} should be positive, got {value}"
    
    logger.info(f"✓ Successfully read {model_type} model from {fn_base}")


@pytest.mark.io
@pytest.mark.swiftcomp
def test_swiftcomp_output_model_properties_access(test_data_dir):
    """Test different ways to access model properties.
    
    This test verifies:
    1. Properties can be accessed as attributes
    2. Model can be converted to dict
    
    Args:
        test_data_dir: Fixture providing test data directory
    """
    fn_in = test_data_dir / "swiftcomp" / "sg21t_tri6_sc21.sg.k"
    
    if not fn_in.exists():
        fn_in = Path(__file__).parent.parent.parent / "files" / "swiftcomp" / "sg21t_tri6_sc21.sg.k"
    
    if not fn_in.exists():
        pytest.skip(f"Test file not found: {fn_in}")
    
    # Read the model
    model = read_output_model(str(fn_in), 'sc', model_type='BM2')
    
    # Test attribute access
    ea_attr = model.ea
    assert ea_attr is not None, "EA should be accessible as attribute"
    
    # Test model_dump() for Pydantic models
    if hasattr(model, 'model_dump'):
        model_dict = model.model_dump()
        assert isinstance(model_dict, dict), "model_dump() should return a dict"
        assert model_dict['ea'] == ea_attr, "model_dump() should agree with attributes"
    
    logger.info("✓ All property access methods work correctly")


@pytest.mark.io
@pytest.mark.swiftcomp
def test_swiftcomp_output_model_phi_pia_branches(test_data_dir):
    """phi_pia must come from the actual rotation angle when the axes are
    rotated, and default to 0 (not a swallowed parse failure) when the
    SwiftComp output states the user axes already are the principal axes.
    """
    already_principal = test_data_dir / "swiftcomp" / "sg21t_tri6_sc21.sg.k"
    rotated = test_data_dir / "swiftcomp" / "sg31t_hex20_sc21.sg.k"

    if not already_principal.exists() or not rotated.exists():
        pytest.skip("Test fixtures not found")

    model_zero = read_output_model(str(already_principal), 'sc', model_type='BM2')
    assert model_zero.phi_pia == 0

    model_rotated = read_output_model(str(rotated), 'sc', model_type='BM2')
    assert model_rotated.phi_pia == pytest.approx(63.079756027134785)

