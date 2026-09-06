"""Internal helpers shared by `iofunc` readers/writers."""
from __future__ import annotations

from sgio.core import StructureGene


def _resolve_num_elements(num_elements: int, sg: StructureGene) -> int:
    """Return ``num_elements`` if positive, else ``sg.nelems``."""
    return num_elements if num_elements else sg.nelems
