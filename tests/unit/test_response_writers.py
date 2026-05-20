"""Unit tests for response writer helpers moved out of ``sgio.model``."""

from __future__ import annotations

from io import StringIO

from sgio.iofunc.common.response_writers import (
    write_section_response_displacement,
    write_section_response_load,
    write_section_response_rotation,
)
from sgio.model.response import SectionResponse


class TestResponseWriters:
    """Test response writer helper functions and compatibility wrappers."""

    def test_write_section_response_displacement_matches_legacy_wrapper(self):
        """Helper function and legacy wrapper should produce the same output."""
        response = SectionResponse()
        response.displacement = [1.0, 2.0, 3.0]

        direct = StringIO()
        wrapper = StringIO()

        write_section_response_displacement(direct, response.displacement)
        response.writeSGInputGlbU(wrapper)

        assert direct.getvalue() == wrapper.getvalue()

    def test_write_section_response_rotation_matches_legacy_wrapper(self):
        """Rotation writer helper should match the legacy object method."""
        response = SectionResponse()
        response.directional_cosine = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]

        direct = StringIO()
        wrapper = StringIO()

        write_section_response_rotation(direct, response.directional_cosine)
        response.writeSGInputGlbC(wrapper)

        assert direct.getvalue() == wrapper.getvalue()

    def test_write_section_response_load_matches_legacy_wrapper(self):
        """Load writer helper should preserve the legacy VABS layout."""
        response = SectionResponse()
        response.load = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        response.distr_load = [0.1] * 6
        response.distr_load_d1 = [0.2] * 6
        response.distr_load_d2 = [0.3] * 6
        response.distr_load_d3 = [0.4] * 6

        direct = StringIO()
        wrapper = StringIO()

        write_section_response_load(
            file=direct,
            load=response.load,
            file_format='vabs',
            load_type=response.load_type,
            distributed_loads=[
                response.distr_load,
                response.distr_load_d1,
                response.distr_load_d2,
                response.distr_load_d3,
            ],
        )
        response.writeSGInputGlbS(wrapper, 'vabs')

        assert direct.getvalue() == wrapper.getvalue()
