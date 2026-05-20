from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from .fe_model import FEModel
from .mesh import SGMesh
from .section import Orientation, Section


class StructuralModel:
    """Minimal structural-analysis application model built on top of ``FEModel``.

    Parameters
    ----------
    name : str, optional
        Model name. If ``fe_model`` is given, this value overrides
        ``fe_model.name`` when non-empty.
    fe_model : FEModel, optional
        Backing finite element model.
    boundary_conditions : list[Any], optional
        Structural boundary-condition payloads.
    loads : list[Any], optional
        Structural load payloads.
    steps : list[Any], optional
        Analysis step payloads.
    interactions : list[Any], optional
        Structural interaction payloads.
    coordinate_systems : mapping[str, Any], optional
        Structural coordinate systems indexed by name.
    extras : mapping[str, Any], optional
        Additional structural-level metadata.
    """

    def __init__(
        self,
        name: str = "",
        fe_model: FEModel | None = None,
        boundary_conditions: list[Any] | None = None,
        loads: list[Any] | None = None,
        steps: list[Any] | None = None,
        interactions: list[Any] | None = None,
        coordinate_systems: Mapping[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> None:
        self._fe = FEModel(name=name) if fe_model is None else fe_model
        if name:
            self._fe.name = name

        self.boundary_conditions: list[Any] = list(boundary_conditions or [])
        self.loads: list[Any] = list(loads or [])
        self.steps: list[Any] = list(steps or [])
        self.interactions: list[Any] = list(interactions or [])
        self.coordinate_systems: dict[str, Any] = dict(coordinate_systems or {})
        self.extras: dict[str, Any] = dict(extras or {})

    @classmethod
    def from_fe(cls, fe_model: FEModel) -> StructuralModel:
        """Create a structural model from finite-element data.

        Parameters
        ----------
        fe_model : FEModel
            Source finite element model.

        Returns
        -------
        StructuralModel
            New structural model with a deep-copied backing ``FEModel``.
        """
        return cls(fe_model=copy.deepcopy(fe_model))

    @property
    def fe(self) -> FEModel:
        """Backing finite element model."""
        return self._fe

    @fe.setter
    def fe(self, value: FEModel) -> None:
        self._fe = value

    @property
    def fe_model(self) -> FEModel:
        """Backing finite element model."""
        return self._fe

    @fe_model.setter
    def fe_model(self, value: FEModel) -> None:
        self._fe = value

    @property
    def name(self) -> str:
        """Model name."""
        return self._fe.name

    @name.setter
    def name(self, value: str) -> None:
        self._fe.name = value

    @property
    def mesh(self) -> SGMesh | None:
        """Finite element mesh."""
        return self._fe.mesh

    @mesh.setter
    def mesh(self, value: SGMesh | None) -> None:
        self._fe.mesh = value

    @property
    def materials(self) -> dict[str, Any]:
        """Materials indexed by material name."""
        return self._fe.materials

    @materials.setter
    def materials(self, value: Mapping[str, Any]) -> None:
        self._fe.materials = dict(value)

    @property
    def orientations(self) -> dict[str, Orientation]:
        """Finite element orientations indexed by name."""
        return self._fe.orientations

    @orientations.setter
    def orientations(self, value: Mapping[str, Orientation]) -> None:
        self._fe.orientations = dict(value)

    @property
    def sections(self) -> dict[str, Section]:
        """Finite element sections indexed by section name."""
        return self._fe.sections

    @sections.setter
    def sections(self, value: Mapping[str, Section]) -> None:
        self._fe.sections = dict(value)

    def copy(self) -> StructuralModel:
        """Create a deep copy of the structural model.

        Returns
        -------
        StructuralModel
            Deep copy of the current instance.
        """
        return copy.deepcopy(self)
