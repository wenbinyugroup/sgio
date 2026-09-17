"""Unit tests for `sgio.core.omega`.

Omega is the SG's measure over the dimensions it shares with the macro
structural model, so it depends on the (sgdim, smdim) pair rather than on
either one alone: the same 3D SG is a volume for a 3D model, an area for a
plate model and a length for a beam model.
"""

from __future__ import annotations

import numpy as np
import pytest

from sgio.core.omega import compute_omega, model_space_axes


# A box spanning 2 x 3 x 5 along the source x, y, z axes.
_BOX = np.array(
    [
        [0.0, 0.0, 0.0],
        [2.0, 0.0, 0.0],
        [2.0, 3.0, 0.0],
        [0.0, 3.0, 0.0],
        [0.0, 0.0, 5.0],
        [2.0, 3.0, 5.0],
    ]
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "sgdim, smdim, model_space, expected",
    [
        # 3D SG writes (y1, y2, y3) = (x, y, z).
        (3, 3, "", 2.0 * 3.0 * 5.0),   # all three shared -> volume
        (3, 2, "", 2.0 * 3.0),         # in-plane y1, y2 -> area
        (3, 1, "", 2.0),               # beam axis y1 -> length
        # 2D SG writes (y2, y3); 'xy' maps them to source x, y.
        (2, 3, "xy", 2.0 * 3.0),       # both shared -> area
        (2, 2, "xy", 2.0),             # only y2 shared -> length
        (2, 1, "xy", 1.0),             # cross section of a beam -> none shared
        # 1D SG writes (y3); 'z' maps it to source z.
        (1, 3, "z", 5.0),              # thickness -> length
        (1, 2, "z", 1.0),              # plate normal only -> none shared
    ],
)
def test_compute_omega_covers_every_sg_model_pair(sgdim, smdim, model_space, expected):
    """Each (sgdim, smdim) pair measures exactly its shared dimensions."""
    assert compute_omega(_BOX, sgdim, smdim, model_space) == pytest.approx(expected)


@pytest.mark.unit
def test_compute_omega_follows_model_space_axis_choice():
    """model_space decides which source axes a 2D SG actually spans."""
    assert compute_omega(_BOX, 2, 3, "yz") == pytest.approx(3.0 * 5.0)
    assert compute_omega(_BOX, 2, 3, "zx") == pytest.approx(5.0 * 2.0)


@pytest.mark.unit
def test_compute_omega_rejects_1d_sg_with_beam_model():
    """A 1D SG shares no dimension with a beam model; the pair is invalid."""
    with pytest.raises(ValueError, match="cannot be used with"):
        compute_omega(_BOX, 1, 1, "z")


@pytest.mark.unit
def test_compute_omega_rejects_degenerate_shared_dimension():
    """A flat SG would yield omega=0 and divide SwiftComp's averaging by zero."""
    flat = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 0.0, 5.0]])

    with pytest.raises(ValueError, match="degenerate"):
        compute_omega(flat, 3, 3, "")


@pytest.mark.unit
def test_model_space_axes_rejects_invalid_model_space():
    """An unusable model_space must be named, not silently mapped."""
    with pytest.raises(ValueError, match="Invalid model space"):
        model_space_axes(2, "xz")
