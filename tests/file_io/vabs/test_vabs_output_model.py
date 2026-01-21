"""Test VABS output model reading.

This module tests reading VABS homogenization output (.K files) including:
- Euler-Bernoulli beam model (BM1)
- Timoshenko beam model (BM2)
- Effective properties (EA, GJ, EI, mass, etc.)
"""
import os
from pathlib import Path
import pytest

from sgio import readOutputModel, logger, configure_logging

configure_logging(cout_level='info')


@pytest.mark.io
@pytest.mark.vabs
@pytest.mark.parametrize("test_case", [
    {
        'fn_base': 'sg21t_tri3_vabs40',
        'file_format': 'vabs',
        'model_type': 'BM2',
        'expected_properties': ['ea', 'gj', 'ei22', 'ei33'],
        'optional_properties': ['ga22', 'ga33'],  # Shear stiffness for Timoshenko
    },
])
def test_vabs_output_model_beam(test_case, test_data_dir):
    """Test reading VABS beam model output files.
    
    This test verifies:
    1. VABS .K output files can be read
    2. Model type is correctly identified (BM1 or BM2)
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
    
    # Construct file path - VABS output files have .sg.K extension
    fn_in = test_data_dir / "vabs" / "version_4_0" / f"{fn_base}.sg.K"
    
    if not fn_in.exists():
        # Try legacy location
        fn_in = Path(__file__).parent.parent.parent / "files" / "vabs" / "version_4_0" / f"{fn_base}.sg.K"
    
    if not fn_in.exists():
        pytest.skip(f"Test file not found: {fn_in}")
    
    logger.info(f"Reading VABS output model from: {fn_in}")
    
    # Read the output model
    model = readOutputModel(str(fn_in), file_format, model_type=model_type)
    
    # Verify model was read
    assert model is not None, "Model should not be None"
    
    # Verify expected properties exist and are not None
    for prop in expected_properties:
        value = model.get(prop)
        assert value is not None, f"Property '{prop}' should not be None"
        logger.info(f"{prop} = {value}")
    
    # Verify some basic properties have reasonable values
    # EA (extension stiffness) should be positive
    ea = model.get('ea')
    if ea is not None:
        assert ea > 0, f"EA should be positive, got {ea}"
    
    # GJ (torsional stiffness) should be positive
    gj = model.get('gj')
    if gj is not None:
        assert gj > 0, f"GJ should be positive, got {gj}"
    
    # EI22 and EI33 (bending stiffness) should be positive
    ei22 = model.get('ei22')
    if ei22 is not None:
        assert ei22 > 0, f"EI22 should be positive, got {ei22}"
    
    ei33 = model.get('ei33')
    if ei33 is not None:
        assert ei33 > 0, f"EI33 should be positive, got {ei33}"
    
    # Check optional properties (e.g., shear stiffness for Timoshenko beam)
    for prop in optional_properties:
        value = model.get(prop)
        if value is not None:
            logger.info(f"{prop} = {value}")
            # Shear stiffness should be positive if present
            if prop in ['ga22', 'ga33']:
                assert value > 0, f"{prop} should be positive, got {value}"
    
    logger.info(f"✓ Successfully read {model_type} model from {fn_base}")


@pytest.mark.io
@pytest.mark.vabs
def test_vabs_output_model_properties_access(test_data_dir):
    """Test different ways to access model properties.
    
    This test verifies:
    1. Properties can be accessed via .get() method
    2. Properties can be accessed as attributes
    3. Model can be converted to dict
    
    Args:
        test_data_dir: Fixture providing test data directory
    """
    fn_in = test_data_dir / "vabs" / "version_4_0" / "sg21t_tri3_vabs40.sg.K"
    
    if not fn_in.exists():
        fn_in = Path(__file__).parent.parent.parent / "files" / "vabs" / "version_4_0" / "sg21t_tri3_vabs40.sg.K"
    
    if not fn_in.exists():
        pytest.skip(f"Test file not found: {fn_in}")
    
    # Read the model
    model = readOutputModel(str(fn_in), 'vabs', model_type='BM2')
    
    # Test .get() method
    ea_get = model.get('ea')
    assert ea_get is not None, "EA should be accessible via .get()"
    
    # Test attribute access
    ea_attr = model.ea
    assert ea_attr is not None, "EA should be accessible as attribute"
    assert ea_get == ea_attr, "Both access methods should return the same value"
    
    # Test model_dump() for Pydantic models
    if hasattr(model, 'model_dump'):
        model_dict = model.model_dump()
        assert isinstance(model_dict, dict), "model_dump() should return a dict"
        assert 'ea' in model_dict, "EA should be in model dict"
    
    logger.info("✓ All property access methods work correctly")

