"""Unit tests for sgio.utils.math error-translation behavior."""

import numpy as np
import pytest

from sgio.utils.math import angle_to_cosine_2d, skew_symmetric_matrix


@pytest.mark.unit
class TestSkewSymmetricMatrix:
    def test_valid_vector(self):
        result = skew_symmetric_matrix([0, 0, 1])
        assert np.array_equal(result, [[0, -1, 0], [1, 0, 0], [0, 0, 0]])

    def test_none_raises_value_error(self):
        with pytest.raises(ValueError):
            skew_symmetric_matrix(None)

    def test_wrong_length_raises_value_error(self):
        with pytest.raises(ValueError):
            skew_symmetric_matrix([1, 2])

    def test_non_iterable_raises_value_error(self):
        with pytest.raises(ValueError):
            skew_symmetric_matrix(1.0)


@pytest.mark.unit
class TestAngleToCosine2D:
    def test_valid_angle(self):
        result = angle_to_cosine_2d(0)
        assert np.allclose(result, [[1.0, 0.0], [0.0, 1.0]])

    def test_none_raises_value_error(self):
        with pytest.raises(ValueError):
            angle_to_cosine_2d(None)

    def test_non_number_raises_value_error(self):
        with pytest.raises(ValueError):
            angle_to_cosine_2d("45")
