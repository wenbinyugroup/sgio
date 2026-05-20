from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ElasticInputType(str, Enum):
    """Typed elastic-input selector for material APIs."""

    AUTO = ""
    ISOTROPIC = "isotropic"
    ENGINEERING = "engineering"
    ORTHOTROPIC = "orthotropic"
    LAMINA = "lamina"
    ANISOTROPIC = "anisotropic"
    STIFFNESS = "stiffness"
    COMPLIANCE = "compliance"
    TRANSVERSE_ISOTROPIC = "transverse_isotropic"

    @classmethod
    def from_value(cls, input_type: ElasticInputType | str | int) -> ElasticInputType:
        """Normalize legacy elastic input tokens into one enum value.

        Parameters
        ----------
        input_type : ElasticInputType or str or int
            Legacy or typed elastic input selector.

        Returns
        -------
        ElasticInputType
            Normalized enum value.
        """

        if isinstance(input_type, cls):
            return input_type

        if isinstance(input_type, int):
            legacy_map = {
                0: cls.ISOTROPIC,
                1: cls.ENGINEERING,
                2: cls.ANISOTROPIC,
                3: cls.TRANSVERSE_ISOTROPIC,
            }
            try:
                return legacy_map[input_type]
            except KeyError as exc:
                raise ValueError(
                    f"Unsupported legacy elastic input type: {input_type}"
                ) from exc

        normalized = input_type.strip().lower()
        if normalized in {
            "",
            "isotropic",
            "engineering",
            "engineering constants",
            "orthotropic",
            "lamina",
            "anisotropic",
            "constants",
            "stiffness",
            "compliance",
            "transverse",
            "transverse_isotropic",
        }:
            alias_map = {
                "": cls.AUTO,
                "isotropic": cls.ISOTROPIC,
                "engineering": cls.ENGINEERING,
                "engineering constants": cls.ENGINEERING,
                "orthotropic": cls.ORTHOTROPIC,
                "lamina": cls.LAMINA,
                "anisotropic": cls.ANISOTROPIC,
                "constants": cls.ANISOTROPIC,
                "stiffness": cls.STIFFNESS,
                "compliance": cls.COMPLIANCE,
                "transverse": cls.TRANSVERSE_ISOTROPIC,
                "transverse_isotropic": cls.TRANSVERSE_ISOTROPIC,
            }
            return alias_map[normalized]

        if normalized.startswith("eng"):
            return cls.ENGINEERING
        if normalized.startswith("ortho"):
            return cls.ORTHOTROPIC
        if normalized.startswith("lam"):
            return cls.LAMINA
        if normalized.startswith("aniso"):
            return cls.ANISOTROPIC
        if normalized.startswith(("trans", "ti")):
            return cls.TRANSVERSE_ISOTROPIC
        if normalized.startswith("iso"):
            return cls.ISOTROPIC

        raise ValueError(f"Unsupported elastic input type: {input_type}")


class MatrixKind(str, Enum):
    """Typed selector for material matrix views."""

    STIFFNESS = "stiffness"
    COMPLIANCE = "compliance"


@dataclass(frozen=True)
class TensorComponent:
    """Typed material tensor/matrix component selector.

    Parameters
    ----------
    row : int
        One-based row index or tensor index.
    column : int
        One-based column index or tensor index.
    """

    row: int
    column: int

    def __post_init__(self) -> None:
        if self.row < 1 or self.column < 1:
            raise ValueError("TensorComponent indices must be >= 1")

    def to_matrix_indices(self) -> tuple[int, int]:
        """Return zero-based matrix indices."""

        return self.row - 1, self.column - 1

    def to_voigt_index(self) -> int:
        """Return the zero-based Voigt index for thermal-expansion access."""

        key = f"{min(self.row, self.column)}{max(self.row, self.column)}"
        mapping = {
            "11": 0,
            "22": 1,
            "33": 2,
            "23": 3,
            "13": 4,
            "12": 5,
        }
        try:
            return mapping[key]
        except KeyError as exc:
            raise ValueError(
                f"TensorComponent {self.row}{self.column} has no Voigt thermal mapping"
            ) from exc


class SectionCenter(str, Enum):
    """Typed selector for section-result center locations."""

    MASS = "mass"
    TENSION = "tension"
    SHEAR = "shear"


class SectionAxis(str, Enum):
    """Typed selector for section-result principal axes."""

    INERTIAL = "inertial"
    BENDING = "bending"
    SHEAR = "shear"


class SectionMatrixKind(str, Enum):
    """Typed selector for beam/shell section-result matrices."""

    MASS = "mass"
    MASS_CENTER = "mass_center"
    STIFFNESS = "stiffness"
    COMPLIANCE = "compliance"
    CLASSICAL_STIFFNESS = "classical_stiffness"
    CLASSICAL_COMPLIANCE = "classical_compliance"
    GEOMETRIC_STIFFNESS = "geometric_stiffness"


__all__ = [
    "ElasticInputType",
    "MatrixKind",
    "SectionAxis",
    "SectionCenter",
    "SectionMatrixKind",
    "TensorComponent",
]
