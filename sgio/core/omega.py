"""Omega: the SG measure along the dimensions it shares with the macro model.

SwiftComp describes a 3D SG with the local coordinates ``(y1, y2, y3)``, a 2D
SG with ``(y2, y3)`` and a 1D SG with ``(y3)``, while the macro model spans
``y1, y2, y3`` for a 3D model, ``y1, y2`` for a plate/shell model and ``y1``
for a beam model. ``omega`` is the SG's measure over the coordinates the two
share, so it is the product of the SG's first ``sgdim + smdim - 3`` extents.
"""

from __future__ import annotations

import numpy as np

# Source-mesh axis indices for each SG coordinate, in the order they are
# written. A 3D SG writes all three axes, so ``model_space`` does not apply.
MODEL_SPACE_AXES: dict[int, dict[str, tuple[int, ...]]] = {
    1: {"x": (0,), "y": (1,), "z": (2,)},
    2: {"xy": (0, 1), "yz": (1, 2), "zx": (2, 0)},
    3: {"": (0, 1, 2)},
}


def model_space_axes(sgdim: int, model_space: str) -> tuple[int, ...]:
    """Return the source-mesh axes an SG writes, in written order.

    Parameters
    ----------
    sgdim : int
        Structure-gene dimension.
    model_space : str
        Mapping from the input mesh axes to the SG axes. Ignored for
        ``sgdim=3``.

    Returns
    -------
    tuple of int
        Source-mesh axis indices.

    Raises
    ------
    ValueError
        If ``sgdim`` or ``model_space`` is not supported.
    """
    if sgdim == 3:
        return MODEL_SPACE_AXES[3][""]
    try:
        return MODEL_SPACE_AXES[sgdim][model_space]
    except KeyError:
        raise ValueError(
            f"Invalid model space {model_space!r} for a {sgdim}D SG; expected one "
            f"of {sorted(MODEL_SPACE_AXES.get(sgdim, {}))}."
        ) from None


def compute_omega(
    points: np.ndarray,
    sgdim: int,
    smdim: int,
    model_space: str = "",
) -> float:
    """Compute omega from the SG's bounding box.

    Parameters
    ----------
    points : numpy.ndarray
        Nodal coordinates of the SG mesh, in the source frame.
    sgdim : int
        Structure-gene dimension.
    smdim : int
        Macro structural model dimension (1 = beam, 2 = plate/shell,
        3 = 3D continuum).
    model_space : str, optional
        Mapping from the input mesh axes to the SG axes. Ignored for
        ``sgdim=3``.

    Returns
    -------
    float
        Volume, area or length over the shared dimensions; 1.0 when the SG
        and the macro model share none.

    Raises
    ------
    ValueError
        If the SG and model dimensions are incompatible, or the SG is
        degenerate along a shared dimension.
    """
    num_shared = sgdim + smdim - 3
    if num_shared < 0:
        raise ValueError(
            f"A {sgdim}D SG cannot be used with a {smdim}D macro structural model."
        )
    if num_shared == 0:
        # The SG spans none of the macro model's dimensions (e.g. a 2D
        # cross-sectional SG of a beam).
        return 1.0

    axes = model_space_axes(sgdim, model_space)[:num_shared]
    coordinates = np.asarray(points, dtype=float)[:, list(axes)]
    extents = np.ptp(coordinates, axis=0)
    if np.any(extents <= 0.0):
        raise ValueError(
            f"SG is degenerate along a dimension shared with the macro model: "
            f"bounding-box extents {list(extents)} over source axes {list(axes)}."
        )
    return float(np.prod(extents))
