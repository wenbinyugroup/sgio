# Issue 6 – Phase 4.7 (Documentation) Complete

## Phase 4.7 – Documentation Updates

Updated all documentation to reflect the new automatic numbering system.

### Developer Documentation

**`docs/source/developer/numbering.md`** — Complete rewrite (338 → 550+ lines):
- Documented automatic format-aware renumbering system
- Explained dual numbering (internal 0-based, external format-specific)
- Added format requirements table with automatic enforcement column
- Documented `ensure_node_ids`, `ensure_element_ids`, `auto_renumber_for_format` API
- Provided reader/writer implementation examples with automatic numbering
- Added testing examples for round-trip and cross-format conversion
- Documented common pitfalls (ID vs index confusion, mesh modification after write)
- **Removed all references** to deprecated `renumber_nodes`/`renumber_elements` parameters
- Added "Deprecated API (Removed)" section listing removed parameters

### User Documentation

**`docs/source/guide/io.rst`** — Updated write section:
- **Removed** `renumber_nodes` and `renumber_elements` from Parameters list
- **Added** note about automatic numbering in Parameters section
- **Replaced** "Write with node/element renumbering" example with "Write with automatic format compliance"
- **Added** new section: "Automatic Node and Element Numbering" (115 lines) covering:
  - How It Works
  - Format Conversion Examples (Abaqus→VABS, VABS→Abaqus, Abaqus→Abaqus)
  - Understanding Warnings (what they mean, when they appear, when they don't)
  - Migration from Old API

**`docs/source/guide/migration_numbering.rst`** — New migration guide (285 lines):
- What Changed (old vs new behavior)
- Removed Parameters list
- Migration Steps (remove params, handle warnings, update validation)
- Common Migration Scenarios:
  - Abaqus → VABS Conversion
  - Programmatic Mesh Creation
  - Round-Trip Preservation
- Troubleshooting section:
  - TypeError for removed parameters
  - UserWarning handling
  - Mesh IDs changed after writing
- Benefits of Automatic Numbering
- Further Reading links

**`docs/source/guide/index.rst`** — Added `migration_numbering` to toctree

### Function Docstrings

**`sgio/iofunc/vabs/_mesh.py::write_buffer()`**:
- Added summary: "Automatically ensures node and element IDs comply with VABS format requirements..."
- Expanded Parameters section to note automatic renumbering behavior
- Added Notes section documenting auto-generation, auto-renumbering, VABS requirements
- Added Warns section for UserWarning
- Added Examples section showing warning behavior

**`sgio/iofunc/swiftcomp/_mesh.py::write_buffer()`**:
- Added summary: "Automatically ensures node and element IDs comply with SwiftComp format requirements..."
- Expanded Parameters section to note automatic renumbering behavior
- Added Notes section documenting auto-generation, auto-renumbering, SwiftComp requirements
- Added Warns section for UserWarning
- Added Examples section showing warning behavior

## Summary of Documentation Changes

| File | Change Type | Key Updates |
|------|-------------|-------------|
| `docs/source/developer/numbering.md` | Complete rewrite | Automatic API, removed deprecated params, new examples |
| `docs/source/guide/io.rst` | Major update | Removed deprecated params, added auto-numbering section |
| `docs/source/guide/migration_numbering.rst` | New file | Comprehensive migration guide |
| `docs/source/guide/index.rst` | Minor update | Added migration guide to toctree |
| `sgio/iofunc/vabs/_mesh.py` | Docstring update | Document automatic behavior, warnings |
| `sgio/iofunc/swiftcomp/_mesh.py` | Docstring update | Document automatic behavior, warnings |

## Result

**All Phase 4 work complete:**
- ✅ Phase 4.1 — Format requirements registry
- ✅ Phase 4.2 — Core auto-numbering utilities
- ✅ Phase 4.3 — Writers updated
- ✅ Phase 4.4 — Readers & conversion fixed
- ✅ Phase 4.5 — Simplified helpers (removed deprecated code)
- ✅ Phase 4.6 — Test updates (31 new tests, 266 total passing)
- ✅ Phase 4.7 — Documentation (rewrites, migration guide, docstrings)

**266 tests passed, 4 skipped** — all green.
