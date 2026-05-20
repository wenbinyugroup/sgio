from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Orientation:
    """Placeholder FE orientation object.

    Parameters
    ----------
    name : str
        Orientation name.
    angle : float, optional
        Simple scalar orientation angle in degrees.
    extras : dict[str, Any], optional
        Additional adapter-specific metadata.
    """

    name: str
    angle: float = 0.0
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class Section:
    """Finite-element section definition for SG material regions.

    Parameters
    ----------
    name : str
        Section name.
    material : str
        Material name referenced from ``FEModel.materials``.
    orientation : float, optional
        In-plane material orientation angle in degrees.
    property_id : int or None, optional
        Property/layer identifier used by mesh cell data and legacy
        ``mocombos`` compatibility APIs.
    extras : dict[str, Any], optional
        Additional adapter-specific metadata.
    """

    name: str
    material: str
    orientation: float = 0.0
    property_id: int | None = None
    extras: dict[str, Any] = field(default_factory=dict)
