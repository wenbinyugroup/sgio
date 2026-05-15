"""Abaqus input writer."""

from __future__ import annotations

from typing import Any


def write_input_payload(destination: Any, payload: dict[str, Any]) -> None:
    """Abaqus input writing is not implemented in SGIO."""
    raise NotImplementedError("Abaqus input writing is not currently implemented")
