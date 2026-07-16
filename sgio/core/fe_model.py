from __future__ import annotations

from dataclasses import dataclass, field

from .mesh import SGMesh
from .section import Orientation, Section


@dataclass
class FEModel:
    """Finite element core model used by :class:`StructureGene`.

    Parameters
    ----------
    name : str, optional
        Model name.
    mesh : SGMesh or None, optional
        Finite element mesh.

    Attributes
    ----------
    name : str
        Model name.
    mesh : SGMesh or None
        Finite element mesh.
    materials : dict[str, Any]
        Materials indexed by material name.
    orientations : dict[str, Orientation]
        FE orientation objects indexed by name.
    sections : dict[str, Section]
        FE sections indexed by section name.
    material_source_ids : dict[str, dict[str, int]]
        Per-format provenance of solver material ids, keyed by material name
        then by format name (e.g. ``{"steel": {"vabs": 3}}``). Enables
        same-format round-trip fidelity for the ``1..n`` material labels that
        VABS/SwiftComp files require. Not user-authored; populated by adapter
        readers and consumed by writers via prefer-then-fill numbering.
    extras : dict[str, Any]
        Extra FE-level metadata.
    """

    name: str = ""
    mesh: SGMesh | None = None
    materials: dict[str, object] = field(default_factory=dict)
    orientations: dict[str, Orientation] = field(default_factory=dict)
    sections: dict[str, Section] = field(default_factory=dict)
    material_source_ids: dict[str, dict[str, int]] = field(default_factory=dict)
    extras: dict[str, object] = field(default_factory=dict)
