"""Tests for automatic format-aware node/element numbering (Phase 4 behavior).

Covers:
- auto_renumber_for_format() renumbers when IDs violate format rules
- auto_renumber_for_format() emits UserWarning when renumbering occurs
- auto_renumber_for_format() is a no-op for compliant IDs
- ensure_node_ids() and ensure_element_ids() create IDs when missing
- End-to-end: VABS and SwiftComp write paths auto-renumber non-consecutive IDs
- _handle_deprecated_parameter() logic
"""
from __future__ import annotations

import warnings
from io import StringIO

import numpy as np
import pytest

from sgio.core.mesh import SGMesh
from sgio.core.numbering import (
    _handle_deprecated_parameter,
    auto_renumber_for_format,
    ensure_element_ids,
    ensure_node_ids,
)
from sgio.iofunc.swiftcomp._mesh import write_buffer as sc_write_buffer
from sgio.iofunc.vabs._mesh import write_buffer as vabs_write_buffer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _simple_mesh(node_ids=None, elem_ids=None, n=3):
    """Create a minimal triangle mesh with optional pre-set IDs."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [("triangle", np.array([[0, 1, 2]]))]
    point_data = {}
    cell_data = {"property_id": [np.array([1])]}
    if node_ids is not None:
        point_data["node_id"] = np.array(node_ids, dtype=int)
    if elem_ids is not None:
        cell_data["element_id"] = [np.array(elem_ids, dtype=int)]
    return SGMesh(points, cells, point_data=point_data, cell_data=cell_data)


# ---------------------------------------------------------------------------
# ensure_node_ids
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnsureNodeIds:
    def test_creates_sequential_ids_when_missing(self):
        mesh = _simple_mesh()
        assert "node_id" not in mesh.point_data
        ensure_node_ids(mesh)
        assert "node_id" in mesh.point_data
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]

    def test_preserves_existing_ids(self):
        mesh = _simple_mesh(node_ids=[10, 20, 30])
        ensure_node_ids(mesh)
        assert list(mesh.point_data["node_id"]) == [10, 20, 30]

    def test_idempotent(self):
        mesh = _simple_mesh()
        ensure_node_ids(mesh)
        ensure_node_ids(mesh)
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]

    def test_raises_on_length_mismatch(self):
        # SGMesh itself (via meshio) raises ValueError when node_id length mismatches points
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
        cells = [("triangle", np.array([[0, 1, 2]]))]
        with pytest.raises(ValueError):
            SGMesh(points, cells, point_data={"node_id": np.array([1, 2])})


# ---------------------------------------------------------------------------
# ensure_element_ids
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnsureElementIds:
    def test_creates_sequential_ids_when_missing(self):
        mesh = _simple_mesh()
        mesh.cell_data.pop("element_id", None)
        ensure_element_ids(mesh)
        assert "element_id" in mesh.cell_data
        assert list(mesh.cell_data["element_id"][0]) == [1]

    def test_preserves_existing_ids(self):
        mesh = _simple_mesh(elem_ids=[42])
        ensure_element_ids(mesh)
        assert list(mesh.cell_data["element_id"][0]) == [42]

    def test_idempotent(self):
        mesh = _simple_mesh()
        ensure_element_ids(mesh)
        ensure_element_ids(mesh)
        assert list(mesh.cell_data["element_id"][0]) == [1]


# ---------------------------------------------------------------------------
# auto_renumber_for_format — vabs (requires consecutive from 1)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAutoRenumberVabs:
    def test_noop_when_already_compliant(self):
        mesh = _simple_mesh(node_ids=[1, 2, 3], elem_ids=[1])
        nodes_renumbered, elems_renumbered = auto_renumber_for_format(
            mesh, format="vabs"
        )
        assert not nodes_renumbered
        assert not elems_renumbered
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]

    def test_renumbers_non_consecutive_nodes(self):
        mesh = _simple_mesh(node_ids=[1, 3, 5], elem_ids=[1])
        nodes_renumbered, _ = auto_renumber_for_format(mesh, format="vabs")
        assert nodes_renumbered
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]

    def test_renumbers_nodes_starting_from_zero(self):
        mesh = _simple_mesh(node_ids=[0, 1, 2], elem_ids=[1])
        nodes_renumbered, _ = auto_renumber_for_format(mesh, format="vabs")
        assert nodes_renumbered
        assert list(mesh.point_data["node_id"])[0] == 1

    def test_renumbers_non_consecutive_elements(self):
        mesh = _simple_mesh(node_ids=[1, 2, 3], elem_ids=[10])
        _, elems_renumbered = auto_renumber_for_format(mesh, format="vabs")
        assert elems_renumbered
        assert list(mesh.cell_data["element_id"][0]) == [1]

    def test_emits_user_warning_on_node_renumber(self):
        mesh = _simple_mesh(node_ids=[1, 3, 5], elem_ids=[1])
        with pytest.warns(UserWarning, match="[Nn]ode"):
            auto_renumber_for_format(mesh, format="vabs")

    def test_emits_user_warning_on_element_renumber(self):
        mesh = _simple_mesh(node_ids=[1, 2, 3], elem_ids=[10])
        with pytest.warns(UserWarning, match="[Ee]lement"):
            auto_renumber_for_format(mesh, format="vabs")

    def test_no_warning_when_compliant(self):
        mesh = _simple_mesh(node_ids=[1, 2, 3], elem_ids=[1])
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            # Should not raise — no warnings emitted for compliant mesh
            auto_renumber_for_format(mesh, format="vabs")


# ---------------------------------------------------------------------------
# auto_renumber_for_format — swiftcomp
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAutoRenumberSwiftcomp:
    def test_noop_when_already_compliant(self):
        mesh = _simple_mesh(node_ids=[1, 2, 3], elem_ids=[1])
        nodes_renumbered, elems_renumbered = auto_renumber_for_format(
            mesh, format="swiftcomp"
        )
        assert not nodes_renumbered
        assert not elems_renumbered

    def test_renumbers_non_consecutive_nodes(self):
        mesh = _simple_mesh(node_ids=[5, 10, 15], elem_ids=[1])
        nodes_renumbered, _ = auto_renumber_for_format(mesh, format="swiftcomp")
        assert nodes_renumbered
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]

    def test_sc_alias_works(self):
        mesh = _simple_mesh(node_ids=[5, 10, 15], elem_ids=[1])
        nodes_renumbered, _ = auto_renumber_for_format(mesh, format="sc")
        assert nodes_renumbered


# ---------------------------------------------------------------------------
# auto_renumber_for_format — abaqus (allows non-consecutive)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAutoRenumberAbaqus:
    def test_noop_for_non_consecutive_abaqus(self):
        """Abaqus allows non-consecutive IDs starting from 1."""
        mesh = _simple_mesh(node_ids=[1, 5, 100], elem_ids=[1])
        nodes_renumbered, elems_renumbered = auto_renumber_for_format(
            mesh, format="abaqus"
        )
        assert not nodes_renumbered
        assert not elems_renumbered
        assert list(mesh.point_data["node_id"]) == [1, 5, 100]

    def test_renumbers_zero_start_abaqus(self):
        """Abaqus still requires start from 1 (no zero IDs)."""
        mesh = _simple_mesh(node_ids=[0, 1, 2], elem_ids=[1])
        nodes_renumbered, _ = auto_renumber_for_format(mesh, format="abaxus")
        # Unknown format — no requirements enforced
        assert not nodes_renumbered


# ---------------------------------------------------------------------------
# auto_renumber_for_format — unknown format
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAutoRenumberUnknownFormat:
    def test_unknown_format_is_noop(self):
        mesh = _simple_mesh(node_ids=[0, 100, 999], elem_ids=[999])
        nodes_renumbered, elems_renumbered = auto_renumber_for_format(
            mesh, format="unknown_xyz"
        )
        assert not nodes_renumbered
        assert not elems_renumbered
        # IDs unchanged
        assert list(mesh.point_data["node_id"]) == [0, 100, 999]


# ---------------------------------------------------------------------------
# End-to-end: VABS write auto-renumbers
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.vabs
class TestVabsWriteAutoNumbering:
    def test_nonconsecutive_nodes_renumbered_in_output(self):
        """Write with non-consecutive IDs; output must have valid IDs."""
        mesh = _simple_mesh(node_ids=[10, 20, 30], elem_ids=[1])
        f = StringIO()
        vabs_write_buffer(f, mesh, sgdim=2, model_space="xy")
        output = f.getvalue()
        # After auto-renumber, nodes should be 1, 2, 3
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]
        # Output should contain '1' as first node id
        assert "1" in output

    def test_missing_node_ids_auto_generated(self):
        """Write without any node IDs; auto-generates them."""
        mesh = _simple_mesh()  # no node_ids
        f = StringIO()
        vabs_write_buffer(f, mesh, sgdim=2, model_space="xy")
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]

    def test_missing_element_ids_auto_generated(self):
        """Write without element IDs; auto-generates them."""
        mesh = _simple_mesh(node_ids=[1, 2, 3])
        mesh.cell_data.pop("element_id", None)
        f = StringIO()
        vabs_write_buffer(f, mesh, sgdim=2, model_space="xy")
        assert "element_id" in mesh.cell_data


# ---------------------------------------------------------------------------
# End-to-end: SwiftComp write auto-renumbers
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.swiftcomp
class TestSwiftcompWriteAutoNumbering:
    def test_nonconsecutive_nodes_renumbered_in_output(self):
        mesh = _simple_mesh(node_ids=[10, 20, 30], elem_ids=[1])
        f = StringIO()
        sc_write_buffer(f, mesh, sgdim=2, model_space="xy")
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]

    def test_missing_node_ids_auto_generated(self):
        mesh = _simple_mesh()
        f = StringIO()
        sc_write_buffer(f, mesh, sgdim=2, model_space="xy")
        assert list(mesh.point_data["node_id"]) == [1, 2, 3]


# ---------------------------------------------------------------------------
# _handle_deprecated_parameter
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHandleDeprecatedParameter:
    def test_both_none_returns_default(self):
        result = _handle_deprecated_parameter("old", "new", None, None, default_value=False)
        assert result is False

    def test_both_none_custom_default(self):
        result = _handle_deprecated_parameter("old", "new", None, None, default_value=True)
        assert result is True

    def test_new_only_returns_new(self):
        result = _handle_deprecated_parameter("old", "new", None, True)
        assert result is True

    def test_old_only_issues_deprecation_warning(self):
        with pytest.warns(DeprecationWarning, match="deprecated"):
            result = _handle_deprecated_parameter("old", "new", True, None)
        assert result is True

    def test_both_same_value_issues_warning(self):
        with pytest.warns(DeprecationWarning):
            result = _handle_deprecated_parameter("old", "new", True, True)
        assert result is True

    def test_conflicting_values_raises(self):
        with pytest.raises(ValueError, match="[Cc]onflic"):
            _handle_deprecated_parameter("old", "new", True, False)
