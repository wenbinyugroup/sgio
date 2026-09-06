"""Unit tests for response writer helpers moved out of ``sgio.model``."""

from __future__ import annotations

from io import StringIO

from sgio.iofunc.common.response_writers import (
    write_section_response_displacement,
    write_section_response_load,
    write_section_response_rotation,
)


class TestResponseWriters:
    """Test the SG input response writer helpers."""

    def test_write_section_response_displacement(self):
        """Displacement is written as one row of formatted floats."""
        buffer = StringIO()

        write_section_response_displacement(buffer, [1.0, 2.0, 3.0])

        assert buffer.getvalue() == (
            "    1.000000e+00    2.000000e+00    3.000000e+00\n"
            "\n"
        )

    def test_write_section_response_rotation(self):
        """Rotation is written as three rows of direction cosines."""
        buffer = StringIO()

        write_section_response_rotation(
            buffer,
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        )

        assert buffer.getvalue() == (
            "    1.000000e+00    0.000000e+00    0.000000e+00\n"
            "    0.000000e+00    1.000000e+00    0.000000e+00\n"
            "    0.000000e+00    0.000000e+00    1.000000e+00\n"
            "\n"
        )

    def test_write_section_response_load_uses_vabs_layout(self):
        """VABS load layout reorders components and appends distributed loads."""
        buffer = StringIO()

        write_section_response_load(
            file=buffer,
            load=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            file_format="vabs",
            load_type=0,
            distributed_loads=[[0.1] * 6, [0.2] * 6, [0.3] * 6, [0.4] * 6],
        )

        assert buffer.getvalue() == (
            "    1.000000e+00    4.000000e+00    5.000000e+00    6.000000e+00\n"
            "    2.000000e+00    3.000000e+00\n"
            "\n"
            "    1.000000e-01    1.000000e-01    1.000000e-01"
            "    1.000000e-01    1.000000e-01    1.000000e-01\n"
            "    2.000000e-01    2.000000e-01    2.000000e-01"
            "    2.000000e-01    2.000000e-01    2.000000e-01\n"
            "    3.000000e-01    3.000000e-01    3.000000e-01"
            "    3.000000e-01    3.000000e-01    3.000000e-01\n"
            "    4.000000e-01    4.000000e-01    4.000000e-01"
            "    4.000000e-01    4.000000e-01    4.000000e-01\n"
            "\n"
        )
