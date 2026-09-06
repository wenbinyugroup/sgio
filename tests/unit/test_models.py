"""Test module for structural models (beam, plate, solid).

This module tests the Pydantic-based model classes for:
- Beam models (BM1: Euler-Bernoulli, BM2: Timoshenko)
- Plate models (PL1: Kirchhoff-Love, PL2: Reissner-Mindlin)
- Solid models (SD1: Cauchy continuum)
"""

from io import StringIO
import pytest
import math
from pydantic import ValidationError

from sgio.iofunc.common.material_writers import write_material
from sgio.model.beam import EulerBernoulliBeamModel, TimoshenkoBeamModel
from sgio.model.material_components import (
    LinearElasticBehavior,
    MaterialDefinition,
    StrengthProperties,
    ThermalProperties,
)
from sgio.model.query_types import (
    ElasticInputType,
    MatrixKind,
    SectionAxis,
    SectionCenter,
    SectionMatrixKind,
    TensorComponent,
)
from sgio.model.shell import (
    KirchhoffLovePlateShellModel,
    ReissnerMindlinPlateShellModel,
)
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
class TestEulerBernoulliBeamModelSafety:
    """Test safe access behavior for the Euler-Bernoulli beam model (BM1)."""

    def test_default_matrix_queries_return_none(self):
        """Default objects should not raise when matrix-backed properties are missing."""
        beam = EulerBernoulliBeamModel()

        assert beam.get_section_matrix_component(SectionMatrixKind.MASS, 1, 1) is None
        assert beam.get_section_matrix_component(SectionMatrixKind.STIFFNESS, 1, 1) is None
        assert beam.get_section_matrix_component(SectionMatrixKind.COMPLIANCE, 1, 1) is None

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

    def test_typed_section_queries(self):
        """Typed section queries should expose centers, axes, and matrices."""
        beam = EulerBernoulliBeamModel(
            xm2=0.1,
            xm3=-0.05,
            xt2=0.2,
            xt3=-0.1,
            phi_pba=12.0,
            stff=[[1.0] * 4 for _ in range(4)],
        )

        assert beam.get_center(SectionCenter.MASS) == (0.1, -0.05)
        assert beam.get_center(SectionCenter.TENSION) == (0.2, -0.1)
        assert beam.get_axis_angle(SectionAxis.BENDING) == 12.0
        assert beam.get_section_matrix_component(SectionMatrixKind.STIFFNESS, 1, 1) == 1.0


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
class TestTimoshenkoBeamModelSafety:
    """Test safe access behavior for the Timoshenko beam model (BM2)."""

    def test_default_matrix_queries_return_none(self):
        """Default objects should not raise when matrix-backed properties are missing."""
        beam = TimoshenkoBeamModel()

        for kind in (
            SectionMatrixKind.MASS,
            SectionMatrixKind.STIFFNESS,
            SectionMatrixKind.CLASSICAL_STIFFNESS,
            SectionMatrixKind.COMPLIANCE,
            SectionMatrixKind.CLASSICAL_COMPLIANCE,
        ):
            assert beam.get_section_matrix_component(kind, 1, 1) is None

    def test_default_repr_does_not_crash(self):
        """Default repr should handle absent matrices cleanly."""
        beam = TimoshenkoBeamModel()

        output = repr(beam)

        assert 'Timoshenko beam model' in output
        assert 'NONE' in output

    def test_theory_schema_exposes_refined_and_classical_semantics(self):
        """Theory schema should describe both classical and refined matrix orders."""
        schema = TimoshenkoBeamModel.theory_schema

        assert 'stff' in schema.matrices
        assert 'stff_c' in schema.matrices
        assert schema.matrices['stff'].column_quantities == (
            'gamma11',
            'gamma12',
            'gamma13',
            'kappa11',
            'kappa12',
            'kappa13',
        )
        assert 'shear_center' in schema.centers
        assert 'principal_shear_axes' in schema.principal_axes

    def test_typed_center_and_axis_queries(self):
        """Typed section queries should expose Timoshenko-specific centers and axes."""
        beam = TimoshenkoBeamModel()
        beam.xs2 = 0.3
        beam.xs3 = -0.2
        beam.phi_psa = 18.0

        assert beam.get_center(SectionCenter.SHEAR) == (0.3, -0.2)
        assert beam.get_axis_angle(SectionAxis.SHEAR) == 18.0


@pytest.mark.unit
class TestKirchhoffLovePlateShellModelSafety:
    """Test safe access behavior for the Kirchhoff-Love shell model (PL1)."""

    def test_default_matrix_queries_return_none(self):
        """Default shell objects should not raise when matrix-backed properties are missing."""
        shell = KirchhoffLovePlateShellModel()

        assert shell.get_section_matrix_component(SectionMatrixKind.STIFFNESS, 1, 1) is None
        assert shell.get_section_matrix_component(
            SectionMatrixKind.GEOMETRIC_STIFFNESS, 1, 1) is None
        assert shell.get_section_matrix_component(SectionMatrixKind.MASS, 1, 1) is None

    def test_classical_and_geometric_stiffness_are_separate_kinds(self):
        """Geometrically corrected stiffness is its own kind, not a fallback."""
        shell = KirchhoffLovePlateShellModel()
        shell.stff = [[1.0] * 6 for _ in range(6)]
        shell.stff_geo = [[2.0] * 6 for _ in range(6)]

        assert shell.get_section_matrix_component(
            SectionMatrixKind.GEOMETRIC_STIFFNESS, 1, 1) == 2.0
        assert shell.get_section_matrix_component(SectionMatrixKind.STIFFNESS, 1, 1) == 1.0

    def test_default_repr_does_not_crash(self):
        """Default shell repr should handle absent matrices and constants cleanly."""
        shell = KirchhoffLovePlateShellModel()

        output = repr(shell)

        assert 'Kirchhoff-Love plate/shell model' in output
        assert 'NONE' in output

    def test_theory_schema_exposes_plate_resultant_order(self):
        """Theory schema should encode the Kirchhoff-Love A/B/D variable order."""
        schema = KirchhoffLovePlateShellModel.theory_schema

        assert schema.matrices['stff'].row_quantities == (
            'N11',
            'N22',
            'N12',
            'M11',
            'M22',
            'M12',
        )
        assert schema.matrices['stff'].column_quantities == (
            'epsilon11',
            'epsilon22',
            '2epsilon12',
            'kappa11',
            'kappa22',
            '2kappa12',
        )

    def test_typed_shell_matrix_queries(self):
        """Typed shell matrix access should work without legacy string tokens."""
        shell = KirchhoffLovePlateShellModel()
        shell.stff_geo = [[3.0] * 6 for _ in range(6)]

        assert shell.get_section_matrix_component(SectionMatrixKind.GEOMETRIC_STIFFNESS, 1, 1) == 3.0


@pytest.mark.unit
class TestReissnerMindlinPlateShellModelBoundary:
    """Test explicit boundary behavior for the not-yet-implemented PL2 model."""

    def test_instantiation_is_explicitly_blocked(self):
        """PL2 should fail loudly instead of exposing a silent empty shell."""
        with pytest.raises(NotImplementedError):
            ReissnerMindlinPlateShellModel()

    def test_theory_schema_is_declared_for_future_implementation(self):
        """Even the blocked type should declare its intended matrix semantics."""
        schema = ReissnerMindlinPlateShellModel.theory_schema

        assert schema.matrices['stff'].shape == (8, 8)
        assert schema.matrices['stff'].row_quantities[-2:] == ('N13', 'N23')
        assert schema.matrices['stff'].column_quantities[-2:] == ('gamma13', 'gamma23')


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
        """set_isotropy() accepts string shorthands."""
        solid = CauchyContinuumModel()

        solid.set_isotropy('orthotropic')
        assert solid.isotropy == 1

        solid.set_isotropy('anisotropic')
        assert solid.isotropy == 2

        solid.set_isotropy('iso')
        assert solid.isotropy == 0

    def test_set_elastic_validation(self):
        """set_elastic() respects field validators under assignment."""
        solid = CauchyContinuumModel(isotropy=0)

        solid.set_elastic([210e9, 0.3])
        assert solid.e1 == pytest.approx(210e9)
        assert solid.nu12 == pytest.approx(0.3)

        with pytest.raises(ValidationError):
            solid.set_elastic([-1.0, 0.25])

        with pytest.raises(ValidationError):
            solid.set_elastic([100e9, 0.7])

    def test_set_elastic_orthotropic(self):
        """Orthotropic elastic input populates the nine engineering constants."""
        solid = CauchyContinuumModel(isotropy=1)
        engineering = [120e9, 10e9, 10e9, 5e9, 4e9, 3e9, 0.25, 0.23, 0.21]

        solid.set_elastic(engineering, input_type='engineering')

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
            solid.set_elastic(bad_matrix, input_type='stiffness')

        good_matrix = [[1.0 if i == j else 0.0 for j in range(6)] for i in range(6)]
        solid.set_elastic(good_matrix, input_type='stiffness')
        assert solid.stff == good_matrix
        assert solid.cmpl is not None
        assert solid.cmpl[0][0] == pytest.approx(1.0)

    def test_constructor_builds_stiffness_from_compliance(self):
        """Compliance-only anisotropic inputs should also populate stiffness."""
        compliance = [
            [0.01, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.02, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.04, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.05, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.1, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.2],
        ]
        solid = CauchyContinuumModel(isotropy=2, cmpl=compliance)

        assert solid.cmpl is not None
        assert solid.cmpl[0][0] == pytest.approx(0.01)
        assert solid.cmpl[1][1] == pytest.approx(0.02)
        assert solid.stff is not None
        assert solid.get_matrix_component(
            MatrixKind.COMPLIANCE,
            TensorComponent(1, 1),
        ) == pytest.approx(0.01)
        assert solid.get_matrix_component(
            MatrixKind.STIFFNESS,
            TensorComponent(1, 1),
        ) == pytest.approx(100.0)
        assert solid.get_matrix_component(
            MatrixKind.STIFFNESS,
            TensorComponent(2, 2),
        ) == pytest.approx(50.0)

    def test_set_elastic_compliance_populates_stiffness(self):
        """Compliance assignment should keep stiffness/compliance views consistent."""
        compliance = [
            [0.01, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.02, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.04, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.05, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.1, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.2],
        ]
        solid = CauchyContinuumModel(isotropy=2)

        solid.set_elastic(compliance, input_type='compliance')

        assert solid.cmpl is not None
        assert solid.cmpl[0][0] == pytest.approx(0.01)
        assert solid.cmpl[5][5] == pytest.approx(0.2)
        assert solid.stff is not None
        assert solid.get_matrix_component(
            MatrixKind.STIFFNESS,
            TensorComponent(1, 1),
        ) == pytest.approx(100.0)

    def test_engineering_input_populates_compliance_view(self):
        """Engineering-constant inputs should also derive compliance."""
        solid = CauchyContinuumModel(isotropy=0)

        solid.set_elastic([210e9, 0.3], input_type='isotropic')

        assert solid.stff is not None
        assert solid.cmpl is not None
        assert solid.cmpl[0][0] == pytest.approx(1 / 210e9)

    def test_write_material_supports_compliance_only_anisotropic_input(self):
        """Material writing should not fail after compliance-only anisotropic initialization."""
        compliance = [
            [0.01, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.02, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.04, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.05, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.1, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.2],
        ]
        solid = CauchyContinuumModel(isotropy=2)
        solid.set_elastic(compliance, input_type='compliance')

        buffer = StringIO()
        write_material(mid=1, material=solid, file=buffer, analysis='h')

        content = buffer.getvalue()
        assert content
        assert '1.000000000000e+02' in content

    def test_strength_constants_assignment(self):
        """set_strength_constants() distributes values to properties."""
        solid = CauchyContinuumModel()
        strength = [1500.0, 1200.0, 900.0, 800.0, 600.0, 500.0, 200.0, 180.0, 160.0]

        solid.set_strength_constants(strength)

        assert solid.strength_constants == strength
        assert solid.x1t == pytest.approx(1500.0)
        assert solid.x12 == pytest.approx(160.0)

    def test_typed_material_queries_and_setters(self):
        """Typed material API should cover matrix, thermal, and setter flows."""
        solid = CauchyContinuumModel()
        solid.set_isotropy('iso')
        solid.set_elastic([210e9, 0.3], input_type=ElasticInputType.ISOTROPIC)
        solid.cte = [1e-6, 2e-6, 3e-6, 4e-6, 5e-6, 6e-6]

        assert solid.isotropy == 0
        assert solid.get_matrix_component(
            MatrixKind.STIFFNESS,
            TensorComponent(1, 1),
        ) is not None
        assert solid.get_thermal_expansion(TensorComponent(1, 2)) == pytest.approx(6e-6)

    def test_grouped_views_reflect_current_fields(self):
        """Grouped composition views should expose the current field partitions."""
        solid = CauchyContinuumModel(
            name='Grouped',
            density=1234.0,
            temperature=45.0,
            isotropy=1,
            e1=100e9,
            nu12=0.25,
            x1t=800.0,
            char_len=0.5,
            cte=[1e-6] * 6,
            specific_heat=900.0,
            failure_criterion=4,
        )

        assert solid.definition == MaterialDefinition(
            name='Grouped',
            id=None,
            density=1234.0,
            temperature=45.0,
        )
        assert solid.elastic.isotropy == 1
        assert solid.elastic.e1 == pytest.approx(100e9)
        assert solid.thermal.cte == [1e-6] * 6
        assert solid.thermal.specific_heat == pytest.approx(900.0)
        assert solid.strength.x1t == pytest.approx(800.0)
        assert solid.strength.failure_criterion == 4

    def test_assigning_grouped_components_updates_outer_fields(self):
        """Assigning grouped components should update the legacy outer shell."""
        solid = CauchyContinuumModel()

        solid.definition = MaterialDefinition(
            name='Updated',
            id=7,
            density=2222.0,
            temperature=80.0,
        )
        solid.elastic = LinearElasticBehavior(
            isotropy=0,
            e1=210e9,
            nu12=0.3,
        )
        solid.thermal = ThermalProperties(
            cte=[2e-6] * 6,
            specific_heat=500.0,
            d_thetatheta=10.0,
            f_eff=0.25,
        )
        solid.strength = StrengthProperties(
            x1t=1000.0,
            x1c=900.0,
            x23=120.0,
            strength_measure=1,
            strength_constants=[1000.0, 0.0, 0.0, 900.0, 0.0, 0.0, 120.0, 0.0, 0.0],
            char_len=0.2,
            failure_criterion=4,
        )

        assert solid.name == 'Updated'
        assert solid.id == 7
        assert solid.density == pytest.approx(2222.0)
        assert solid.temperature == pytest.approx(80.0)
        assert solid.isotropy == 0
        assert solid.e1 == pytest.approx(210e9)
        assert solid.nu12 == pytest.approx(0.3)
        assert solid.stff is not None
        assert solid.cte == [2e-6] * 6
        assert solid.specific_heat == pytest.approx(500.0)
        assert solid.d_thetatheta == pytest.approx(10.0)
        assert solid.f_eff == pytest.approx(0.25)
        assert solid.x1t == pytest.approx(1000.0)
        assert solid.x1c == pytest.approx(900.0)
        assert solid.x23 == pytest.approx(120.0)
        assert solid.strength_measure == 1
        assert solid.char_len == pytest.approx(0.2)
        assert solid.failure_criterion == 4


