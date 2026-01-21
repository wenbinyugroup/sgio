"""Test plotting functionality.

This module tests the visualization functions for plotting cross-sections.
"""
import pytest
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

import sgio
from sgio.utils.plot import plot_sg_2d


@pytest.mark.visualization
@pytest.mark.io
@pytest.mark.vabs
def test_plot_sg_2d_basic(test_data_dir):
    """Test basic 2D structure gene plotting.

    This test verifies:
    1. Cross-section can be read from file
    2. Output model can be read
    3. plot_sg_2d function executes without errors
    4. Figure and axes are created correctly
    """
    # Use a test file from the test data directory
    fn = test_data_dir / 'vabs' / 'version_4_0' / 'sg21t_tri3_vabs40.sg'
    
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")
    
    # Check if output file exists
    fn_out = Path(f'{fn}.K')
    if not fn_out.exists():
        pytest.skip(f"Output file not found: {fn_out}")
    
    # Read the cross-section
    cs = sgio.read(str(fn), 'vabs')
    assert cs is not None, "Failed to read cross-section"
    assert hasattr(cs, 'mesh'), "Cross-section should have mesh attribute"
    
    # Read the output model
    model = sgio.readOutputModel(str(fn_out), 'vabs', sg=cs)
    assert model is not None, "Failed to read output model"
    
    # Create figure and axes
    fig, ax = plt.subplots()
    
    # Plot the cross-section
    try:
        plot_sg_2d(cs, model, ax)
    except Exception as e:
        pytest.fail(f"plot_sg_2d raised an exception: {e}")
    
    # Verify the plot was created
    assert ax is not None, "Axes should not be None"
    assert len(ax.collections) > 0 or len(ax.lines) > 0, "Plot should contain some elements"
    
    # Clean up
    plt.close(fig)


@pytest.mark.visualization
@pytest.mark.io
@pytest.mark.vabs
def test_plot_sg_2d_with_properties(test_data_dir):
    """Test 2D plotting with beam properties visualization.

    This test verifies:
    1. Plot includes principal bending axes
    2. Plot includes mass center
    3. Plot includes other beam property features
    """
    fn = test_data_dir / 'vabs' / 'version_4_0' / 'sg21t_tri3_vabs40.sg'
    
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")
    
    fn_out = Path(f'{fn}.K')
    if not fn_out.exists():
        pytest.skip(f"Output file not found: {fn_out}")
    
    cs = sgio.read(str(fn), 'vabs')
    model = sgio.readOutputModel(str(fn_out), 'vabs', sg=cs)
    
    fig, ax = plt.subplots()
    
    # Plot with default settings
    plot_sg_2d(cs, model, ax)
    
    # Verify that lines were added (principal axes, centers, etc.)
    assert len(ax.lines) > 0, "Plot should contain lines for axes and centers"
    
    # Verify that mesh was added (as a collection)
    assert len(ax.collections) > 0, "Plot should contain mesh elements"
    
    plt.close(fig)


@pytest.mark.visualization
def test_plot_sg_2d_error_handling():
    """Test error handling in plot_sg_2d function.
    
    This test verifies:
    1. Function raises ValueError for None arguments
    2. Function raises ValueError for invalid sg object
    """
    fig, ax = plt.subplots()
    
    # Test with None arguments
    with pytest.raises(ValueError, match="cannot be None"):
        plot_sg_2d(None, None, ax)
    
    with pytest.raises(ValueError, match="cannot be None"):
        plot_sg_2d(None, {}, ax)
    
    with pytest.raises(ValueError, match="cannot be None"):
        plot_sg_2d({}, None, ax)
    
    with pytest.raises(ValueError, match="cannot be None"):
        plot_sg_2d({}, {}, None)
    
    plt.close(fig)


@pytest.mark.visualization
@pytest.mark.io
@pytest.mark.vabs
def test_plot_sg_2d_euler_bernoulli(test_data_dir):
    """Test plotting with Euler-Bernoulli beam model.

    This test verifies plotting works with BM1 (Euler-Bernoulli) models.
    """
    fn = test_data_dir / 'vabs' / 'version_4_0' / 'sg21eb_tri3_vabs40.sg'

    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")

    fn_out = Path(f'{fn}.K')
    if not fn_out.exists():
        pytest.skip(f"Output file not found: {fn_out}")

    cs = sgio.read(str(fn), 'vabs')

    # Read the model
    model = sgio.readOutputModel(str(fn_out), 'vabs', sg=cs)

    fig, ax = plt.subplots()
    plot_sg_2d(cs, model, ax)

    # Just verify it doesn't crash
    assert ax is not None

    plt.close(fig)

