from __future__ import annotations

from dataclasses import dataclass


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
