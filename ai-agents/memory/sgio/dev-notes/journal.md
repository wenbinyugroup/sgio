# Journal (sgio dev-notes)

## 2026-02-07

- **DONE 2026-02-07 14:00** — Implemented Phase 4.1 format requirements registry and
  public exports; added unit tests.
  - Note: [issue-1-minor-fixed.md](issue-1-minor-fixed.md)

- **DONE 2026-02-07 15:30** — Implemented Phase 4.2 auto-renumbering utilities
  (`ensure_node_ids`, `auto_renumber_for_format`), wired exports, and added unit tests.
  - Note: [issue-2-minor-fixed.md](issue-2-minor-fixed.md)

- **DONE 2026-02-07 16:45** — Completed Phase 4.3: Updated all VABS and SwiftComp writers
  to use automatic format-aware numbering. Fixed indentation issues (tabs vs spaces).
  Updated tests to reflect Phase 4 auto-renumbering behavior.
  - Note: [issue-3-minor-fixed.md](issue-3-minor-fixed.md)

- **DONE 2026-02-08** — Completed Phase 4.4: Fixed three bugs in reader node/element ID
  population. Fixed `_mesh_to_sg` logic so `sg.mesh`, `ensure_node_ids`, and `element_id`
  generation run for all `model_type` values (not only the `else` branch). Fixed tab
  indentation in VABS `read_buffer`. Unnested VABS reader test from solver test.
  All 66 relevant tests pass.
  - Note: [issue-4-minor-fixed.md](issue-4-minor-fixed.md)

- **DONE 2026-02-08** — Completed Phase 4.5 and 4.6: Removed all deprecated renumbering
  parameters from the entire call chain (writers, helpers, CLI). Created comprehensive
  `tests/unit/test_auto_numbering.py` (31 tests). Added 5 conversion tests to
  `test_format_conversions.py`. Fixed `test_raises_on_length_mismatch` to correctly test
  that `SGMesh` construction raises on mismatched node_id length.
  All 266 tests pass, 4 skipped.
  - Note: [issue-5-minor-fixed.md](issue-5-minor-fixed.md)

- **DONE 2026-02-08** — Completed Phase 4.7 (Documentation): Completely rewrote
  `docs/source/developer/numbering.md` to document automatic numbering system.
  Updated `docs/source/guide/io.rst` to remove deprecated parameters and add
  "Automatic Node and Element Numbering" section with examples and warning docs.
  Updated `write_buffer()` docstrings in VABS and SwiftComp to document automatic
  renumbering behavior. Created `docs/source/guide/migration_numbering.rst` with
  comprehensive migration guide. Added migration guide to docs index.
  **Phase 4 complete — 266 tests passing.**
  - Note: [issue-6-phase4-complete.md](issue-6-phase4-complete.md)
