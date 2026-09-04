"""Shared SwiftComp thermal-record constants.

Isolated from ``material_readers.py`` / ``material_writers.py`` so neither
module has to import the other for a constant both need: SwiftComp's thermal
record (CTE + specific heat) is isotropy-dependent, and reader and writer
must agree on the same length table to round-trip it.
"""

from __future__ import annotations

CTE_LEN_BY_ISOTROPY = {0: 1, 1: 3, 2: 6}
"""Voigt CTE components SwiftComp's thermal record carries per isotropy level."""
