"""Unit tests for failure criteria."""

import numpy as np
import pytest
from sgio.model.failure import TsaiWuFailureCriterion


class TestTsaiWuFailureCriterion:
    """Test suite for Tsai-Wu failure criterion."""

    @pytest.fixture
    def typical_composite(self):
        """Create a typical composite material with Tsai-Wu criterion.
        
        Typical carbon fiber composite properties.
        """
        return TsaiWuFailureCriterion(
            xt=1500.0,  # MPa - tensile strength in x
            xc=1200.0,  # MPa - compressive strength in x
            yt=50.0,    # MPa - tensile strength in y
            yc=150.0,   # MPa - compressive strength in y
            zt=50.0,    # MPa - tensile strength in z
            zc=150.0,   # MPa - compressive strength in z
            r=70.0,     # MPa - shear strength yz
            t=70.0,     # MPa - shear strength xz
            s=70.0      # MPa - shear strength xy
        )

    @pytest.fixture
    def isotropic_material(self):
        """Create an isotropic material for simpler testing."""
        return TsaiWuFailureCriterion(
            xt=100.0,
            xc=100.0,
            yt=100.0,
            yc=100.0,
            zt=100.0,
            zc=100.0,
            r=50.0,
            t=50.0,
            s=50.0
        )

    def test_initialization(self, typical_composite):
        """Test that the criterion initializes correctly."""
        assert typical_composite.xt == 1500.0
        assert typical_composite.xc == 1200.0
        assert typical_composite.A.shape == (6, 6)
        assert typical_composite.b.shape == (6,)

    def test_failure_index_zero_stress(self, typical_composite):
        """Test failure index with zero stress."""
        stress = np.zeros(6)
        fi = typical_composite.failure_index(stress)
        assert fi == pytest.approx(0.0, abs=1e-10)

    def test_failure_index_single_stress(self, typical_composite):
        """Test failure index with a single stress vector."""
        # Stress below failure
        stress = np.array([100.0, 10.0, 10.0, 5.0, 5.0, 5.0])
        fi = typical_composite.failure_index(stress)
        assert isinstance(fi, (float, np.floating))
        assert fi >= 0.0

    def test_failure_index_multiple_stresses(self, typical_composite):
        """Test failure index with multiple stress vectors."""
        stresses = np.array([
            [100.0, 10.0, 10.0, 5.0, 5.0, 5.0],
            [200.0, 20.0, 20.0, 10.0, 10.0, 10.0],
            [50.0, 5.0, 5.0, 2.0, 2.0, 2.0]
        ])
        fi = typical_composite.failure_index(stresses)
        assert fi.shape == (3,)
        assert np.all(fi >= 0.0)

    def test_failure_index_at_failure(self, isotropic_material):
        """Test that failure index equals 1.0 at failure stress."""
        # Pure tensile stress at failure
        stress = np.array([100.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        fi = isotropic_material.failure_index(stress)
        assert fi == pytest.approx(1.0, rel=1e-6)

    def test_strength_ratio_zero_stress(self, typical_composite):
        """Test strength ratio with zero stress."""
        stress = np.array([1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10])
        sr = typical_composite.strength_ratio(stress)
        # Should be very large for very small stress
        assert sr > 1000.0

    def test_strength_ratio_single_stress(self, typical_composite):
        """Test strength ratio with a single stress vector."""
        stress = np.array([100.0, 10.0, 10.0, 5.0, 5.0, 5.0])
        sr = typical_composite.strength_ratio(stress)
        assert isinstance(sr, (float, np.floating))
        assert sr > 0.0

    def test_strength_ratio_multiple_stresses(self, typical_composite):
        """Test strength ratio with multiple stress vectors."""
        stresses = np.array([
            [100.0, 10.0, 10.0, 5.0, 5.0, 5.0],
            [200.0, 20.0, 20.0, 10.0, 10.0, 10.0],
            [50.0, 5.0, 5.0, 2.0, 2.0, 2.0]
        ])
        sr = typical_composite.strength_ratio(stresses)
        assert sr.shape == (3,)
        assert np.all(sr > 0.0)

    def test_strength_ratio_at_failure(self, isotropic_material):
        """Test that strength ratio equals 1.0 at failure stress."""
        # Pure tensile stress at failure
        stress = np.array([100.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        sr = isotropic_material.strength_ratio(stress)
        assert sr == pytest.approx(1.0, rel=1e-6)

    def test_strength_ratio_consistency(self, typical_composite):
        """Test consistency between failure index and strength ratio."""
        stress = np.array([100.0, 10.0, 10.0, 5.0, 5.0, 5.0])
        sr = typical_composite.strength_ratio(stress)
        
        # At failure, stress * SR should give FI = 1.0
        failure_stress = stress * sr
        fi = typical_composite.failure_index(failure_stress)
        assert fi == pytest.approx(1.0, rel=1e-5)

    def test_vectorization_performance(self, typical_composite):
        """Test that vectorization works for large arrays."""
        n = 1000
        stresses = np.random.rand(n, 6) * 100

        # Should handle large arrays efficiently
        fi = typical_composite.failure_index(stresses)
        sr = typical_composite.strength_ratio(stresses)

        assert fi.shape == (n,)
        assert sr.shape == (n,)
        assert np.all(fi >= 0.0)
        assert np.all(sr > 0.0)

    def test_pure_tensile_x(self, typical_composite):
        """Test pure tensile stress in x-direction."""
        stress = np.array([1500.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        fi = typical_composite.failure_index(stress)
        sr = typical_composite.strength_ratio(stress)

        # At tensile strength, FI should be ~1.0
        assert fi == pytest.approx(1.0, rel=1e-5)
        assert sr == pytest.approx(1.0, rel=1e-5)

    def test_pure_compressive_x(self, typical_composite):
        """Test pure compressive stress in x-direction."""
        stress = np.array([-1200.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        fi = typical_composite.failure_index(stress)
        sr = typical_composite.strength_ratio(stress)

        # At compressive strength, FI should be ~1.0
        assert fi == pytest.approx(1.0, rel=1e-5)
        assert sr == pytest.approx(1.0, rel=1e-5)

    def test_pure_shear_xy(self, typical_composite):
        """Test pure shear stress in xy-plane."""
        stress = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 70.0])
        fi = typical_composite.failure_index(stress)
        sr = typical_composite.strength_ratio(stress)

        # At shear strength, FI should be ~1.0
        assert fi == pytest.approx(1.0, rel=1e-5)
        assert sr == pytest.approx(1.0, rel=1e-5)

    def test_combined_stress(self, typical_composite):
        """Test combined stress state."""
        # Stress below failure
        stress = np.array([500.0, 20.0, 20.0, 10.0, 10.0, 10.0])
        fi = typical_composite.failure_index(stress)
        sr = typical_composite.strength_ratio(stress)

        # Should be safe (FI < 1, SR > 1)
        assert fi < 1.0
        assert sr > 1.0

    def test_negative_stresses(self, typical_composite):
        """Test with negative (compressive) stresses."""
        stress = np.array([-500.0, -30.0, -30.0, 5.0, 5.0, 5.0])
        fi = typical_composite.failure_index(stress)
        sr = typical_composite.strength_ratio(stress)

        # Failure index can be negative for safe stress states
        # Failure occurs when FI >= 1.0
        assert fi < 1.0  # Should be safe
        assert sr > 0.0

    def test_mixed_stress_signs(self, typical_composite):
        """Test with mixed tension and compression."""
        stress = np.array([300.0, -40.0, 10.0, -5.0, 8.0, -3.0])
        fi = typical_composite.failure_index(stress)
        sr = typical_composite.strength_ratio(stress)

        # Failure index can be negative for safe stress states
        # Failure occurs when FI >= 1.0
        assert fi < 1.0  # Should be safe
        assert sr > 0.0

    def test_batch_consistency(self, typical_composite):
        """Test that batch processing gives same results as individual."""
        stresses = np.array([
            [100.0, 10.0, 10.0, 5.0, 5.0, 5.0],
            [200.0, 20.0, 20.0, 10.0, 10.0, 10.0],
            [50.0, 5.0, 5.0, 2.0, 2.0, 2.0]
        ])

        # Batch processing
        fi_batch = typical_composite.failure_index(stresses)
        sr_batch = typical_composite.strength_ratio(stresses)

        # Individual processing
        for i in range(3):
            fi_single = typical_composite.failure_index(stresses[i])
            sr_single = typical_composite.strength_ratio(stresses[i])

            assert fi_batch[i] == pytest.approx(fi_single, rel=1e-10)
            assert sr_batch[i] == pytest.approx(sr_single, rel=1e-10)

    def test_strength_ratio_inverse_relationship(self, typical_composite):
        """Test that higher stress gives lower strength ratio."""
        stress_low = np.array([100.0, 10.0, 10.0, 5.0, 5.0, 5.0])
        stress_high = np.array([200.0, 20.0, 20.0, 10.0, 10.0, 10.0])

        sr_low = typical_composite.strength_ratio(stress_low)
        sr_high = typical_composite.strength_ratio(stress_high)

        # Higher stress should have lower strength ratio
        assert sr_low > sr_high

    def test_failure_index_proportional_relationship(self, typical_composite):
        """Test that higher stress gives higher failure index."""
        stress_low = np.array([100.0, 10.0, 10.0, 5.0, 5.0, 5.0])
        stress_high = np.array([200.0, 20.0, 20.0, 10.0, 10.0, 10.0])

        fi_low = typical_composite.failure_index(stress_low)
        fi_high = typical_composite.failure_index(stress_high)

        # Higher stress should have higher failure index
        assert fi_high > fi_low

