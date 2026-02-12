"""Test module for JSON material reading functions.

This module tests JSON reading functionality for CauchyContinuumModel:
- read_material_from_json: Read a single material from JSON
- read_materials_from_json: Read multiple materials from JSON
"""

import pytest
import json
import tempfile
from pathlib import Path

from sgio.model.solid import (
    CauchyContinuumModel,
    read_material_from_json,
    read_materials_from_json
)


@pytest.mark.unit
class TestReadMaterialFromJson:
    """Test read_material_from_json function."""

    def test_read_isotropic_material(self, steel_isotropic_path):
        """Test reading an isotropic material from JSON file."""
        # Read material
        materials = read_material_from_json(steel_isotropic_path)
        
        # Verify it's a dict with the material name as key
        assert isinstance(materials, dict)
        assert len(materials) == 1
        assert "Steel" in materials
        
        mat = materials["Steel"]
        assert isinstance(mat, CauchyContinuumModel)
        assert mat.name == "Steel"
        assert mat.isotropy == 0
        assert mat.e1 == 200e9
        assert mat.nu12 == 0.3
        assert mat.density == 7850
        assert mat.stff is not None  # Should auto-build stiffness

    def test_read_orthotropic_material(self, carbon_fiber_orthotropic_path):
        """Test reading an orthotropic material from JSON file."""
        # Read material
        materials = read_material_from_json(carbon_fiber_orthotropic_path)
        mat = materials["Carbon Fiber"]
        
        # Verify
        assert mat.name == "Carbon Fiber"
        assert mat.isotropy == 1
        assert mat.e1 == 150e9
        assert mat.e2 == 10e9
        assert mat.g12 == 5e9
        assert mat.density == 1600

    def test_read_transverse_isotropic_material(self, ti_composite_transverse_path):
        """Test reading a transverse isotropic material from JSON file."""
        # Read material
        materials = read_material_from_json(ti_composite_transverse_path)
        mat = materials["Ti-Composite"]
        
        # Verify
        assert mat.name == "Ti-Composite"
        assert mat.isotropy == 3
        assert mat.e1 == 120e9
        assert mat.e2 == 80e9
        assert mat.stff is not None

    def test_read_material_with_strength_properties(self, aluminum_strength_path):
        """Test reading material with strength properties."""
        # Read material
        materials = read_material_from_json(aluminum_strength_path)
        mat = materials["Aluminum"]
        
        # Verify
        assert mat.name == "Aluminum"
        assert mat.x1t == 310e6
        assert mat.x1c == 310e6
        assert mat.failure_criterion == 1

    def test_read_material_with_thermal_properties(self, steel_thermal_path):
        """Test reading material with thermal properties."""
        # Read material
        materials = read_material_from_json(steel_thermal_path)
        mat = materials["Steel Thermal"]
        
        # Verify
        assert mat.cte is not None
        assert len(mat.cte) == 6
        assert mat.cte[0] == 12e-6
        assert mat.specific_heat == 500

    def test_read_material_with_stiffness_matrix(self, custom_anisotropic_path):
        """Test reading material with explicit stiffness matrix."""
        # Read material
        materials = read_material_from_json(custom_anisotropic_path)
        mat = materials["Custom Material"]
        
        # Verify
        assert mat.name == "Custom Material"
        assert mat.stff is not None
        assert len(mat.stff) == 6
        assert mat.stff[0][0] == 1e9

    def test_file_not_found(self):
        """Test error when file does not exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            read_material_from_json("nonexistent_file.json")
        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json_format(self, invalid_format_path):
        """Test error when JSON is not a dictionary."""
        with pytest.raises(TypeError) as exc_info:
            read_material_from_json(invalid_format_path)
        assert "dictionary" in str(exc_info.value).lower()

    def test_invalid_material_parameters(self, invalid_material_path):
        """Test error when material parameters are invalid."""
        # Should raise validation error from Pydantic
        with pytest.raises(Exception):  # ValidationError
            read_material_from_json(invalid_material_path)

    def test_empty_material(self, empty_material_path):
        """Test reading material with minimal parameters."""
        # Should create material with defaults
        materials = read_material_from_json(empty_material_path)
        mat = materials['Empty Material']
        assert mat.name == 'Empty Material'
        assert mat.density == 0
        assert mat.isotropy == 0


@pytest.mark.unit
class TestReadMaterialsFromJson:
    """Test read_materials_from_json function."""

    def test_read_multiple_materials(self, multiple_materials_path):
        """Test reading multiple materials from JSON file."""
        # Read materials
        materials = read_materials_from_json(multiple_materials_path)
        
        # Verify - now returns dict instead of list
        assert isinstance(materials, dict)
        assert len(materials) == 3
        assert all(isinstance(m, CauchyContinuumModel) for m in materials.values())
        assert "Steel" in materials
        assert "Aluminum" in materials
        assert "Titanium" in materials
        assert materials["Steel"].name == "Steel"
        assert materials["Aluminum"].name == "Aluminum"
        assert materials["Titanium"].name == "Titanium"

    def test_read_mixed_isotropy_materials(self, mixed_isotropy_path):
        """Test reading materials with different isotropy types."""
        # Read materials
        materials = read_materials_from_json(mixed_isotropy_path)
        
        # Verify - access by name instead of index
        assert len(materials) == 3
        assert materials["Isotropic"].isotropy == 0
        assert materials["Orthotropic"].isotropy == 1
        assert materials["Transverse"].isotropy == 3

    def test_read_empty_list(self, empty_list_path):
        """Test reading empty material list."""
        # Read materials
        materials = read_materials_from_json(empty_list_path)
        
        # Verify - now returns empty dict instead of empty list
        assert isinstance(materials, dict)
        assert len(materials) == 0

    def test_read_single_material_in_list(self, tmp_path):
        """Test reading a single material in a list."""
        materials_data = [
            {"name": "Steel", "isotropy": 0, "e": 200e9, "nu": 0.3}
        ]
        json_file = tmp_path / "single.json"
        with open(json_file, 'w') as f:
            json.dump(materials_data, f)
        
        # Read materials
        materials = read_materials_from_json(str(json_file))
        
        # Verify - now dict with name as key
        assert len(materials) == 1
        assert "Steel" in materials
        assert materials["Steel"].name == "Steel"

    def test_file_not_found_multiple(self):
        """Test error when file does not exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            read_materials_from_json("nonexistent.json")
        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json_format_multiple(self, not_list_path):
        """Test error when JSON is not a list."""
        with pytest.raises(TypeError) as exc_info:
            read_materials_from_json(not_list_path)
        assert "list" in str(exc_info.value).lower()

    def test_invalid_material_in_list(self, invalid_list_path):
        """Test error when one material in list is invalid."""
        # Should raise validation error
        with pytest.raises(Exception):  # ValidationError
            read_materials_from_json(invalid_list_path)

    def test_non_dict_element_in_list(self, mixed_types_path):
        """Test error when list contains non-dictionary elements."""
        with pytest.raises(TypeError) as exc_info:
            read_materials_from_json(mixed_types_path)
        assert "index 1" in str(exc_info.value).lower()
        assert "not a dictionary" in str(exc_info.value).lower()

    def test_materials_with_varying_properties(self, varying_properties_path):
        """Test reading materials with different sets of properties."""
        # Read materials
        materials = read_materials_from_json(varying_properties_path)
        
        # Verify - access by name instead of index
        assert len(materials) == 3
        # Check specific materials by their names
        assert "Basic" in materials
        assert "With Strength" in materials  
        assert "With Thermal" in materials
        assert materials["Basic"].x1t is None
        assert materials["With Strength"].x1t == 400e6
        assert materials["With Thermal"].cte is not None


@pytest.mark.unit
class TestJsonRoundTrip:
    """Test round-trip conversion: CauchyContinuumModel -> JSON -> CauchyContinuumModel."""

    def test_roundtrip_isotropic(self, tmp_path):
        """Test round-trip for isotropic material."""
        # Create original material
        original = CauchyContinuumModel(
            name="Steel",
            isotropy=0,
            e=200e9,
            nu=0.3,
            density=7850
        )
        
        # Save to JSON
        json_file = tmp_path / "roundtrip.json"
        with open(json_file, 'w') as f:
            json.dump(original.model_dump(exclude_none=True), f)
        
        # Read back
        restored_dict = read_material_from_json(str(json_file))
        restored = restored_dict["Steel"]
        
        # Verify key properties match
        assert restored.name == original.name
        assert restored.e1 == original.e1
        assert restored.nu12 == original.nu12
        assert restored.density == original.density

    def test_roundtrip_orthotropic(self, tmp_path):
        """Test round-trip for orthotropic material."""
        original = CauchyContinuumModel(
            name="Composite",
            isotropy=1,
            e1=150e9, e2=10e9, e3=10e9,
            g12=5e9, g13=5e9, g23=3e9,
            nu12=0.3, nu13=0.3, nu23=0.4,
            density=1600
        )
        
        # Save to JSON
        json_file = tmp_path / "roundtrip_ortho.json"
        with open(json_file, 'w') as f:
            json.dump(original.model_dump(exclude_none=True), f)
        
        # Read back
        restored_dict = read_material_from_json(str(json_file))
        restored = restored_dict["Composite"]
        
        # Verify
        assert restored.name == original.name
        assert restored.e1 == original.e1
        assert restored.e2 == original.e2
        assert restored.g12 == original.g12

    def test_roundtrip_list(self, tmp_path):
        """Test round-trip for list of materials."""
        originals = [
            CauchyContinuumModel(name="Steel", isotropy=0, e=200e9, nu=0.3),
            CauchyContinuumModel(name="Aluminum", isotropy=0, e=70e9, nu=0.33),
        ]
        
        # Save to JSON
        json_file = tmp_path / "roundtrip_list.json"
        data = [mat.model_dump(exclude_none=True) for mat in originals]
        with open(json_file, 'w') as f:
            json.dump(data, f)
        
        # Read back - now returns dict
        restored_dict = read_materials_from_json(str(json_file))
        
        # Verify
        assert len(restored_dict) == len(originals)
        for orig in originals:
            assert orig.name in restored_dict
            rest = restored_dict[orig.name]
            assert rest.name == orig.name
            assert rest.e1 == orig.e1


@pytest.mark.unit
class TestWriteMaterialToJson:
    """Test write_to_json method."""

    def test_write_isotropic_material(self, tmp_path, steel_isotropic_path):
        """Test writing an isotropic material to JSON file."""
        # Read material from fixture
        materials = read_material_from_json(steel_isotropic_path)
        mat = materials["Steel"]
        
        # Write to JSON
        json_file = tmp_path / "steel_write.json"
        mat.write_to_json(str(json_file))
        
        # Verify file exists and can be read
        assert json_file.exists()
        
        # Read back and verify
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert data["name"] == "Steel"
        assert data["isotropy"] == 0
        assert data["e1"] == 200e9
        assert data["nu12"] == 0.3
        assert data["density"] == 7850
        assert "stff" in data  # Stiffness matrix should be included

    def test_write_orthotropic_material(self, tmp_path, carbon_fiber_orthotropic_path):
        """Test writing an orthotropic material to JSON file."""
        # Read material from fixture
        materials = read_material_from_json(carbon_fiber_orthotropic_path)
        mat = materials["Carbon Fiber"]
        
        # Write to JSON
        json_file = tmp_path / "carbon_write.json"
        mat.write_to_json(str(json_file), indent=2)
        
        # Read back
        restored_dict = read_material_from_json(str(json_file))
        restored = restored_dict["Carbon Fiber"]
        
        # Verify key properties
        assert restored.name == "Carbon Fiber"
        assert restored.isotropy == 1
        assert restored.e1 == 150e9
        assert restored.e2 == 10e9
        assert restored.g12 == 5e9

    def test_write_with_thermal_properties(self, tmp_path, steel_thermal_path):
        """Test writing material with thermal properties."""
        # Read material from fixture
        materials = read_material_from_json(steel_thermal_path)
        mat = materials["Steel Thermal"]
        
        # Write to JSON
        json_file = tmp_path / "thermal_write.json"
        mat.write_to_json(str(json_file))
        
        # Read back
        restored_dict = read_material_from_json(str(json_file))
        restored = restored_dict["Steel Thermal"]
        
        # Verify thermal properties
        assert restored.cte is not None
        assert len(restored.cte) == 6
        assert restored.cte[0] == 12e-6
        assert restored.specific_heat == 500

    def test_write_with_strength_properties(self, tmp_path, aluminum_strength_path):
        """Test writing material with strength properties."""
        # Read material from fixture
        materials = read_material_from_json(aluminum_strength_path)
        mat = materials["Aluminum"]
        
        # Write to JSON
        json_file = tmp_path / "strength_write.json"
        mat.write_to_json(str(json_file))
        
        # Read back
        restored_dict = read_material_from_json(str(json_file))
        restored = restored_dict["Aluminum"]
        
        # Verify strength properties
        assert restored.x1t == 310e6
        assert restored.x1c == 310e6
        assert restored.failure_criterion == 1

    def test_write_exclude_none(self, tmp_path):
        """Test writing with exclude_none option."""
        mat = CauchyContinuumModel(
            name="Minimal Material",
            isotropy=0,
            e=200e9,
            nu=0.3
            # No density, strength, thermal properties set explicitly
        )
        
        # Manually set some properties to None to test exclusion
        mat.e2 = None
        mat.g12 = None
        mat.x1t = None
        mat.cte = None
        
        # Write with exclude_none=True (default)
        json_file = tmp_path / "minimal_write.json"
        mat.write_to_json(str(json_file))
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Verify None values are excluded (but defaults are included)
        assert "density" in data  # Has default value 0
        assert data["density"] == 0
        assert "e2" not in data  # Set to None, should be excluded
        assert "g12" not in data  # Set to None, should be excluded
        assert "x1t" not in data  # Set to None, should be excluded
        assert "cte" not in data  # Set to None, should be excluded
        
        # Write with exclude_none=False
        json_file_none = tmp_path / "minimal_with_none.json"
        mat.write_to_json(str(json_file_none), exclude_none=False)
        
        with open(json_file_none, 'r') as f:
            data_none = json.load(f)
        
        # Verify None values are included when exclude_none=False
        assert "e2" in data_none
        assert data_none["e2"] is None
        assert "g12" in data_none
        assert data_none["g12"] is None
        assert "x1t" in data_none
        assert data_none["x1t"] is None
        assert "cte" in data_none
        assert data_none["cte"] is None

    def test_write_with_indent(self, tmp_path):
        """Test writing with indentation for pretty formatting."""
        mat = CauchyContinuumModel(
            name="Pretty Material",
            isotropy=0,
            e=200e9,
            nu=0.3,
            density=7850
        )
        
        # Write with indentation
        json_file = tmp_path / "pretty.json"
        mat.write_to_json(str(json_file), indent=4)
        
        # Read the raw content to verify formatting
        with open(json_file, 'r') as f:
            content = f.read()
        
        # Should contain newlines and indentation
        assert '\n' in content
        assert '    ' in content  # 4-space indentation

    def test_write_creates_directories(self, tmp_path):
        """Test that write_to_json creates parent directories."""
        mat = CauchyContinuumModel(
            name="Nested Material",
            isotropy=0,
            e=200e9,
            nu=0.3
        )
        
        # Write to nested path that doesn't exist
        nested_dir = tmp_path / "materials" / "metals"
        json_file = nested_dir / "nested.json"
        
        mat.write_to_json(str(json_file))
        
        # Verify file was created
        assert json_file.exists()
        assert nested_dir.exists()

    def test_roundtrip_write_read(self, tmp_path, carbon_fiber_orthotropic_path):
        """Test complete round-trip: create -> write -> read -> compare."""
        materials = read_material_from_json(carbon_fiber_orthotropic_path)
        original = materials["Carbon Fiber"]
        
        # Add some additional properties
        original.x1t = 2000e6
        original.cte = [1e-6, 2e-6, 3e-6, 0, 0, 0]
        
        # Write to file
        json_file = tmp_path / "roundtrip.json"
        original.write_to_json(str(json_file))
        
        # Read back
        restored_dict = read_material_from_json(str(json_file))
        restored = restored_dict["Carbon Fiber"]
        
        # Should be equal
        assert original == restored