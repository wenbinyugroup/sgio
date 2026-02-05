"""Test module for structural models (beam, plate, solid).

This module tests the Pydantic-based model classes for:
- Beam models (BM1: Euler-Bernoulli, BM2: Timoshenko)
- Plate models (PL1: Kirchhoff-Love, PL2: Reissner-Mindlin)
- Solid models (SD1: Cauchy continuum)
"""

import pytest
import math
from pydantic import ValidationError

from sgio.model.beam import EulerBernoulliBeamModel
from sgio.model.solid import CauchyContinuumModel


@pytest.mark.unit
class TestEulerBernoulliBeamModelBasic:
    """Test basic functionality of the Euler-Bernoulli beam model (BM1)."""

    def test_default_creation(self):
        """Test creating a beam model with default values."""
        beam = EulerBernoulliBeamModel()
        
        assert beam.name == ''
        assert beam.id is None
        assert beam.dim == 1
        assert beam.label == 'bm1'
        assert beam.model_name == 'Euler-Bernoulli beam model'
        assert beam.phi_pia == 0
        assert beam.phi_pba == 0

    def test_parameterized_creation(self):
        """Test creating a beam model with specific parameters."""
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
        """Test creating a beam model from a dictionary."""
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


@pytest.mark.unit
class TestEulerBernoulliBeamModelValidation:
    """Test validation functionality for Euler-Bernoulli beam model."""

    def test_negative_mass_validation(self):
        """Test that negative mass values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            EulerBernoulliBeamModel(mu=-100.0)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'greater_than_equal'
        assert 'mu' in str(errors[0]['loc'])

    def test_negative_stiffness_validation(self):
        """Test that negative stiffness values are rejected."""
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(ea=-1e11)
        
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(gj=-1e10)
        
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(ei22=-1e9)

    def test_mass_matrix_validation(self):
        """Test validation of 6x6 mass matrix."""
        # Valid 6x6 matrix
        valid_matrix = [[0.0] * 6 for _ in range(6)]
        beam = EulerBernoulliBeamModel(mass=valid_matrix)
        assert beam.mass == valid_matrix

        # Invalid matrix - wrong number of rows
        with pytest.raises(ValidationError) as exc_info:
            EulerBernoulliBeamModel(mass=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        
        errors = exc_info.value.errors()
        assert 'Matrix must be 6x6' in str(errors[0]['msg'])

        # Invalid matrix - wrong number of columns
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(mass=[[1.0, 2.0, 3.0]] * 6)

    def test_stiffness_matrix_validation(self):
        """Test validation of 4x4 stiffness matrix."""
        # Valid 4x4 matrix
        valid_matrix = [[0.0] * 4 for _ in range(4)]
        beam = EulerBernoulliBeamModel(stff=valid_matrix)
        assert beam.stff == valid_matrix

        # Invalid matrix - wrong dimensions
        with pytest.raises(ValidationError):
            EulerBernoulliBeamModel(stff=[[1.0, 2.0], [3.0, 4.0]])


@pytest.mark.unit
class TestEulerBernoulliBeamModelComputedProperties:
    """Test computed properties of Euler-Bernoulli beam model."""

    def test_gyr1_property(self):
        """Test gyr1 computed property (radius of gyration about axis 1)."""
        beam = EulerBernoulliBeamModel(rg=0.1)
        assert beam.gyr1 == 0.1
        
        beam_none = EulerBernoulliBeamModel()
        assert beam_none.gyr1 is None

    def test_gyr2_property(self):
        """Test gyr2 computed property (radius of gyration about axis 2)."""
        beam = EulerBernoulliBeamModel(i22=1e6, mu=1000.0)
        expected = math.sqrt(1e6 / 1000.0)
        gyr2 = beam.gyr2
        assert gyr2 is not None
        assert abs(gyr2 - expected) < 1e-10
        
        # Test with missing values
        beam_incomplete = EulerBernoulliBeamModel(i22=1e6)
        assert beam_incomplete.gyr2 is None
        
        beam_zero_mu = EulerBernoulliBeamModel(i22=1e6, mu=0.0)
        assert beam_zero_mu.gyr2 is None

    def test_gyr3_property(self):
        """Test gyr3 computed property (radius of gyration about axis 3)."""
        beam = EulerBernoulliBeamModel(i33=2e6, mu=1000.0)
        expected = math.sqrt(2e6 / 1000.0)
        gyr3 = beam.gyr3
        assert gyr3 is not None
        assert abs(gyr3 - expected) < 1e-10


@pytest.mark.unit
class TestEulerBernoulliBeamModelBackwardCompatibility:
    """Test backward compatibility with existing API."""

    def test_get_method_basic_properties(self):
        """Test the get() method for basic properties."""
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
        """Test the get() method with multiple properties."""
        beam = EulerBernoulliBeamModel(mu=1000.0, ea=2.1e11, gj=8.1e10)

        props = beam.get(['mu', 'ea', 'gj'])
        assert props == [1000.0, 2.1e11, 8.1e10]

    def test_get_all_method(self):
        """Test the getAll() method."""
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
        """Test the __repr__ method still works."""
        beam = EulerBernoulliBeamModel(
            name="Test Beam",
            mu=1000.0,
            ea=2.1e11
        )

        repr_str = repr(beam)
        assert 'Euler-Bernoulli beam model' in repr_str
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0


@pytest.mark.unit
class TestEulerBernoulliBeamModelSerialization:
    """Test Pydantic serialization features."""

    def test_model_dump(self):
        """Test converting model to dictionary."""
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
        """Test excluding None values from serialization."""
        beam = EulerBernoulliBeamModel(name="Test", mu=1000.0)

        data = beam.model_dump(exclude_none=True)
        assert 'name' in data
        assert 'mu' in data
        assert 'id' not in data  # Should be excluded since it's None
        assert 'ea' not in data  # Should be excluded since it's None

    def test_json_serialization(self):
        """Test JSON serialization."""
        beam = EulerBernoulliBeamModel(name="JSON Test", mu=500.0)

        json_str = beam.model_dump_json()
        assert isinstance(json_str, str)
        assert '"name":"JSON Test"' in json_str or '"name": "JSON Test"' in json_str


@pytest.mark.unit
class TestCauchyContinuumModel:
    """Tests for the Cauchy continuum solid model (SD1)."""

    def test_default_creation(self):
        """Default model has expected metadata and zeroed properties."""
        solid = CauchyContinuumModel()

        assert solid.dim == 3
        assert solid.label == 'sd1'
        assert solid.model_name == 'Cauchy continuum model'
        assert solid.density == 0
        assert solid.isotropy == 0

    def test_parameterized_creation(self):
        """Parameterized creation populates elastic and strength properties."""
        solid = CauchyContinuumModel(
            name='Carbon',
            id=42,
            density=1600.0,
            isotropy=1,
            e1=140e9,
            e2=10e9,
            e3=10e9,
            g12=5e9,
            g13=4e9,
            g23=3e9,
            nu12=0.28,
            nu13=0.26,
            nu23=0.3,
            x1t=1500.0,
            specific_heat=900.0,
        )

        assert solid.name == 'Carbon'
        assert solid.id == 42
        assert solid.e1 == pytest.approx(140e9)
        assert solid.nu23 == pytest.approx(0.3)
        assert solid.x1t == pytest.approx(1500.0)
        assert solid.specific_heat == pytest.approx(900.0)

    def test_invalid_poisson_ratio(self):
        """Out-of-range Poisson ratio is rejected with validation error."""
        with pytest.raises(ValidationError):
            CauchyContinuumModel(nu12=0.6)

        with pytest.raises(ValidationError):
            CauchyContinuumModel(nu13=-1.5)

    def test_invalid_stiffness_matrix(self):
        """Stiffness/compliance matrices must be 6x6."""
        with pytest.raises(ValidationError) as exc_info:
            CauchyContinuumModel(stff=[[1, 2], [3, 4]])

        assert 'Matrix must be 6x6' in str(exc_info.value)

        with pytest.raises(ValidationError):
            CauchyContinuumModel(cmpl=[[0.0] * 6 for _ in range(5)])

    def test_set_method_isotropy_parsing(self):
        """set('isotropy', value) accepts string shorthands."""
        solid = CauchyContinuumModel()

        solid.set('isotropy', 'orthotropic')
        assert solid.isotropy == 1

        solid.set('isotropy', 'anisotropic')
        assert solid.isotropy == 2

        solid.set('isotropy', 'iso')
        assert solid.isotropy == 0

    def test_set_elastic_validation(self):
        """set('elastic', ...) respects field validators under assignment."""
        solid = CauchyContinuumModel(isotropy=0)

        solid.set('elastic', [210e9, 0.3])
        assert solid.e1 == pytest.approx(210e9)
        assert solid.nu12 == pytest.approx(0.3)

        with pytest.raises(ValidationError):
            solid.set('elastic', [-1.0, 0.25])

        with pytest.raises(ValidationError):
            solid.set('elastic', [100e9, 0.7])

    def test_set_elastic_orthotropic(self):
        """Orthotropic elastic input populates the nine engineering constants."""
        solid = CauchyContinuumModel(isotropy=1)
        engineering = [120e9, 10e9, 10e9, 5e9, 4e9, 3e9, 0.25, 0.23, 0.21]

        solid.set('elastic', engineering, input_type='engineering')

        assert solid.e1 == pytest.approx(engineering[0])
        assert solid.e2 == pytest.approx(engineering[1])
        assert solid.e3 == pytest.approx(engineering[2])
        assert solid.g12 == pytest.approx(engineering[3])
        assert solid.g13 == pytest.approx(engineering[4])
        assert solid.g23 == pytest.approx(engineering[5])
        assert solid.nu12 == pytest.approx(engineering[6])
        assert solid.nu13 == pytest.approx(engineering[7])
        assert solid.nu23 == pytest.approx(engineering[8])

    def test_set_elastic_anisotropic_matrix_validation(self):
        """Anisotropic stiffness assignment validates matrix dimensions."""
        solid = CauchyContinuumModel(isotropy=2)
        bad_matrix = [[0.0] * 5 for _ in range(6)]

        with pytest.raises(ValidationError):
            solid.set('elastic', bad_matrix, input_type='stiffness')

        good_matrix = [[0.0] * 6 for _ in range(6)]
        solid.set('elastic', good_matrix, input_type='stiffness')
        assert solid.stff == good_matrix

    def test_strength_constants_assignment(self):
        """set('strength_constants', ...) distributes values to properties."""
        solid = CauchyContinuumModel()
        strength = [1500.0, 1200.0, 900.0, 800.0, 600.0, 500.0, 200.0, 180.0, 160.0]

        solid.set('strength_constants', strength)

        assert solid.strength_constants == strength
        assert solid.x1t == pytest.approx(1500.0)
        assert solid.x12 == pytest.approx(160.0)

    def test_get_method_aliases(self):
        """get() exposes legacy names for properties."""
        solid = CauchyContinuumModel(
            density=1500.0,
            temperature=20.0,
            isotropy=1,
            e1=100e9,
            nu12=0.3,
            stff=[[1.0] * 6 for _ in range(6)],
            cte=[1e-6] * 6,
        )

        assert solid.get('density') == 1500.0
        assert solid.get('temperature') == 20.0
        assert solid.get('e') == 100e9
        assert solid.get('nu') == pytest.approx(0.3)
        assert solid.get('c11') == 1.0
        assert solid.get('alpha') == pytest.approx(1e-6)


