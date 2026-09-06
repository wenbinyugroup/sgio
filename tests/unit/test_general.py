"""Unit tests for general model containers."""

import sgio
import sgio.model as sgmodel
import numpy as np
import pytest

from sgio.model.protocols import getModelDim
from sgio.model.state import State, StateCase
from sgio.model.state import StateCase as StateCaseFromModule


class TestModelReExports:
    """Test that the canonical model objects are re-exported consistently."""

    def test_package_re_exports_are_the_same_objects(self):
        """``sgio``, ``sgio.model`` and the defining module must agree."""
        assert StateCase is StateCaseFromModule
        assert sgmodel.StateCase is StateCase
        assert sgmodel.getModelDim is getModelDim
        assert sgio.StateCase is StateCase
        assert sgio.getModelDim is getModelDim


class TestState:
    """Test State point/field data semantics."""

    def test_1d_ndarray_without_entity_ids_is_point_data(self):
        """A flat ndarray should behave like list-backed point data."""
        state = State(data=np.array([1.0, 2.0, 3.0]))

        assert state.is_field_data() is False
        assert state.entity_ids is None
        assert state.data == [1.0, 2.0, 3.0]

    def test_2d_ndarray_without_entity_ids_is_field_data(self):
        """A 2D ndarray should default to field data with sequential IDs."""
        state = State(data=np.array([[1.0, 2.0], [3.0, 4.0]]))

        assert state.is_field_data() is True
        assert np.array_equal(state.entity_ids, np.array([0, 1]))
        assert state.data == {0: [1.0, 2.0], 1: [3.0, 4.0]}

    def test_1d_ndarray_with_entity_ids_is_scalar_field_data(self):
        """Explicit entity IDs should preserve scalar field-data semantics."""
        state = State(
            data=np.array([10.0, 20.0]),
            entity_ids=np.array([5, 9]),
        )

        assert state.is_field_data() is True
        assert np.array_equal(state.entity_ids, np.array([5, 9]))
        assert state.data == {5: 10.0, 9: 20.0}

    def test_ndarray_entity_ids_must_match_first_dimension(self):
        """entity_ids length should match the first array dimension."""
        with pytest.raises(
            ValueError,
            match='entity_ids length must match the first dimension of data',
        ):
            State(data=np.array([[1.0, 2.0], [3.0, 4.0]]), entity_ids=np.array([1]))

    def test_data_setter_keeps_1d_ndarray_as_point_data(self):
        """Assigning a flat ndarray through the setter should keep point semantics."""
        state = State(data={1: [3.0, 4.0]})

        state.data = np.array([7.0, 8.0])

        assert state.is_field_data() is False
        assert state.entity_ids is None
        assert state.data == [7.0, 8.0]


class TestStateCase:
    """Test load-case container semantics."""

    def test_add_state_exposes_convenience_accessors(self):
        """Named states should be available through convenience properties."""
        state_case = StateCase(case={'load_case': 3}, states={})
        state_case.addState(
            name='load',
            state=State(name='load', data=[1.0, 2.0, 3.0], label=['f1', 'f2', 'f3']),
        )
        state_case.addState(
            name='displacement',
            state=State(name='displacement', data=[0.1, 0.2, 0.3], label=['u1', 'u2', 'u3']),
        )

        assert state_case.case['load_case'] == 3
        assert state_case.load is not None
        assert state_case.displacement is not None
        assert state_case.load.data == [1.0, 2.0, 3.0]
        assert state_case.displacement.label == ['u1', 'u2', 'u3']

    def test_to_dictionary_preserves_case_and_states(self):
        """StateCase serialization should preserve metadata and state payloads."""
        state_case = StateCase(case={'station': 9, 'mode': 2}, states={})
        state_case.addState(
            name='rotation',
            state=State(
                name='rotation',
                data=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                label=['c11', 'c12', 'c13', 'c21', 'c22', 'c23', 'c31', 'c32', 'c33'],
            ),
        )

        payload = state_case.toDictionary()

        assert payload['case'] == {'station': 9, 'mode': 2}
        assert payload['states']['rotation']['data'][0] == [1.0, 0.0, 0.0]
        assert payload['states']['rotation']['label'][0] == 'c11'
