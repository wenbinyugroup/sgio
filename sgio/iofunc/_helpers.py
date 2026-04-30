"""Internal helpers shared by `iofunc` readers/writers."""
from __future__ import annotations

import logging

from sgio.core import StructureGene

logger = logging.getLogger(__name__)


def _resolve_num_elements(num_elements: int, sg: StructureGene) -> int:
    """Return ``num_elements`` if positive, else ``sg.nelems``."""
    return num_elements if num_elements else sg.nelems


def _safe_parse(parser_fn, *args, **kwargs):
    """Call ``parser_fn(*args, **kwargs)`` with unified error handling.

    Returns the parser's result on success, ``None`` on exception, or ``None``
    if the result itself is ``None`` (or any element of a tuple result is
    ``None``). Errors are logged.
    """
    try:
        result = parser_fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error: {e}")
        return None
    if result is None or (isinstance(result, tuple) and any(x is None for x in result)):
        logger.error("Error: No data read")
        return None
    return result
