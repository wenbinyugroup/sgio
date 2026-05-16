from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class MaterialDefinition:
    """Identity and inertial metadata for a material definition.

    Parameters
    ----------
    name : str, optional
        Material name.
    id : int or None, optional
        Material identifier.
    density : float, optional
        Material density.
    temperature : float, optional
        Reference temperature or temperature metadata.
    """

    name: str = ''
    id: int | None = None
    density: float = 0.0
    temperature: float = 0.0


@dataclass(slots=True)
class LinearElasticBehavior:
    """Linear-elastic behavior payload used by ``CauchyContinuumModel``.

    Parameters
    ----------
    isotropy : int, optional
        Symmetry family identifier.
    e1, e2, e3 : float or None, optional
        Young's moduli.
    g12, g13, g23 : float or None, optional
        Shear moduli.
    nu12, nu13, nu23 : float or None, optional
        Poisson ratios.
    stff : list[list[float]] or None, optional
        Stiffness matrix.
    cmpl : list[list[float]] or None, optional
        Compliance matrix.
    """

    isotropy: int = 0
    e1: float | None = None
    e2: float | None = None
    e3: float | None = None
    g12: float | None = None
    g13: float | None = None
    g23: float | None = None
    nu12: float | None = None
    nu13: float | None = None
    nu23: float | None = None
    stff: list[list[float]] | None = None
    cmpl: list[list[float]] | None = None


@dataclass(slots=True)
class ThermalProperties:
    """Thermal-material properties grouped away from the outer compatibility shell.

    Parameters
    ----------
    cte : list[float] or None, optional
        Thermal expansion coefficients.
    specific_heat : float, optional
        Specific heat capacity.
    d_thetatheta : float, optional
        Solver-specific thermal property.
    f_eff : float, optional
        Effective thermal property used by some readers.
    """

    cte: list[float] | None = None
    specific_heat: float = 0.0
    d_thetatheta: float = 0.0
    f_eff: float = 0.0


@dataclass(slots=True)
class StrengthProperties:
    """Strength and failure parameters grouped for explicit responsibility boundaries.

    Parameters
    ----------
    x1t, x2t, x3t : float or None, optional
        Tensile strengths.
    x1c, x2c, x3c : float or None, optional
        Compressive strengths.
    x23, x13, x12 : float or None, optional
        Shear strengths.
    strength_measure : int, optional
        Strength measure selector.
    strength_constants : list[float] or None, optional
        Packed strength constants.
    char_len : float, optional
        Characteristic length.
    failure_criterion : int, optional
        Failure criterion identifier.
    """

    x1t: float | None = None
    x2t: float | None = None
    x3t: float | None = None
    x1c: float | None = None
    x2c: float | None = None
    x3c: float | None = None
    x23: float | None = None
    x13: float | None = None
    x12: float | None = None
    strength_measure: int = 0
    strength_constants: list[float] | None = None
    char_len: float = 0.0
    failure_criterion: int = 0


__all__ = [
    'LinearElasticBehavior',
    'MaterialDefinition',
    'StrengthProperties',
    'ThermalProperties',
]
