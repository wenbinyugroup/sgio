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
        Internal element->section binding key. It is the integer that tags each
        element in ``mesh.cell_data["property_id"]`` and keys the legacy
        ``mocombos`` view; sections read from a mesh are created from it. It is
        an internal implementation detail, not a user-authored field and not
        part of the public SG-on-Gmsh serialization contract (the sidecars use
        ``name``/``id``, never ``property_id``). For the id a section carried in
        a specific solver file, use :attr:`source_ids` instead.
    source_ids : dict[str, int], optional
        Per-format provenance of the integer id this section carried in the
        solver file it was read from, keyed by format name (e.g.
        ``{"vabs": 3}``). Enables same-format round-trip fidelity: a writer
        prefers the remembered id for its format, then fills gaps
        deterministically. Not user-authored; populated by adapter readers.
    extras : dict[str, Any], optional
        Additional adapter-specific metadata.
    """

    name: str
    material: str
    orientation: float = 0.0
    property_id: int | None = None
    source_ids: dict[str, int] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)
