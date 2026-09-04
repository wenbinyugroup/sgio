"""Unit tests for the Abaqus parser layer."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import pytest

from sgio._vendors.inprw.inpRW import inpRW
from sgio.iofunc.abaqus.parser import (
    STRUCTURAL_KEYWORDS,
    _extract_structural_blocks,
    _serialize_block,
    parse_input_file,
)


@pytest.mark.unit
def test_parse_input_file_returns_inprw_payload(abaqus_test_files):
    """Parser should wrap ``inpRW`` and preserve caller context."""
    fixture = abaqus_test_files["root"] / "sg2_min.inp"

    payload = parse_input_file(str(fixture), sgdim=2, model="PL1")

    assert payload["filename"] == str(fixture)
    assert payload["sgdim"] == 2
    assert payload["model"] == "PL1"
    assert hasattr(payload["inprw"], "nd")
    assert len(payload["inprw"].nd) > 0


_STRUCTURAL_KEYWORDS_INPUT = """*Heading
test
*Node
1, 0.0, 0.0, 0.0
2, 1.0, 0.0, 0.0
*Element, type=T3D2
1, 1, 2
*Boundary
1, 1, 3
2, 2
*Cload
1, 1, 100.0
*Dload
1, GRAV, 9.81, 0., 0., -1.
*Step, name=Step-1
*Static
1., 1., 1e-05, 1.
*End Step
"""


def _parse_structural_keywords_fixture(tmp_path) -> inpRW:
    """Parse a minimal input covering all four STRUCTURAL_KEYWORDS blocks."""
    filename = tmp_path / "structural_keywords.inp"
    filename.write_text(_STRUCTURAL_KEYWORDS_INPUT)

    parser = inpRW(str(filename))
    buf = io.StringIO()
    with redirect_stdout(buf):
        parser.parse()
    return parser


@pytest.mark.unit
class TestSerializeBlockCharacterization:
    """Characterizes the actual inpRW shapes for STRUCTURAL_KEYWORDS blocks.

    ``block.parameter`` is a ``csid`` mapping and ``block.data`` is a list of
    rows of wrapped scalars (``inpInt``/``inpDecimal``/``inpString``) for all
    four keywords -- never a ``Mesh`` instance (that shape is only used for
    ``*Node``/``*Element``, which are not in STRUCTURAL_KEYWORDS). ``*Step``
    data is an empty list, not something that raises on iteration.
    """

    def test_boundary_block_serializes_tabular_data(self, tmp_path):
        parser = _parse_structural_keywords_fixture(tmp_path)
        block = parser.findKeyword("boundary", printOutput=False)[0]

        result = _serialize_block(block)

        assert result["keyword"] == "Boundary"
        assert result["parameters"] == {}
        assert result["data"] == [[1, 1, 3], [2, 2]]

    def test_cload_block_serializes_tabular_data(self, tmp_path):
        """Note: inpRW's decimal cells (``inpDecimal``, a ``Decimal``
        subclass) are not caught by any isinstance branch in ``_scalar``, so
        they fall through to its str() catch-all -- '100.0', not 100.0. This
        is a pre-existing quirk of ``_scalar``, out of scope for the
        exception-handling fix under test here; characterized as-is."""
        parser = _parse_structural_keywords_fixture(tmp_path)
        block = parser.findKeyword("cload", printOutput=False)[0]

        result = _serialize_block(block)

        assert result["data"] == [[1, 1, "100.0"]]

    def test_dload_block_serializes_tabular_data(self, tmp_path):
        parser = _parse_structural_keywords_fixture(tmp_path)
        block = parser.findKeyword("dload", printOutput=False)[0]

        result = _serialize_block(block)

        assert result["data"] == [[1, "GRAV", "9.81", "0.", "0.", "-1."]]

    def test_step_block_has_parameters_but_empty_data(self, tmp_path):
        """*Step's own data list is empty; its content lives in nested
        keyword blocks (*Static, *End Step, ...), not block.data."""
        parser = _parse_structural_keywords_fixture(tmp_path)
        block = parser.findKeyword("step", printOutput=False)[0]

        result = _serialize_block(block)

        assert result["keyword"] == "Step"
        assert result["parameters"] == {"name": "Step-1"}
        assert result["data"] == []

    def test_serialize_block_raises_with_keyword_when_data_is_not_iterable(self):
        """A block whose .data genuinely cannot be walked must raise a clear,
        keyword-tagged error instead of silently producing an empty block."""

        class _FakeParameter:
            def __iter__(self):
                return iter(())

        class _FakeBlock:
            name = "Step"
            parameter = _FakeParameter()
            data = None  # not iterable

        with pytest.raises(ValueError, match=r"data.*Step"):
            _serialize_block(_FakeBlock())

    def test_serialize_block_raises_with_keyword_when_parameter_is_not_iterable(self):
        class _FakeBlock:
            name = "Boundary"
            parameter = None  # not iterable
            data = []

        with pytest.raises(ValueError, match=r"parameters.*Boundary"):
            _serialize_block(_FakeBlock())


@pytest.mark.unit
def test_extract_structural_blocks_covers_all_four_keywords(tmp_path):
    parser = _parse_structural_keywords_fixture(tmp_path)

    blocks = _extract_structural_blocks(parser)

    assert set(blocks) == set(STRUCTURAL_KEYWORDS)
    assert blocks["boundary"][0]["data"] == [[1, 1, 3], [2, 2]]
    assert blocks["step"][0]["parameters"] == {"name": "Step-1"}


@pytest.mark.unit
def test_extract_structural_blocks_skips_one_bad_block_without_failing_the_rest(
    tmp_path, monkeypatch,
):
    """One block that cannot be serialized must not take down the others --
    ``extras`` is a best-effort, non-lossy fallback, not a strict validator."""
    parser = _parse_structural_keywords_fixture(tmp_path)

    real_serialize_block = _serialize_block

    def _fail_on_step(block):
        if str(getattr(block, "name", "")) == "Step":
            raise ValueError("Cannot serialize data of Abaqus '*Step' block: boom")
        return real_serialize_block(block)

    monkeypatch.setattr(
        "sgio.iofunc.abaqus.parser._serialize_block", _fail_on_step
    )

    blocks = _extract_structural_blocks(parser)

    assert "step" not in blocks
    assert blocks["boundary"][0]["data"] == [[1, 1, 3], [2, 2]]
    assert blocks["cload"][0]["data"] == [[1, 1, "100.0"]]
    assert blocks["dload"][0]["data"] == [[1, "GRAV", "9.81", "0.", "0.", "-1."]]
