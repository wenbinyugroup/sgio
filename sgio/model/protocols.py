from __future__ import annotations

from enum import Enum
from numbers import Number
from typing import Protocol


class Model(Protocol):
    """Protocol shared by legacy model-like objects."""

    def __repr__(self) -> str:
        ...

    def __call__(self, x):
        ...

    def set(self, name: str, value: Number) -> None:
        ...

    def get(self, name: str):
        """Get model parameter (property) given a name."""


class LocationType(str, Enum):
    """Valid location types for state data."""

    NODE = 'node'
    ELEMENT = 'element'
    ELEMENT_NODE = 'element_node'


def getModelDim(model: str) -> int:
    """Infer structural-model dimension from a legacy model label."""

    mdim = 0
    if model.strip().lower()[:2] == 'sd':
        mdim = 3
    elif model.strip().lower()[:2] == 'pl':
        mdim = 2
    elif model.strip().lower()[:2] == 'bm':
        mdim = 1

    return mdim


__all__ = ['LocationType', 'Model', 'getModelDim']
