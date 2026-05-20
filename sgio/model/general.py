from __future__ import annotations

"""Compatibility shell for legacy imports from ``sgio.model.general``."""

from ._deprecations import warn_model_deprecation
from .protocols import LocationType, Model, getModelDim
from .response import SectionResponse, StructureResponseCase, StructureResponseCases
from .state import State, StateCase

warn_model_deprecation('sgio.model.general')

__all__ = [
    'LocationType',
    'Model',
    'SectionResponse',
    'State',
    'StateCase',
    'StructureResponseCase',
    'StructureResponseCases',
    'getModelDim',
]
