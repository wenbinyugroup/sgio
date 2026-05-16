"""Unit tests for general model containers."""

import numpy as np
import pytest

from sgio.model.general import SectionResponse, State, StructureResponseCase, StructureResponseCases


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


class TestStructureResponseCases:
    """Test structured response case containers."""

    def test_add_response_case_stores_objects(self):
        """addResponseCase should create StructureResponseCase objects."""
        cases = StructureResponseCases()
        cases.loc_tags = ['x1']
        cases.cond_tags = ['load_case']

        response = SectionResponse()
        response.load = [1.0, 2.0, 3.0]

        cases.addResponseCase([0.5], [2], response)

        assert len(cases.responses) == 1
        resp_case = cases.responses[0]
        assert isinstance(resp_case, StructureResponseCase)
        assert resp_case.getLocation('x1') == 0.5
        assert resp_case.getCondition('load_case') == 2
        assert resp_case.response is response

    def test_response_case_keeps_legacy_mapping_access(self):
        """StructureResponseCase should remain readable via legacy dict-style access."""
        response = SectionResponse()
        response.load = [10.0]
        resp_case = StructureResponseCase(
            loc={'station': 1},
            cond={'mode': 3},
            response=response,
        )

        assert 'response' in resp_case
        assert 'station' in resp_case
        assert resp_case['response'] is response
        assert resp_case['station'] == 1
        assert resp_case['mode'] == 3

    def test_get_responses_by_loc_cond_handles_object_cases(self):
        """Location/condition filtering should work on object-backed cases."""
        cases = StructureResponseCases()
        cases.loc_tags = ['station']
        cases.cond_tags = ['mode']

        resp_1 = SectionResponse()
        resp_2 = SectionResponse()

        cases.addResponseCase([1], [100], resp_1)
        cases.addResponseCase([2], [200], resp_2)

        found = cases.getResponsesByLocCond(station=2, mode=200)

        assert found == [cases.responses[1]]
        assert found[0].response is resp_2

    def test_get_responses_by_loc_cond_coerces_legacy_dict_cases(self):
        """Filtering should still work if legacy dict payloads are present."""
        cases = StructureResponseCases()
        cases.loc_tags = ['station']
        cases.cond_tags = ['mode']

        response = SectionResponse()
        cases.responses.append({'station': 3, 'mode': 9, 'response': response})

        found = cases.getResponsesByLocCond(station=3, mode=9)

        assert len(found) == 1
        assert isinstance(found[0], StructureResponseCase)
        assert found[0].response is response
