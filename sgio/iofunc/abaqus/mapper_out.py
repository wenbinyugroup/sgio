"""Abaqus output mapper."""

from __future__ import annotations

from typing import Any


def map_model_to_write_payload(model_obj: Any, **kwargs: Any) -> dict[str, Any]:
    """Abaqus input writing is not implemented in SGIO."""
    raise NotImplementedError("Abaqus input writing is not currently implemented")
