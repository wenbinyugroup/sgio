# Issue 4: Phase 4.4 - Fix Reader node_id/element_id Bugs

**Summary**: Fixed three bugs preventing readers from correctly populating `point_data['node_id']` and `cell_data['element_id']` in all code paths.

**Location**: `sgio/iofunc/main.py`, `sgio/iofunc/vabs/_mesh.py`, `tests/file_io/vabs/test_vabs_input.py`

**Severity**: Minor

**Description**:
Phase 4.4 added reader-side node/element ID population but left three issues:

1. **`sgio/iofunc/main.py` — `_mesh_to_sg` logic bug**: The `sg.smdim`, `sg.model`, `sg.mesh` assignments and the `ensure_node_ids` / `element_id` generation block were incorrectly indented inside the `else:` branch (which only runs when `model_type` is neither `str` nor `int`). Since `model_type` is virtually always a string (e.g. `'BM2'`), the mesh was never attached to `sg` and IDs were never generated for the gmsh/meshio conversion path.

2. **`sgio/iofunc/vabs/_mesh.py` — tab/space inconsistency**: The entire `read_buffer` function body used tabs while the rest of the file used 4-space indentation. This violates PEP 8 and can cause issues in mixed-indent environments.

3. **`tests/file_io/vabs/test_vabs_input.py` — nested test function**: `test_vabs_reader_populates_node_and_element_ids` was accidentally defined inside `test_vabs_solver_execution`, making it invisible to pytest.

**Solution**:

1. **`sgio/iofunc/main.py`**: Moved `sg.smdim = smdim`, `sg.model = _submodel`, `sg.mesh = mesh`, `ensure_node_ids(mesh)`, and the `element_id` generation block outside the `else:` branch so they execute for all `model_type` values.

2. **`sgio/iofunc/vabs/_mesh.py`**: Replaced all tab indentation in `read_buffer` with 4-space indentation. Also moved the `from sgio.core.numbering import ...` to the top of the function.

3. **`tests/file_io/vabs/test_vabs_input.py`**: Moved `test_vabs_reader_populates_node_and_element_ids` and its decorators to module level (de-indented by one level).

**Test Results**: 66 unit/format-requirements/VABS tests passing; 6 SwiftComp file-IO tests passing.

**Status**: Fixed

**Assignee**: AI Agent

**Reviewer**: User
