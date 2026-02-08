# Issue 3: Phase 4.3 - Update Writers to Use Auto-Renumbering

**Summary**: Updated all VABS and SwiftComp writers to use automatic format-aware numbering instead of manual renumber parameters.

**Location**: Multiple files in `sgio/iofunc/` directory

**Severity**: Minor

**Description**: 
Phase 4.3 required updating all writer functions to:
1. Add deprecation warnings for old numbering parameters (`renumber_nodes`, `renumber_elements`, `use_sequential_node_ids`, `use_sequential_element_ids`)
2. Call `auto_renumber_for_format()` to automatically handle numbering based on format requirements
3. Remove manual numbering logic from writers

**Impact**: 
- Simplifies the API - users no longer need to understand format-specific numbering requirements
- Backward compatible - old parameters are accepted but ignored with warnings
- More robust - automatic renumbering prevents format-specific numbering errors

**Solution**:
Updated the following files:

1. **`sgio/iofunc/vabs/_mesh.py`** - Updated `write_buffer()` function
2. **`sgio/iofunc/swiftcomp/_mesh.py`** - Updated `write_buffer()` and `_write_elements()` 
3. **`sgio/iofunc/swiftcomp/_swiftcomp.py`** - Updated `write_buffer()` function
4. **`sgio/iofunc/swiftcomp/_input.py`** - Updated `writeInputBuffer()` and `_writeMesh()` functions
5. **`sgio/iofunc/vabs/_input.py`** - Updated `_writeMesh()` function
6. **`sgio/iofunc/main.py`** - Updated `convert()` function

Fixed indentation issues (tabs vs spaces) in multiple files.

Updated tests in `tests/unit/test_mesh_validation.py`:
- `test_vabs_write_with_invalid_numbering` - Now verifies auto-renumbering behavior
- `test_swiftcomp_write_with_invalid_numbering` - Now verifies auto-renumbering behavior

**Documentation**: issue-3-minor-fixed.md

**Status**: Fixed

**Assignee**: AI Agent

**Reviewer**: User

**Test Results**: 144 passed, 1 skipped (all unit tests passing)

