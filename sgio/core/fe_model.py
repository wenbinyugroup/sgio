from __future__ import annotations

from dataclasses import dataclass, field

from meshio import Mesh

from .mesh import SGMesh
from .section import Orientation, Section


@dataclass
class FEModel:
    """Finite element core model used by :class:`StructureGene`.

    Parameters
    ----------
    name : str, optional
        Model name.
    mesh : SGMesh or meshio.Mesh or None, optional
        Finite element mesh.

    Attributes
    ----------
    name : str
        Model name.
    mesh : SGMesh or meshio.Mesh or None
        Finite element mesh.
    materials : dict[str, Any]
        Materials indexed by material name.
    orientations : dict[str, Orientation]
        FE orientation objects indexed by name.
    sections : dict[str, Section]
        FE sections indexed by section name.
    extras : dict[str, Any]
        Extra FE-level metadata.
    """

    name: str = ""
    mesh: SGMesh | Mesh | None = None
    materials: dict[str, object] = field(default_factory=dict)
    orientations: dict[str, Orientation] = field(default_factory=dict)
    sections: dict[str, Section] = field(default_factory=dict)
    extras: dict[str, object] = field(default_factory=dict)
