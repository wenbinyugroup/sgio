"""Shared pytest fixtures and configuration for SGIO test suite.

This module provides common fixtures used across all test modules.
"""
import pytest
from pathlib import Path
import tempfile
import shutil


# ============================================================================
# Directory Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_root_dir():
    """Root directory of the test suite."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def test_data_dir(test_root_dir):
    """Root directory for test fixtures (input data).

    This directory contains all test input files organized by format.
    For YAML test case files, check the yaml/ subdirectory.
    """
    return test_root_dir / "fixtures"


@pytest.fixture(scope="session")
def yaml_test_dir(test_data_dir):
    """Directory for YAML test case definition files."""
    return test_data_dir / "yaml"


@pytest.fixture(scope="session")
def expected_data_dir(test_root_dir):
    """Root directory for expected outputs.
    
    This directory contains reference outputs for validation.
    """
    return test_root_dir / "expected"


@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    """Temporary directory for test outputs.
    
    This fixture provides a clean temporary directory for each test.
    The directory is automatically cleaned up after the test.
    """
    return tmp_path


@pytest.fixture(scope="session")
def legacy_files_dir(test_root_dir):
    """Legacy test files directory (for backward compatibility).
    
    This points to the old 'files' directory during migration.
    """
    return test_root_dir / "files"


# ============================================================================
# Format-Specific File Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def vabs_test_files(test_data_dir, legacy_files_dir):
    """VABS test file paths organized by version.
    
    Returns a dictionary with version keys pointing to directories.
    Falls back to legacy location if new structure doesn't exist.
    """
    vabs_dir = test_data_dir / "vabs"
    if not vabs_dir.exists():
        vabs_dir = legacy_files_dir / "vabs"
    
    return {
        'root': vabs_dir,
        'v40': vabs_dir / 'version_4_0',
        'v41': vabs_dir / 'version_4_1',
    }


@pytest.fixture(scope="session")
def sc_test_files(test_data_dir, legacy_files_dir):
    """SwiftComp test file paths organized by version.
    
    Returns a dictionary with version keys pointing to directories.
    Falls back to legacy location if new structure doesn't exist.
    """
    sc_dir = test_data_dir / "swiftcomp"
    if not sc_dir.exists():
        sc_dir = legacy_files_dir / "swiftcomp"
    
    return {
        'root': sc_dir,
        'v21': sc_dir / 'version_2_1',
        'v22': sc_dir / 'version_2_2',
    }


@pytest.fixture(scope="session")
def abaqus_test_files(test_data_dir, legacy_files_dir):
    """Abaqus test file paths.
    
    Falls back to legacy location if new structure doesn't exist.
    """
    abaqus_dir = test_data_dir / "abaqus"
    if not abaqus_dir.exists():
        abaqus_dir = legacy_files_dir / "abaqus"
    
    return {'root': abaqus_dir}


@pytest.fixture(scope="session")
def gmsh_test_files(test_data_dir):
    """Gmsh test file paths."""
    return {'root': test_data_dir / "gmsh"}


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def sample_materials():
    """Sample material definitions for testing.
    
    Returns a dictionary with material types as keys.
    """
    return {
        'isotropic': {
            'name': 'Aluminum',
            'type': 'isotropic',
            'density': 2700.0,
            'elastic': {
                'E': 70e9,  # Young's modulus (Pa)
                'nu': 0.33,  # Poisson's ratio
            }
        },
        'orthotropic': {
            'name': 'Carbon Fiber',
            'type': 'orthotropic',
            'density': 1600.0,
            'elastic': {
                'E1': 150e9,
                'E2': 10e9,
                'E3': 10e9,
                'G12': 5e9,
                'G13': 5e9,
                'G23': 3.5e9,
                'nu12': 0.3,
                'nu13': 0.3,
                'nu23': 0.4,
            }
        },
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

# ============================================================================
# Material JSON Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def materials_fixtures_dir(test_data_dir):
    """Directory for material JSON fixtures."""
    materials_dir = test_data_dir / "materials"
    return materials_dir


@pytest.fixture(scope="session")
def steel_isotropic_path(materials_fixtures_dir):
    """Path to steel isotropic material fixture."""
    return str(materials_fixtures_dir / "steel_isotropic.json")


@pytest.fixture(scope="session")
def carbon_fiber_orthotropic_path(materials_fixtures_dir):
    """Path to carbon fiber orthotropic material fixture."""
    return str(materials_fixtures_dir / "carbon_fiber_orthotropic.json")


@pytest.fixture(scope="session")
def ti_composite_transverse_path(materials_fixtures_dir):
    """Path to Ti composite transverse isotropic material fixture."""
    return str(materials_fixtures_dir / "ti_composite_transverse.json")


@pytest.fixture(scope="session")
def aluminum_strength_path(materials_fixtures_dir):
    """Path to aluminum with strength properties fixture."""
    return str(materials_fixtures_dir / "aluminum_strength.json")


@pytest.fixture(scope="session")
def steel_thermal_path(materials_fixtures_dir):
    """Path to steel with thermal properties fixture."""
    return str(materials_fixtures_dir / "steel_thermal.json")


@pytest.fixture(scope="session")
def custom_anisotropic_path(materials_fixtures_dir):
    """Path to custom anisotropic material fixture."""
    return str(materials_fixtures_dir / "custom_anisotropic.json")


@pytest.fixture(scope="session")
def empty_material_path(materials_fixtures_dir):
    """Path to empty material fixture."""
    return str(materials_fixtures_dir / "empty.json")


@pytest.fixture(scope="session")
def multiple_materials_path(materials_fixtures_dir):
    """Path to multiple materials fixture."""
    return str(materials_fixtures_dir / "multiple_materials.json")


@pytest.fixture(scope="session")
def mixed_isotropy_path(materials_fixtures_dir):
    """Path to mixed isotropy materials fixture."""
    return str(materials_fixtures_dir / "mixed_isotropy.json")


@pytest.fixture(scope="session")
def empty_list_path(materials_fixtures_dir):
    """Path to empty list fixture."""
    return str(materials_fixtures_dir / "empty_list.json")


@pytest.fixture(scope="session")
def invalid_format_path(materials_fixtures_dir):
    """Path to invalid format fixture."""
    return str(materials_fixtures_dir / "invalid_format.json")


@pytest.fixture(scope="session")
def invalid_material_path(materials_fixtures_dir):
    """Path to invalid material fixture."""
    return str(materials_fixtures_dir / "invalid_material.json")


@pytest.fixture(scope="session")
def not_list_path(materials_fixtures_dir):
    """Path to not list fixture."""
    return str(materials_fixtures_dir / "not_list.json")


@pytest.fixture(scope="session")
def invalid_list_path(materials_fixtures_dir):
    """Path to invalid list fixture."""
    return str(materials_fixtures_dir / "invalid_list.json")


@pytest.fixture(scope="session")
def mixed_types_path(materials_fixtures_dir):
    """Path to mixed types fixture."""
    return str(materials_fixtures_dir / "mixed_types.json")


@pytest.fixture(scope="session")
def varying_properties_path(materials_fixtures_dir):
    """Path to varying properties fixture."""
    return str(materials_fixtures_dir / "varying_properties.json")


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def capsys_disabled(capsys):
    """Disable output capture for tests that need to write to stdout.
    
    This is useful for tests that use vendor code (like inprw) that
    writes directly to stdout.
    """
    with capsys.disabled():
        yield

