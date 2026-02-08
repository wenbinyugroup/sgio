"""Test format requirements registry.

Phase 4.1 introduces a registry describing numbering constraints per format.
"""

import pytest

from sgio.core.format_requirements import (
    REQUIREMENTS,
    FORMAT_ALIASES,
    get_numbering_requirements,
    normalize_format_name,
)


@pytest.mark.unit
def test_normalize_format_name_handles_aliases():
    """Aliases should normalize to canonical names."""
    assert normalize_format_name("sc") == "swiftcomp"
    assert normalize_format_name(" SwiftComp ") == "swiftcomp"


@pytest.mark.unit
def test_requirements_registry_contains_expected_keys():
    """Registry should include canonical formats and documented aliases."""
    assert "vabs" in REQUIREMENTS
    assert "swiftcomp" in REQUIREMENTS
    assert "abaqus" in REQUIREMENTS
    assert "gmsh" in REQUIREMENTS

    # Alias keys
    for alias in FORMAT_ALIASES:
        assert alias in REQUIREMENTS


@pytest.mark.unit
def test_get_numbering_requirements_returns_canonical_only():
    """get_numbering_requirements should return canonical requirement objects."""
    sc_req = get_numbering_requirements("sc")
    swift_req = get_numbering_requirements("swiftcomp")
    assert sc_req is swift_req

    vabs_req = get_numbering_requirements("vabs")
    assert vabs_req is not None
    assert vabs_req.nodes_consecutive is True
    assert vabs_req.nodes_start_from == 1
    assert vabs_req.elements_consecutive is True
    assert vabs_req.elements_start_from == 1


@pytest.mark.unit
def test_get_numbering_requirements_unknown_returns_none():
    """Unknown formats should return None (no enforced requirements)."""
    assert get_numbering_requirements("unknown") is None
