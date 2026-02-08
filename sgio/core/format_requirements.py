"""Format-specific requirements.

This module defines a small registry of constraints that certain output formats
impose on node/element IDs.

Phase 4 (Automatic Format-Aware Numbering) will use these requirements to
automatically validate and, when needed, renumber IDs before writing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class FormatNumberingRequirements:
    """Numbering requirements for a target format.

    Parameters
    ----------
    name : str
        Human readable name for messages (e.g., "VABS").
    nodes_consecutive : bool
        Whether node IDs must be consecutive.
    nodes_start_from : int
        Required starting value for node IDs when consecutive.
    elements_consecutive : bool
        Whether element IDs must be consecutive.
    elements_start_from : int
        Required starting value for element IDs when consecutive.
    allows_zero_id : bool
        Whether ID value 0 is allowed.
    """

    name: str
    nodes_consecutive: bool
    nodes_start_from: int
    elements_consecutive: bool
    elements_start_from: int
    allows_zero_id: bool = False


# Canonical format requirements
_CANONICAL_REQUIREMENTS: Dict[str, FormatNumberingRequirements] = {
    "vabs": FormatNumberingRequirements(
        name="VABS",
        nodes_consecutive=True,
        nodes_start_from=1,
        elements_consecutive=True,
        elements_start_from=1,
        allows_zero_id=False,
    ),
    "swiftcomp": FormatNumberingRequirements(
        name="SwiftComp",
        nodes_consecutive=True,
        nodes_start_from=1,
        elements_consecutive=True,
        elements_start_from=1,
        allows_zero_id=False,
    ),
    "abaqus": FormatNumberingRequirements(
        name="Abaqus",
        nodes_consecutive=False,
        nodes_start_from=1,
        elements_consecutive=False,
        elements_start_from=1,
        allows_zero_id=False,
    ),
    "gmsh": FormatNumberingRequirements(
        name="Gmsh",
        nodes_consecutive=False,
        nodes_start_from=1,
        elements_consecutive=False,
        elements_start_from=1,
        allows_zero_id=False,
    ),
}


# Aliases accepted by public APIs/documentation
FORMAT_ALIASES: Dict[str, str] = {
    "sc": "swiftcomp",
}


# Public registry (includes canonical names + aliases)
REQUIREMENTS: Dict[str, FormatNumberingRequirements] = {
    **_CANONICAL_REQUIREMENTS,
    **{alias: _CANONICAL_REQUIREMENTS[target] for alias, target in FORMAT_ALIASES.items()},
}


def normalize_format_name(file_format: str) -> str:
    """Normalize a user-provided format string.

    Parameters
    ----------
    file_format : str
        Format name from public APIs.

    Returns
    -------
    str
        Lower-cased canonical name if an alias is known, otherwise lower-cased
        input.
    """
    fmt = (file_format or "").strip().lower()
    return FORMAT_ALIASES.get(fmt, fmt)


def get_numbering_requirements(file_format: str) -> Optional[FormatNumberingRequirements]:
    """Get numbering requirements for a format.

    Parameters
    ----------
    file_format : str
        Format name (e.g., 'vabs', 'swiftcomp', 'sc').

    Returns
    -------
    FormatNumberingRequirements or None
        Requirements if known; otherwise None.
    """
    fmt = normalize_format_name(file_format)
    return _CANONICAL_REQUIREMENTS.get(fmt)


__all__ = [
    "FormatNumberingRequirements",
    "FORMAT_ALIASES",
    "REQUIREMENTS",
    "normalize_format_name",
    "get_numbering_requirements",
]
