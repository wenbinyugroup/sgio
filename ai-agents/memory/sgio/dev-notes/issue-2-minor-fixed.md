# Issue 2 — Minor — Fixed

## Summary
Implemented Phase 4.2 auto-renumbering utilities for format-aware node/element IDs.

## Location
- `sgio/core/numbering.py` (around lines ~343–620): `ensure_node_ids()`, `auto_renumber_for_format()`, helpers.
- `sgio/core/__init__.py`: re-export new utilities.
- `sgio/__init__.py`: re-export new utilities at top-level.
- `tests/unit/test_numbering.py`: added unit coverage for new utilities.

## Severity
Minor

## Description
Phase 4.2 required adding automatic numbering utilities so callers can ensure `node_id`/`element_id` exist and optionally auto-renumber them to satisfy target format constraints (VABS/SwiftComp consecutive; Abaqus/Gmsh non-consecutive allowed but positive/unique).

## Impact
- Enables Phase 4.3 (writers) to transparently enforce numbering requirements without requiring users to manually set renumber flags.
- Provides a single shared implementation path for node/element ID generation and format-aware renumbering.

## Solution
- Added `ensure_node_ids(mesh)` to generate sequential node IDs when missing.
- Added `auto_renumber_for_format(mesh, format, logger=None) -> (bool, bool)` using the Phase 4.1 requirements registry (`get_numbering_requirements`).
- Implemented helper functions for requirement checking and sequential renumbering.
- Wired exports via `sgio/core/__init__.py` and `sgio/__init__.py`.
- Added unit tests validating generation, renumbering behavior, and warnings.

## Documentation
issue-2-minor-fixed.md

## Status
Fixed

## Assignee
Augment Agent

## Reviewer
TBD

