"""
Test module for the refactored EulerBernoulliBeamModel with Pydantic
"""

import pytest
import math
from pydantic import ValidationError

from sgio.model.beam import EulerBernoulliBeamModel


class TestEulerBernoulliBeamModelBasic:
    """Test basic functionality of the refactored beam model"""

    def test_default_creation(self):
        """Test creating a beam model with default values"""
        beam = EulerBernoulliBeamModel()
        
        assert beam.name == ''
        assert beam.id is None
        assert beam.dim == 1
        assert beam.label == 'bm1'
        assert beam.model_name == 'Euler-Bernoulli beam model'
        assert beam.phi_pia == 0
        assert beam.phi_pba == 0

    def test_parameterized_creation(self):
        """Test creating a beam model with specific parameters"""
        beam = EulerBernoulliBeamModel(
            name="Test Beam",
            id=1,
            mu=1000.0,
            ea=2.1e11,
            gj=8.1e10,
            ei22=1e9,
            ei33=2e9
        )
        
        assert beam.name == "Test Beam"
        assert beam.id == 1
        assert beam.mu == 1000.0
        assert beam.ea == 2.1e11
        assert beam.gj == 8.1e10
        assert beam.ei22 == 1e9
        assert beam.ei33 == 2e9

    def test_dict_creation(self):
        """Test creating a beam model from a dictionary"""
        data = {
            "name": "Dict Beam",
            "mu": 500.0,
            "ea": 1.5e11,
            "xm2": 0.1,
            "xm3": -0.05
        }
        
        beam = EulerBernoulliBeamModel(**data)
        assert beam.name == "Dict Beam"
        assert beam.mu == 500.0
        assert beam.ea == 1.5e11
        assert beam.xm2 == 0.1
        assert beam.xm3 == -0.05


class TestEulerBernoulliBeamModelValidation:
    """Test validation functionality"""

    def test_negative_mass_validation(self):
        """Test that negative mass values are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            EulerBernoulliBeamModel(mu=-100.0)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'greater_than_equal'
        assert 'mu' in str(errors[0]['loc'])

    def test_negative_stiffness_validation(self):
        """Test that negative stiffness values are rejected"""
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(ea=-1e11)
        
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(gj=-1e10)
        
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(ei22=-1e9)

    def test_mass_matrix_validation(self):
        """Test validation of 6x6 mass matrix"""
        # Valid 6x6 matrix
        valid_matrix = [[0.0] * 6 for _ in range(6)]
        beam = EulerBernoulliBeamModel(mass=valid_matrix)
        assert beam.mass == valid_matrix

        # Invalid matrix - wrong number of rows
        with pytest.raises(ValidationError) as exc_info:
            EulerBernoulliBeamModel(mass=[[1, 2, 3], [4, 5, 6]])
        
        errors = exc_info.value.errors()
        assert 'Matrix must be 6x6' in str(errors[0]['msg'])

        # Invalid matrix - wrong number of columns
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(mass=[[1, 2, 3]] * 6)

    def test_stiffness_matrix_validation(self):
        """Test validation of 4x4 stiffness matrix"""
        # Valid 4x4 matrix
        valid_matrix = [[0.0] * 4 for _ in range(4)]
        beam = EulerBernoulliBeamModel(stff=valid_matrix)
        assert beam.stff == valid_matrix

        # Invalid matrix - wrong dimensions
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(stff=[[1, 2], [3, 4]])


class TestEulerBernoulliBeamModelComputedProperties:
    """Test computed properties"""

    def test_gyr1_property(self):
        """Test gyr1 computed property"""
        beam = EulerBernoulliBeamModel(rg=0.1)
        assert beam.gyr1 == 0.1
        
        beam_none = EulerBernoulliBeamModel()
        assert beam_none.gyr1 is None

    def test_gyr2_property(self):
        """Test gyr2 computed property"""
        beam = EulerBernoulliBeamModel(i22=1e6, mu=1000.0)
        expected = math.sqrt(1e6 / 1000.0)
        assert abs(beam.gyr2 - expected) < 1e-10
        
        # Test with missing values
        beam_incomplete = EulerBernoulliBeamModel(i22=1e6)
        assert beam_incomplete.gyr2 is None
        
        beam_zero_mu = EulerBernoulliBeamModel(i22=1e6, mu=0.0)
        assert beam_zero_mu.gyr2 is None

    def test_gyr3_property(self):
        """Test gyr3 computed property"""
        beam = EulerBernoulliBeamModel(i33=2e6, mu=1000.0)
        expected = math.sqrt(2e6 / 1000.0)
        assert abs(beam.gyr3 - expected) < 1e-10


class TestEulerBernoulliBeamModelBackwardCompatibility:
    """Test backward compatibility with existing API"""

    def test_get_method_basic_properties(self):
        """Test the get() method for basic properties"""
        beam = EulerBernoulliBeamModel(
            mu=1000.0,
            ea=2.1e11,
            gj=8.1e10,
            ei22=1e9,
            ei33=2e9,
            xm2=0.1,
            xm3=-0.05
        )
        
        assert beam.get('mu') == 1000.0
        assert beam.get('ea') == 2.1e11
        assert beam.get('gj') == 8.1e10
        assert beam.get('ei22') == 1e9
        assert beam.get('ei33') == 2e9
        assert beam.get('mc2') == 0.1  # alias for xm2
        assert beam.get('mc3') == -0.05  # alias for xm3

    def test_get_method_multiple_properties(self):
        """Test the get() method with multiple properties"""
        beam = EulerBernoulliBeamModel(mu=1000.0, ea=2.1e11, gj=8.1e10)
        
        props = beam.get(['mu', 'ea', 'gj'])
        assert props == [1000.0, 2.1e11, 8.1e10]

    def test_get_all_method(self):
        """Test the getAll() method"""
        beam = EulerBernoulliBeamModel(
            mu=1000.0,
            ea=2.1e11,
            gj=8.1e10,
            ei22=1e9,
            ei33=2e9
        )
        
        all_props = beam.getAll()
        assert isinstance(all_props, dict)
        assert 'mu' in all_props
        assert 'ea' in all_props
        assert all_props['mu'] == 1000.0
        assert all_props['ea'] == 2.1e11

    def test_repr_method(self):
        """Test the __repr__ method still works"""
        beam = EulerBernoulliBeamModel(
            name="Test Beam",
            mu=1000.0,
            ea=2.1e11
        )
        
        repr_str = repr(beam)
        assert 'Euler-Bernoulli beam model' in repr_str
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0


class TestEulerBernoulliBeamModelSerialization:
    """Test Pydantic serialization features"""

    def test_model_dump(self):
        """Test converting model to dictionary"""
        beam = EulerBernoulliBeamModel(
            name="Test Beam",
            mu=1000.0,
            ea=2.1e11,
            xm2=0.1
        )
        
        data = beam.model_dump()
        assert isinstance(data, dict)
        assert data['name'] == "Test Beam"
        assert data['mu'] == 1000.0
        assert data['ea'] == 2.1e11
        assert data['xm2'] == 0.1

    def test_model_dump_exclude_none(self):
        """Test excluding None values from serialization"""
        beam = EulerBernoulliBeamModel(name="Test", mu=1000.0)
        
        data = beam.model_dump(exclude_none=True)
        assert 'name' in data
        assert 'mu' in data
        assert 'id' not in data  # Should be excluded since it's None
        assert 'ea' not in data  # Should be excluded since it's None

    def test_json_serialization(self):
        """Test JSON serialization"""
        beam = EulerBernoulliBeamModel(name="JSON Test", mu=500.0)
        
        json_str = beam.model_dump_json()
        assert isinstance(json_str, str)
        assert '"name":"JSON Test"' in json_str or '"name": "JSON Test"' in json_str
