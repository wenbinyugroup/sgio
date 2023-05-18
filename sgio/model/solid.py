from dataclasses import dataclass
from typing import List

@dataclass
class Cauchy:
    """Cauchy continuum model
    """

    #: Isotropy type.
    #: Isotropic (0), orthotropic (1), anisotropic (2).
    isotropy: int

    #: Stiffness matrix
    c: List[List[float]] = None
    #: Compliance matrix
    s: List[List[float]] = None

    e1: float = None
    e2: float = None
    e3: float = None
    g12: float = None
    g13: float = None
    g23: float = None
    nu12: float = None
    nu13: float = None
    nu23: float = None
