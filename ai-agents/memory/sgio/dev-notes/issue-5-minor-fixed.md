# Issue 5 – Phase 4.5 and 4.6 completion

## Phase 4.5 – Simplified helper functions

Removed all deprecated parameter machinery (`renumber_nodes`, `renumber_elements`,
`use_sequential_node_ids`, `use_sequential_element_ids`) throughout the call chain.

### Changes

**`sgio/iofunc/_meshio.py`:**
- `_write_nodes()`: Removed deprecated params; simplified to `nid = node_id[i] if len(node_id) > 0 else i + 1`
- `_meshio_to_sg_order()`: Removed deprecated params; simplified mapping logic
- Removed dead commented-out old `_meshio_to_sg_order` block
- Removed deprecated `_validate_consecutive_numbering` wrapper function
- Removed unused `from sgio.core.numbering import validate_node_ids` import

**Callers updated** (deprecated params stripped from signatures and call sites):
- `sgio/iofunc/vabs/_mesh.py` — `write`, `write_buffer`
- `sgio/iofunc/vabs/_input.py` — `_writeMesh`
- `sgio/iofunc/vabs/main.py` — `write_buffer`, `writeInputBuffer`
- `sgio/iofunc/swiftcomp/_mesh.py` — `write`, `write_buffer`
- `sgio/iofunc/swiftcomp/_input.py` — `writeInputBuffer`, `_writeMesh`
- `sgio/iofunc/swiftcomp/_swiftcomp.py` — `write_buffer`
- `sgio/iofunc/main.py` — `write`

**`tests/unit/test_mesh_validation.py`:** Completely rewritten — replaced import of removed
`_validate_consecutive_numbering` with `validate_node_ids`, removed deprecated-param tests,
added Phase 4 auto-renumber behavior tests.

## Phase 4.6 – Test updates

Created `tests/unit/test_auto_numbering.py` with 31 tests covering:
- `TestEnsureNodeIds` (4 tests)
- `TestEnsureElementIds` (3 tests)
- `TestAutoRenumberVabs` (7 tests)
- `TestAutoRenumberSwiftcomp` (3 tests)
- `TestAutoRenumberAbaqus` (2 tests)
- `TestAutoRenumberUnknownFormat` (1 test)
- `TestVabsWriteAutoNumbering` (3 tests)
- `TestSwiftcompWriteAutoNumbering` (2 tests)
- `TestHandleDeprecatedParameter` (6 tests)

Added `@pytest.mark.io` and `@pytest.mark.abaqus` markers to `tests/file_io/abaqus/test_abaqus_numbering.py`.

Updated `tests/conversion/test_format_conversions.py`:
- Fixed duplicate module docstring at top of file
- Added imports: `warnings`, `StringIO`, `numpy`, `SGMesh`, `auto_renumber_for_format`,
  `vabs_write_buffer`, `sc_write_buffer`
- Added 5 new tests:
  - `test_vabs_conversion_auto_renumbers_nonconsecutive_ids`
  - `test_vabs_conversion_emits_warning_on_renumber`
  - `test_swiftcomp_conversion_auto_renumbers_nonconsecutive_ids`
  - `test_swiftcomp_conversion_emits_warning_on_renumber`
  - `test_auto_renumber_preserves_compliant_ids`

Fixed `tests/unit/test_auto_numbering.py::TestEnsureNodeIds::test_raises_on_length_mismatch`:
the test incorrectly expected `ensure_node_ids` to raise the length-mismatch error; in
reality, `SGMesh.__init__` (via meshio) raises it first. Updated test to verify construction
raises `ValueError`.

## Result

**266 tests passed, 4 skipped** — all clean.
