from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, Sequence

from .query_types import SectionAxis, SectionCenter, SectionMatrixKind


@dataclass(frozen=True)
class StructuralMatrixSchema:
    """Physical schema for one structural matrix representation.

    Parameters
    ----------
    name : str
        Stable matrix identifier used inside the model layer.
    shape : tuple[int, int]
        Matrix shape.
    row_quantities : tuple[str, ...]
        Ordered physical quantities represented by matrix rows.
    column_quantities : tuple[str, ...]
        Ordered physical quantities represented by matrix columns.
    description : str
        Human-readable summary of the matrix semantics.
    """

    name: str
    shape: tuple[int, int]
    row_quantities: tuple[str, ...]
    column_quantities: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class StructuralTheorySchema:
    """Theory-level descriptor for a structural section result model.

    Parameters
    ----------
    theory_name : str
        Name of the structural theory.
    matrices : Mapping[str, StructuralMatrixSchema]
        Matrix schemas keyed by model attribute name.
    centers : tuple[str, ...], optional
        Named centers exposed by the model.
    principal_axes : tuple[str, ...], optional
        Named principal-axis descriptors exposed by the model.
    """

    theory_name: str
    matrices: Mapping[str, StructuralMatrixSchema]
    centers: tuple[str, ...] = ()
    principal_axes: tuple[str, ...] = ()


class StructuralSectionSupport:
    """Internal helper mixin shared by beam/shell section-result models."""

    theory_schema: ClassVar[StructuralTheorySchema]
    _SECTION_CENTER_ATTRS: ClassVar[Mapping[SectionCenter, tuple[str, ...]]] = {}
    _SECTION_AXIS_ATTRS: ClassVar[Mapping[SectionAxis, str]] = {}
    _SECTION_MATRIX_ATTRS: ClassVar[Mapping[SectionMatrixKind, str]] = {}

    @staticmethod
    def _get_matrix_entry(matrix: Sequence[Sequence[float]] | None, i: int, j: int) -> float | None:
        """Safely return one matrix entry.

        Parameters
        ----------
        matrix : sequence of sequence of float or None
            Candidate matrix container.
        i : int
            Zero-based row index.
        j : int
            Zero-based column index.

        Returns
        -------
        float or None
            Requested entry when available, otherwise ``None``.
        """

        if matrix is None or len(matrix) <= i:
            return None
        row = matrix[i]
        if row is None or len(row) <= j:
            return None
        return row[j]

    @classmethod
    def _get_matrix_value(
        cls,
        name: str,
        digit_offset: int,
        matrix: Sequence[Sequence[float]] | None,
    ) -> float | None:
        """Resolve a legacy matrix-token query such as ``stf11`` or ``mass23``."""

        try:
            i = int(name[digit_offset]) - 1
            j = int(name[digit_offset + 1]) - 1
        except (IndexError, TypeError, ValueError):
            return None
        return cls._get_matrix_entry(matrix, i, j)

    @staticmethod
    def _get_aliased_value(
        obj: Any,
        name: str,
        alias_map: Mapping[str, str],
    ) -> tuple[bool, Any]:
        """Resolve one legacy alias map against an object attribute set."""

        attr_name = alias_map.get(name)
        if attr_name is None:
            return False, None
        return True, getattr(obj, attr_name, None)

    @staticmethod
    def _format_scalar(value: Any) -> str:
        """Format one scalar for human-readable repr output."""

        if value is None:
            return "NONE"
        if isinstance(value, (int, float)):
            return f"{value:14e}"
        return str(value)

    @classmethod
    def _format_matrix_block(
        cls,
        title: str,
        matrix: Sequence[Sequence[float]] | None,
    ) -> list[str]:
        """Format one matrix block for repr output."""

        lines = [title]
        if matrix is None:
            lines.append("NONE")
            return lines

        for row in matrix:
            lines.append(", ".join(cls._format_scalar(value) for value in row))
        return lines

    @classmethod
    def _format_scalar_line(cls, label: str, value: Any) -> str:
        """Format a labeled scalar line for repr output."""

        return f"{label} = {cls._format_scalar(value)}"

    @classmethod
    def _format_center_line(cls, label: str, *values: Any) -> str:
        """Format a center tuple line for repr output."""

        formatted = ", ".join(cls._format_scalar(value) for value in values)
        return f"{label} = ({formatted})"

    @staticmethod
    def _format_named_attribute_block(
        title: str,
        obj: Any,
        label_to_attr: Mapping[str, str],
    ) -> list[str]:
        """Format a block of named attributes using ``getattr`` lookups."""

        lines = [title]
        for label, attr_name in label_to_attr.items():
            lines.append(f"  {label} = {getattr(obj, attr_name, None)}")
        return lines

    def get_center(self, center: SectionCenter) -> tuple[Any, ...]:
        """Return one named section center in typed form.

        Parameters
        ----------
        center : SectionCenter
            Named center selector.

        Returns
        -------
        tuple
            Ordered center coordinates stored by the model.
        """

        try:
            attr_names = self._SECTION_CENTER_ATTRS[center]
        except KeyError as exc:
            raise ValueError(
                f"{type(self).__name__} does not expose center {center.value!r}"
            ) from exc
        return tuple(getattr(self, attr_name, None) for attr_name in attr_names)

    def get_axis_angle(self, axis: SectionAxis) -> Any:
        """Return one named principal-axis angle in typed form."""

        try:
            attr_name = self._SECTION_AXIS_ATTRS[axis]
        except KeyError as exc:
            raise ValueError(
                f"{type(self).__name__} does not expose axis {axis.value!r}"
            ) from exc
        return getattr(self, attr_name, None)

    def get_section_matrix(self, kind: SectionMatrixKind) -> Sequence[Sequence[float]] | None:
        """Return one named section matrix in typed form."""

        try:
            attr_name = self._SECTION_MATRIX_ATTRS[kind]
        except KeyError as exc:
            raise ValueError(
                f"{type(self).__name__} does not expose matrix {kind.value!r}"
            ) from exc
        return getattr(self, attr_name, None)

    def get_section_matrix_component(
        self,
        kind: SectionMatrixKind,
        row: int,
        column: int,
    ) -> float | None:
        """Return one typed section-matrix entry using one-based indices."""

        matrix = self.get_section_matrix(kind)
        return self._get_matrix_entry(matrix, row - 1, column - 1)


_BEAM_MASS_QUANTITIES = ("u1", "u2", "u3", "theta1", "theta2", "theta3")
_EB_BEAM_RESULTANTS = ("F1", "M1", "M2", "M3")
_EB_BEAM_STRAINS = ("gamma11", "kappa11", "kappa12", "kappa13")
_TIMO_BEAM_RESULTANTS = ("F1", "F2", "F3", "M1", "M2", "M3")
_TIMO_BEAM_STRAINS = ("gamma11", "gamma12", "gamma13", "kappa11", "kappa12", "kappa13")
_KL_SHELL_RESULTANTS = ("N11", "N22", "N12", "M11", "M22", "M12")
_KL_SHELL_STRAINS = ("epsilon11", "epsilon22", "2epsilon12", "kappa11", "kappa22", "2kappa12")
_RM_SHELL_RESULTANTS = ("N11", "N22", "N12", "M11", "M22", "M12", "N13", "N23")
_RM_SHELL_STRAINS = (
    "epsilon11",
    "epsilon22",
    "2epsilon12",
    "kappa11",
    "kappa22",
    "2kappa12",
    "gamma13",
    "gamma23",
)


EULER_BERNOULLI_BEAM_SCHEMA = StructuralTheorySchema(
    theory_name="Euler-Bernoulli beam",
    matrices={
        "mass": StructuralMatrixSchema(
            name="mass",
            shape=(6, 6),
            row_quantities=_BEAM_MASS_QUANTITIES,
            column_quantities=_BEAM_MASS_QUANTITIES,
            description="Mass matrix in translational/rotational DOF order.",
        ),
        "mass_mc": StructuralMatrixSchema(
            name="mass_mc",
            shape=(6, 6),
            row_quantities=_BEAM_MASS_QUANTITIES,
            column_quantities=_BEAM_MASS_QUANTITIES,
            description="Mass matrix evaluated at the mass center.",
        ),
        "stff": StructuralMatrixSchema(
            name="stff",
            shape=(4, 4),
            row_quantities=_EB_BEAM_RESULTANTS,
            column_quantities=_EB_BEAM_STRAINS,
            description="Classical Euler-Bernoulli beam stiffness matrix.",
        ),
        "cmpl": StructuralMatrixSchema(
            name="cmpl",
            shape=(4, 4),
            row_quantities=_EB_BEAM_STRAINS,
            column_quantities=_EB_BEAM_RESULTANTS,
            description="Classical Euler-Bernoulli beam compliance matrix.",
        ),
    },
    centers=("mass_center", "tension_center"),
    principal_axes=("principal_inertial_axes", "principal_bending_axes"),
)


TIMOSHENKO_BEAM_SCHEMA = StructuralTheorySchema(
    theory_name="Timoshenko beam",
    matrices={
        "mass": StructuralMatrixSchema(
            name="mass",
            shape=(6, 6),
            row_quantities=_BEAM_MASS_QUANTITIES,
            column_quantities=_BEAM_MASS_QUANTITIES,
            description="Mass matrix in translational/rotational DOF order.",
        ),
        "mass_mc": StructuralMatrixSchema(
            name="mass_mc",
            shape=(6, 6),
            row_quantities=_BEAM_MASS_QUANTITIES,
            column_quantities=_BEAM_MASS_QUANTITIES,
            description="Mass matrix evaluated at the mass center.",
        ),
        "stff": StructuralMatrixSchema(
            name="stff",
            shape=(6, 6),
            row_quantities=_TIMO_BEAM_RESULTANTS,
            column_quantities=_TIMO_BEAM_STRAINS,
            description="Refined Timoshenko beam stiffness matrix.",
        ),
        "cmpl": StructuralMatrixSchema(
            name="cmpl",
            shape=(6, 6),
            row_quantities=_TIMO_BEAM_STRAINS,
            column_quantities=_TIMO_BEAM_RESULTANTS,
            description="Refined Timoshenko beam compliance matrix.",
        ),
        "stff_c": StructuralMatrixSchema(
            name="stff_c",
            shape=(4, 4),
            row_quantities=_EB_BEAM_RESULTANTS,
            column_quantities=_EB_BEAM_STRAINS,
            description="Classical beam stiffness view carried alongside the refined model.",
        ),
        "cmpl_c": StructuralMatrixSchema(
            name="cmpl_c",
            shape=(4, 4),
            row_quantities=_EB_BEAM_STRAINS,
            column_quantities=_EB_BEAM_RESULTANTS,
            description="Classical beam compliance view carried alongside the refined model.",
        ),
    },
    centers=("mass_center", "tension_center", "shear_center"),
    principal_axes=(
        "principal_inertial_axes",
        "principal_bending_axes",
        "principal_shear_axes",
    ),
)


KIRCHHOFF_LOVE_SHELL_SCHEMA = StructuralTheorySchema(
    theory_name="Kirchhoff-Love plate/shell",
    matrices={
        "mass": StructuralMatrixSchema(
            name="mass",
            shape=(6, 6),
            row_quantities=_BEAM_MASS_QUANTITIES,
            column_quantities=_BEAM_MASS_QUANTITIES,
            description="Section mass matrix in translational/rotational DOF order.",
        ),
        "stff": StructuralMatrixSchema(
            name="stff",
            shape=(6, 6),
            row_quantities=_KL_SHELL_RESULTANTS,
            column_quantities=_KL_SHELL_STRAINS,
            description="Kirchhoff-Love plate/shell stiffness matrix (A/B/D form).",
        ),
        "cmpl": StructuralMatrixSchema(
            name="cmpl",
            shape=(6, 6),
            row_quantities=_KL_SHELL_STRAINS,
            column_quantities=_KL_SHELL_RESULTANTS,
            description="Kirchhoff-Love plate/shell compliance matrix.",
        ),
        "stff_geo": StructuralMatrixSchema(
            name="stff_geo",
            shape=(6, 6),
            row_quantities=_KL_SHELL_RESULTANTS,
            column_quantities=_KL_SHELL_STRAINS,
            description="Geometrically corrected Kirchhoff-Love stiffness matrix.",
        ),
    },
    centers=("mass_center",),
)


REISSNER_MINDLIN_SHELL_SCHEMA = StructuralTheorySchema(
    theory_name="Reissner-Mindlin plate/shell",
    matrices={
        "stff": StructuralMatrixSchema(
            name="stff",
            shape=(8, 8),
            row_quantities=_RM_SHELL_RESULTANTS,
            column_quantities=_RM_SHELL_STRAINS,
            description="Reissner-Mindlin plate/shell stiffness matrix with transverse shear terms.",
        ),
        "cmpl": StructuralMatrixSchema(
            name="cmpl",
            shape=(8, 8),
            row_quantities=_RM_SHELL_STRAINS,
            column_quantities=_RM_SHELL_RESULTANTS,
            description="Reissner-Mindlin plate/shell compliance matrix.",
        ),
    },
)


__all__ = [
    "EULER_BERNOULLI_BEAM_SCHEMA",
    "KIRCHHOFF_LOVE_SHELL_SCHEMA",
    "REISSNER_MINDLIN_SHELL_SCHEMA",
    "StructuralMatrixSchema",
    "StructuralSectionSupport",
    "StructuralTheorySchema",
    "TIMOSHENKO_BEAM_SCHEMA",
]
