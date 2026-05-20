"""Utilities for element property reference coordinate systems.

The internal SG representation stores one local coordinate system per element
as nine floating-point values ``(a1, a2, a3, b1, b2, b3, c1, c2, c3)``:

* ``c`` is the origin point of the local system.
* ``a`` is a point on the positive local ``y1`` axis, so ``a - c`` defines
  the ``y1`` direction.
* ``b`` is another point in the ``y1-y2`` plane that is not collinear with
  ``a - c``.  ``(a - c) x (b - c)`` defines the positive local ``y3`` axis,
  and ``y2`` follows from the right-handed system.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np


VABS_REFERENCE_POINT_A = np.array([1.0, 0.0, 0.0], dtype=float)
VABS_REFERENCE_POINT_C = np.array([0.0, 0.0, 0.0], dtype=float)
_EPS = 1.0e-12


def normalize_property_ref_csys(csys: Iterable[float]) -> np.ndarray:
    """Return one local-coordinate-system payload as a flat 9-value array.

    Parameters
    ----------
    csys : iterable of float
        Sequence storing ``(a, b, c)`` point coordinates.

    Returns
    -------
    numpy.ndarray
        Flat array with shape ``(9,)``.

    Raises
    ------
    ValueError
        If the input does not contain exactly 9 numeric values.
    """
    array = np.asarray(csys, dtype=float).reshape(-1)
    if array.size != 9:
        raise ValueError(
            "property_ref_csys must contain exactly 9 values "
            f"(got shape {np.asarray(csys).shape})."
        )
    return array


def property_ref_csys_to_axes(csys: Iterable[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert one ``property_ref_csys`` payload to orthonormal local axes.

    Parameters
    ----------
    csys : iterable of float
        Flat 9-value ``(a, b, c)`` point payload.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]
        Local axis unit vectors ``(y1, y2, y3)``.

    Raises
    ------
    ValueError
        If the point definition is degenerate.
    """
    array = normalize_property_ref_csys(csys)
    point_a = array[0:3]
    point_b = array[3:6]
    point_c = array[6:9]

    vector_ca = point_a - point_c
    norm_ca = np.linalg.norm(vector_ca)
    if norm_ca <= _EPS:
        raise ValueError("Invalid property_ref_csys: points a and c must be distinct.")
    axis_y1 = vector_ca / norm_ca

    vector_cb = point_b - point_c
    normal_y3 = np.cross(axis_y1, vector_cb)
    norm_y3 = np.linalg.norm(normal_y3)
    if norm_y3 <= _EPS:
        raise ValueError(
            "Invalid property_ref_csys: points a, b, and c must not be collinear."
        )
    axis_y3 = normal_y3 / norm_y3

    axis_y2 = np.cross(axis_y3, axis_y1)
    norm_y2 = np.linalg.norm(axis_y2)
    if norm_y2 <= _EPS:
        raise ValueError("Invalid property_ref_csys: failed to construct local y2 axis.")
    axis_y2 = axis_y2 / norm_y2

    return axis_y1, axis_y2, axis_y3


def vabs_theta_to_property_ref_csys(theta_deg: float) -> np.ndarray:
    """Build the internal 9-value representation from a VABS ``theta_1`` angle.

    Parameters
    ----------
    theta_deg : float
        VABS sectional material angle in degrees. The cross-section lies in the
        global ``x2-x3`` plane, so the local ``y1`` axis is always aligned with
        global ``x1``.

    Returns
    -------
    numpy.ndarray
        Flat 9-value ``(a, b, c)`` payload.
    """
    theta_rad = np.deg2rad(float(theta_deg))
    point_a = VABS_REFERENCE_POINT_A
    point_b = np.array([0.0, np.cos(theta_rad), np.sin(theta_rad)], dtype=float)
    point_c = VABS_REFERENCE_POINT_C
    return np.concatenate((point_a, point_b, point_c))


def property_ref_csys_to_vabs_theta(csys: Iterable[float]) -> float:
    """Convert one internal 9-value representation to a VABS ``theta_1`` angle.

    Parameters
    ----------
    csys : iterable of float
        Flat 9-value ``(a, b, c)`` point payload.

    Returns
    -------
    float
        VABS ``theta_1`` angle in degrees.
    """
    _, axis_y2, _ = property_ref_csys_to_axes(csys)
    theta_deg = float(np.rad2deg(np.arctan2(axis_y2[2], axis_y2[1])))
    if abs(theta_deg) <= _EPS:
        return 0.0
    return theta_deg


def property_ref_value_to_vabs_theta(value: object) -> float:
    """Convert a stored reference-csys value to VABS ``theta_1``.

    Accepts either the new 9-value representation or a legacy scalar angle.

    Parameters
    ----------
    value : object
        Stored cell-data value.

    Returns
    -------
    float
        VABS ``theta_1`` angle in degrees.
    """
    array = np.asarray(value, dtype=float)
    if array.ndim == 0:
        theta_deg = float(array)
        return 0.0 if abs(theta_deg) <= _EPS else theta_deg
    return property_ref_csys_to_vabs_theta(array.reshape(-1))


def build_property_ref_axis_cell_data(
    cell_csys_blocks: list[Iterable[Iterable[float]]],
) -> dict[str, list[np.ndarray]]:
    """Derive Gmsh-ready local axis vectors from ``property_ref_csys`` blocks.

    Parameters
    ----------
    cell_csys_blocks : list
        Cell-block-major ``property_ref_csys`` payload.

    Returns
    -------
    dict[str, list[numpy.ndarray]]
        Three cell-data fields named ``property_ref_axis_y1``,
        ``property_ref_axis_y2``, and ``property_ref_axis_y3``. Each value is a
        list of ``(n_elements, 3)`` arrays, one per cell block.
    """
    axis_blocks = {
        "property_ref_axis_y1": [],
        "property_ref_axis_y2": [],
        "property_ref_axis_y3": [],
    }

    for block in cell_csys_blocks:
        axis_y1_rows = []
        axis_y2_rows = []
        axis_y3_rows = []
        for csys in block:
            axis_y1, axis_y2, axis_y3 = property_ref_csys_to_axes(csys)
            axis_y1_rows.append(axis_y1)
            axis_y2_rows.append(axis_y2)
            axis_y3_rows.append(axis_y3)

        axis_blocks["property_ref_axis_y1"].append(np.asarray(axis_y1_rows, dtype=float))
        axis_blocks["property_ref_axis_y2"].append(np.asarray(axis_y2_rows, dtype=float))
        axis_blocks["property_ref_axis_y3"].append(np.asarray(axis_y3_rows, dtype=float))

    return axis_blocks
