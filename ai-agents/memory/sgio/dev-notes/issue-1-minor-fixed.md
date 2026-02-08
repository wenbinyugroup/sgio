## Summary
Implement Phase 4.1 format requirements registry for automatic format-aware numbering.

## Location
- `sgio/core/format_requirements.py:1-136`
- `sgio/core/__init__.py:16-22`
- `sgio/__init__.py:15-26, 83-90`

## Severity
Minor

## Description
Phase 4 (Automatic Format-Aware Numbering) requires a central registry describing
node/element ID numbering constraints per supported format (e.g., VABS and
SwiftComp require consecutive IDs starting from 1).

Before this change, there was no single source of truth for these constraints,
making it harder to implement consistent auto-renumbering in later phases.

## Impact
- Enables later phases (4.2+) to query numbering constraints in a consistent way.
- Reduces duplication of format-specific rules across writers.
- Provides a stable normalization layer for format aliases (e.g., `sc` →
  `swiftcomp`).

## Solution
- Added `sgio/core/format_requirements.py` containing:
  - `FormatNumberingRequirements` (frozen dataclass)
  - canonical requirements for `vabs`, `swiftcomp`, `abaqus`, `gmsh`
  - alias mapping `FORMAT_ALIASES` (`sc` → `swiftcomp`)
  - helpers `normalize_format_name()` and `get_numbering_requirements()`
- Re-exported registry symbols via `sgio/core/__init__.py` and `sgio/__init__.py`.
- Added unit tests in `tests/unit/test_format_requirements.py`.

## Documentation
issue-1-minor-fixed.md

## Status
Fixed

## Assignee
augment-agent

## Reviewer
tian50
