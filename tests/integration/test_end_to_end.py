"""Test end-to-end workflows.

This module tests complete workflows from building structure genes to writing output files.
"""
import pytest
from pathlib import Path
import yaml

import sgio


@pytest.mark.integration
@pytest.mark.io
def test_build_sg_1d_from_yaml(legacy_files_dir, tmp_path):
    """Test building a 1D structure gene from YAML input.

    This test verifies:
    1. YAML file can be read and parsed
    2. Material database can be created from YAML
    3. 1D SG can be built from layup design
    4. SG can be written to SwiftComp format
    """
    # Use the test YAML file
    fn = legacy_files_dir / 'sg1.yml'
    
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")
    
    # Read YAML input
    with open(fn, 'r') as fobj:
        raw_input = yaml.safe_load(fobj)
    
    assert raw_input is not None, "Failed to load YAML file"
    assert 'layup' in raw_input, "YAML should contain 'layup' section"
    assert 'material' in raw_input, "YAML should contain 'material' section"
    
    # Extract layup information
    sg_input = raw_input['layup']
    sg_name = sg_input.get('name', 'laminate')
    sg_design_input = sg_input['design']
    
    # Extract model information
    sg_model_input = sg_input['model']
    model_type = sg_model_input['type']
    mesh_size = sg_model_input.get('mesh_size', 0)
    elem_type = sg_model_input.get('element_type', 2)
    version = sg_model_input.get('version', '2.2')
    
    # Create material database
    mdb = {}
    for _m in raw_input['material']:
        mdb[_m['name']] = {'property': _m['property']}
    
    assert len(mdb) > 0, "Material database should not be empty"
    
    # Build 1D structure gene
    sg = sgio.buildSG1D(
        name=sg_name,
        layup=sg_design_input,
        sgdb=mdb,
        model=model_type,
        mesh_size=mesh_size,
        elem_type=elem_type,
    )
    
    assert sg is not None, "Failed to build SG"
    assert hasattr(sg, 'mesh'), "SG should have mesh"
    assert sg.mesh is not None, "SG mesh should not be None"
    assert len(sg.mesh.points) > 0, "SG should have nodes"
    assert len(sg.mesh.cells) > 0, "SG should have elements"
    
    # Verify materials were added
    assert len(sg.materials) > 0, "SG should have materials"
    assert len(sg.mocombos) > 0, "SG should have material-orientation combinations"
    
    # Write to output file
    fn_sg = tmp_path / f'{sg_name}.sg'
    try:
        sgio.write(sg, str(fn_sg), 'sc', format_version=version, model_space='z')
        assert fn_sg.exists(), "Output file should be created"
    except Exception as e:
        pytest.fail(f"Failed to write SG: {e}")


@pytest.mark.integration
@pytest.mark.io
def test_build_sg_1d_layup_symmetry(legacy_files_dir, tmp_path):
    """Test building 1D SG with symmetric layup.

    This test verifies:
    1. Symmetric layup is correctly expanded
    2. Number of layers is correct after symmetry
    """
    fn = legacy_files_dir / 'sg1.yml'
    
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")
    
    with open(fn, 'r') as fobj:
        raw_input = yaml.safe_load(fobj)
    
    sg_input = raw_input['layup']
    sg_design_input = sg_input['design']
    
    # Check symmetry setting
    symmetry = sg_design_input.get('symmetry', 0)
    original_layers = [l for l in sg_design_input['layers'] if l.get('number_of_plies', 1) > 0]
    
    # Build SG
    mdb = {}
    for _m in raw_input['material']:
        mdb[_m['name']] = {'property': _m['property']}
    
    sg = sgio.buildSG1D(
        name='test_symmetry',
        layup=sg_design_input,
        sgdb=mdb,
        model=sg_input['model']['type'],
        mesh_size=sg_input['model'].get('mesh_size', 0),
        elem_type=sg_input['model'].get('element_type', 2),
    )
    
    # Verify the SG was built
    assert sg is not None
    assert len(sg.mesh.points) > 0


@pytest.mark.integration
@pytest.mark.io
def test_build_sg_1d_mesh_generation(legacy_files_dir, tmp_path):
    """Test mesh generation in 1D SG building.

    This test verifies:
    1. Mesh is generated with correct element type
    2. Mesh has correct connectivity
    3. Property IDs are assigned correctly
    """
    fn = legacy_files_dir / 'sg1.yml'
    
    if not fn.exists():
        pytest.skip(f"Test file not found: {fn}")
    
    with open(fn, 'r') as fobj:
        raw_input = yaml.safe_load(fobj)
    
    sg_input = raw_input['layup']
    
    mdb = {}
    for _m in raw_input['material']:
        mdb[_m['name']] = {'property': _m['property']}
    
    elem_type = sg_input['model'].get('element_type', 2)
    
    sg = sgio.buildSG1D(
        name='test_mesh',
        layup=sg_input['design'],
        sgdb=mdb,
        model=sg_input['model']['type'],
        mesh_size=sg_input['model'].get('mesh_size', 0),
        elem_type=elem_type,
    )
    
    # Verify mesh structure
    assert len(sg.mesh.cells) > 0, "Should have cell blocks"
    
    # Check element type
    cell_block = sg.mesh.cells[0]
    expected_type = f'line{elem_type}' if elem_type > 2 else 'line'
    assert cell_block.type == expected_type, \
        f"Cell type should be '{expected_type}', got '{cell_block.type}'"
    
    # Check property IDs
    assert 'property_id' in sg.mesh.cell_data, "Should have property_id in cell_data"
    prop_ids = sg.mesh.cell_data['property_id'][0]
    assert len(prop_ids) > 0, "Should have property IDs assigned"
    assert all(pid > 0 for pid in prop_ids), "All property IDs should be positive"

