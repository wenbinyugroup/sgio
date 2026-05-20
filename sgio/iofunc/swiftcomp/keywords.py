"""SwiftComp format constants used by parser and writer layers."""

from __future__ import annotations


COMMENT_CHAR = "#"


def resolve_model_dimension(model: int | str) -> int:
    """Resolve a SwiftComp model selector to structural model dimension."""
    if isinstance(model, int):
        return model

    model_prefix = model.upper()[:2]
    if model_prefix == "SD":
        return 3
    if model_prefix == "PL":
        return 2
    if model_prefix == "BM":
        return 1
    raise ValueError(f"Unsupported SwiftComp model selector: {model}")
