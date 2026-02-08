# SGIO Phase 4 – Status Summary

## Goal and objectives

- Implement automatic, format‑aware node/element numbering for all SGIO readers and writers.
- Ensure users do not need renumbering flags; the library enforces format rules internally.
- Maintain consistent `node_id` (point_data) and `element_id` (cell_data) across all formats.

## What has been done

- **Phase 4.1 – Format requirements registry**
  - Added `FormatNumberingRequirements` registry in `sgio/core/format_requirements.py`.
  - Defined numbering rules for vabs, swiftcomp (sc), abaqus, gmsh.
  - Exported via `sgio/core/__init__.py` and `sgio/__init__.py`.
  - Unit tests in `tests/unit/test_format_requirements.py`.

- **Phase 4.2 – Core auto‑numbering utilities**
  - Implemented `ensure_node_ids(mesh)` and `ensure_element_ids(mesh)` in `sgio/core/numbering.py`.
  - Implemented `auto_renumber_for_format(mesh, format, logger)` using the registry.
  - Exported via `sgio/core/__init__.py` and `sgio/__init__.py`.
  - Unit tests in `tests/unit/test_numbering.py`.

- **Phase 4.3 – Writers updated**
  - Updated VABS and SwiftComp writers (and helpers) to:
    - Call `ensure_node_ids`, `ensure_element_ids`, and `auto_renumber_for_format`.
    - Ignore old renumbering parameters with warnings.
  - Updated `sgio/iofunc/main.py::convert` to rely on auto‑numbering.
  - Fixed earlier indentation issues and adjusted tests to expect auto‑renumbering.

- **Phase 4.4 – Readers & conversion (in progress)**
  - **VABS reader** (`sgio/iofunc/vabs/_mesh.py`):
    - `read_buffer` converts `point_ids` into `point_data['node_id']`.
    - Stores element IDs in `cell_data['element_id']`.
    - Builds `SGMesh` and calls `ensure_node_ids` and `ensure_element_ids`.
    - Fixed: replaced tab indentation with 4-space throughout `read_buffer`.
  - **SwiftComp reader** (`sgio/iofunc/swiftcomp/_mesh.py`):
    - `read_buffer` converts `point_ids` to `point_data['node_id']`.
    - Populates `cell_data['element_id']`, `cell_data['property_id']`, and `cell_data['property_ref_csys']`.
    - Builds `SGMesh` and calls `ensure_node_ids` / `ensure_element_ids`.
  - **Gmsh/meshio conversion** (`sgio/iofunc/main.py` `_mesh_to_sg`):
    - Fixed: `sg.smdim`, `sg.model`, `sg.mesh`, `ensure_node_ids`, and `element_id` generation
      were inside the `else:` branch (never ran for string `model_type`). Moved outside.
    - Ensures `property_id` with sensible defaults and builds `sg.mocombos`.
  - **Tests**:
    - VABS reader test (`test_vabs_reader_populates_node_and_element_ids`) moved to module
      level (was accidentally nested inside `test_vabs_solver_execution`).
    - SwiftComp reader checks in `test_sc_output_state.py` pass.
  - **All 66 relevant tests pass.**

- **Phase 4.5 – Simplified helpers**
  - Removed all deprecated parameter machinery (`renumber_nodes`, `renumber_elements`,
    `use_sequential_node_ids`, `use_sequential_element_ids`) from all writer call chains.
  - Removed `_validate_consecutive_numbering` wrapper; tests use `validate_node_ids` directly.
  - All 230+ tests pass after cleanup.

- **Phase 4.6 – Test updates**
  - Created `tests/unit/test_auto_numbering.py` with 31 new tests.
  - Added `@pytest.mark.io` / `@pytest.mark.abaqus` markers to abaqus numbering tests.
  - Added 5 conversion tests to `tests/conversion/test_format_conversions.py`.
  - Fixed `test_raises_on_length_mismatch` — error comes from `SGMesh` construction.
  - Fixed duplicate module docstring in `test_format_conversions.py`.
  - **266 tests passed, 4 skipped.**

- **Phase 4.7 – Documentation updates (COMPLETE)**
  - Completely rewrote `docs/source/developer/numbering.md` (550+ lines) documenting automatic system.
  - Updated `docs/source/guide/io.rst` to remove deprecated parameters and add "Automatic Numbering" section.
  - Created `docs/source/guide/migration_numbering.rst` — comprehensive migration guide (285 lines).
  - Updated `write_buffer()` docstrings in VABS and SwiftComp to document automatic behavior.
  - Added migration guide to docs index.

## Phase 4 Status: ✅ COMPLETE

All phases complete. 266 tests passing, 4 skipped. Full automatic numbering system implemented,
tested, and documented.