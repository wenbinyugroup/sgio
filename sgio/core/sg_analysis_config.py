from __future__ import annotations

from dataclasses import dataclass

# Physics included in the analysis, as named by sgio's public API. The values
# are SwiftComp's analysis codes; format writers translate them where their
# own numbering differs (VABS writes its thermal flag as 3).
PHYSICS_BY_NAME = {
    'elastic': 0,
    'thermoelastic': 1,
}


def resolve_physics(physics: int | str) -> int:
    """Return the physics code for a name or a raw code.

    Parameters
    ----------
    physics : int or str
        Physics name (see :data:`PHYSICS_BY_NAME`) or its integer code.

    Returns
    -------
    int
        Physics code.

    Raises
    ------
    ValueError
        If ``physics`` is a name that is not supported.
    """
    if isinstance(physics, str):
        try:
            return PHYSICS_BY_NAME[physics.lower()]
        except KeyError:
            raise ValueError(
                f'Unsupported physics {physics!r}; expected one of '
                f'{sorted(PHYSICS_BY_NAME)}.'
            ) from None
    return int(physics)


@dataclass
class SGAnalysisConfig:
    """Analysis configuration for a structure gene.

    Attributes
    ----------
    analysis : int
        Analysis type.
    physics : int
        Physics included in the analysis.
    model : int
        Macroscopic structural model selector.
    geo_correct : bool
        Geometrically corrected shell model flag.
    do_damping : int
        Damping computation flag.
    is_temp_nonuniform : int
        Non-uniform temperature flag.
    force_flag : int
        Force flag for SwiftComp inputs.
    steer_flag : int
        Steer flag for SwiftComp inputs.
    """

    analysis: int = 0
    physics: int = 0
    model: int = 0
    geo_correct: bool = False
    do_damping: int = 0
    is_temp_nonuniform: int = 0
    force_flag: int = 0
    steer_flag: int = 0
