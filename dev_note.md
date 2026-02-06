# Developer Notes - SGIO

## Node and Element Numbering System Review

**Date**: 2026-02-06  
**Status**: Code Review Completed

---

## Executive Summary

SGIO implements a **dual numbering system** to handle mesh data conversion between formats with different numbering requirements:

1. **Internal (0-based)**: All mesh connectivity uses Python/NumPy array indices (0-based)
2. **External (format-specific)**: Original IDs preserved in `point_data['node_id']` and `cell_data['element_id']`

This design enables:
- ✅ Round-trip preservation of original numbering from files
- ✅ Format-agnostic internal processing
- ✅ Format-specific writing with appropriate numbering rules

---

## Format-Specific Requirements

| Format | Node Numbering | Element Numbering | Special Requirements |
|--------|----------------|-------------------|----------------------|
| **Abaqus** | Arbitrary, non-consecutive, no 0 | Arbitrary, non-consecutive | Supports element/node sets (elset/nset) |
| **VABS** | Consecutive from 1 | Consecutive from 1 | Fixed-width zero-padding for some elements |
| **SwiftComp** | Consecutive from 1 | Consecutive from 1 | Zero-padding encodes element type |
| **Gmsh** | 1-based entity tags | 1-based entity tags | Hierarchical entity relationships |
| **Internal (meshio)** | 0-based array indices | 0-based array indices | All connectivity uses indices |

---

## Data Structure Contract

### Points and Nodes
```python
mesh.points              # NumPy array shape (n_nodes, 3), 0-based indexing
mesh.point_data['node_id']  # List of original node IDs from file (arbitrary)
```

**Contract**: Element connectivity in `mesh.cells[*].data` MUST contain 0-based indices into `mesh.points`, NOT original node IDs.

### Cells and Elements
```python
mesh.cells  # List of CellBlock(type, data)
mesh.cells[i].data  # NumPy array of connectivity, values are 0-based node indices
mesh.cell_data['element_id']  # List of lists, original element IDs per cell block
```

**Example**:
```python
# File contains nodes: ID=100 at [0,0,0], ID=200 at [1,0,0], ID=300 at [0,1,0]
mesh.points = [[0,0,0], [1,0,0], [0,1,0]]  # 0-based array
mesh.point_data['node_id'] = [100, 200, 300]  # Original IDs

# File contains element: ID=5000 with nodes [100, 200, 300]
mesh.cells[0].data = [[0, 1, 2]]  # 0-based indices into mesh.points
mesh.cell_data['element_id'] = [[5000]]  # Original element ID
```

---

## Critical Issues Found

### 🔴 CRITICAL BUG: Abaqus Reader Node ID Conversion

**Location**: `sgio/iofunc/abaqus/_abaqus.py:236-240`

**Problem**: The Abaqus reader stores original node IDs in cell connectivity instead of converting to 0-based array indices:

```python
for _eid, _elem in elems.items():
    _nids = list(map(int, _elem.data[1:]))  # Keeps original IDs (WRONG!)
    cells[cell_block_i][1].append(_nids)
```

**Should be**:
```python
for _eid, _elem in elems.items():
    _nids_original = list(map(int, _elem.data[1:]))
    _nids = [nid2pid[nid] for nid in _nids_original]  # Convert to 0-based indices
    cells[cell_block_i][1].append(_nids)
```

**Impact**: 
- ❌ Breaks round-trip conversion for Abaqus files with non-consecutive node numbering
- ❌ Causes `IndexError` when accessing `mesh.points[large_node_id]`
- ❌ Violates meshio data structure contract

**Priority**: **MUST FIX IMMEDIATELY**

---

### 🟡 Missing Validation: No Format Requirement Checks

**Problem**: Writers don't validate that numbering meets format requirements before writing.

**Scenario**: 
1. Read Abaqus file with arbitrary node IDs [10, 50, 100]
2. Write to VABS with `renumber_nodes=False`
3. Result: Invalid VABS file (requires consecutive 1, 2, 3...)

**Impact**: Silent generation of invalid output files

**Priority**: **HIGH - Add validation**

---

### 🟡 Missing Validation: No Duplicate Detection

**Problem**: No validation for:
- Duplicate node IDs
- Duplicate element IDs  
- Node ID = 0 in Abaqus (forbidden)

**Priority**: **HIGH - Add validation**

---

### 🟠 API Consistency: Confusing Parameter Names

**Problem**: `renumber_nodes` and `renumber_elements` don't actually renumber the mesh data; they control write behavior.

**Recommendation**: Rename to `use_sequential_node_ids`, `force_consecutive_numbering`, or similar.

**Priority**: **MEDIUM - API improvement**

---

### 🟠 Missing Utilities: No Helper Functions

**Problem**: Common operations require understanding internal structure:
- Validating numbering for a format
- Getting node ID to index mapping
- Converting IDs to indices

**Recommendation**: Create `sgio/core/numbering.py` with utilities:
```python
def validate_numbering(mesh, format='vabs')
def get_node_id_mapping(mesh) -> dict[int, int]
def ensure_element_ids(mesh)
```

**Priority**: **MEDIUM - Developer experience**

---

## Implementation in Key Modules

### Reading Workflow

```
File Format → Reader → Mesh Structure
                ↓
           Parse nodes with original IDs
                ↓
           Create point_ids mapping: {original_id: 0-based_index}
                ↓
           Parse elements and convert node IDs to indices
                ↓
           Store original IDs in point_data/cell_data
```

**Example**: `sgio/iofunc/_meshio.py:389-433` (`_read_nodes`)

```python
def _read_nodes(f, nnodes, sgdim):
    points = []
    point_ids = {}  # Mapping: {original_id: array_index}
    counter = 0
    
    for line in file:
        point_id, coords = line[0], line[1:]
        point_ids[int(point_id)] = counter  # Store mapping
        points.append(coords)
        counter += 1
    
    return points, point_ids, line
```

### Writing Workflow

```
Mesh Structure → Writer → File Format
        ↓
   Check renumber_nodes flag
        ↓
   If True: Use sequential 1, 2, 3...
   If False: Use stored node_id from point_data
        ↓
   Convert connectivity: indices → node IDs
        ↓
   Apply format-specific padding/ordering
```

**Example**: `sgio/iofunc/_meshio.py:616-680` (`_meshio_to_sg_order`)

```python
def _meshio_to_sg_order(cell_type, idx, node_id=[], renumber_nodes=True):
    idx_sg = np.asarray(idx)
    
    if renumber_nodes:
        if len(node_id) == 0:
            idx_sg = np.asarray(idx) + 1  # 0-based → 1-based
        else:
            # Map array index to sequential ID
            idx_map = {v: i+1 for i, v in enumerate(node_id)}
            idx_sg = np.vectorize(idx_map.get)(idx_sg)
    
    # Apply element-specific zero-padding
    # ... (padding logic)
    
    return idx_sg
```

---

## Code Locations Reference

### Core Mesh Module
- **File**: `sgio/core/mesh.py`
- **Key Functions**:
  - `renumber_elements()` (line 360-368): Renumber elements consecutively from 1
  - `check_cell_ordering()` (line 195-247): Validate cell node ordering
  - `get_invalid_cell_ordering_element_ids()` (line 250-310): Get invalid element IDs

### Mesh I/O Utilities
- **File**: `sgio/iofunc/_meshio.py`
- **Key Functions**:
  - `_read_nodes()` (line 389-433): Read nodes and create ID mapping
  - `_write_nodes()` (line 524-612): Write nodes with renumbering option
  - `_meshio_to_sg_order()` (line 616-680): Convert connectivity to SG format
  - `_sg_to_meshio_order()` (line 438-482): Convert connectivity from SG format
  - `add_cell_dict_data_to_mesh()` (line 263-310): Add element data using element IDs

### Abaqus I/O
- **File**: `sgio/iofunc/abaqus/_abaqus.py`
- **Reading**:
  - `process_mesh()` (line 166-469): Main mesh processing
  - Lines 171-182: Node ID preservation with `nid2pid` mapping
  - Lines 193-244: Element reading (**BUG HERE** - not using `nid2pid`)
  - Lines 418-426: Cell data structure with element IDs

### VABS I/O
- **File**: `sgio/iofunc/vabs/_mesh.py`
- **Writing**:
  - `write_buffer()` (line 234-286): Main write function
  - `_write_elements()` (line 315-403): Element writing with consecutive ID generation
  - Uses `consecutive_index` counter for sequential numbering

### SwiftComp I/O
- **File**: `sgio/iofunc/swiftcomp/_mesh.py`
- **Writing**:
  - `write_buffer()` (line 434-482): Main write function with validation
  - `_write_elements()` (line 486-572): Element writing with auto-increment

### Gmsh I/O
- **File**: `sgio/iofunc/gmsh/_gmsh41_refactored.py`
- **Constants**:
  - `GMSH_NODE_TAG_OFFSET = 1` (line 78): Offset for 1-based indexing
- **Reading/Writing**: Lines 427, 967 - Apply offset conversion

---

## Action Items

### Phase 1: Fix Critical Bugs (REQUIRED)

- [ ] **Fix Abaqus reader node ID conversion bug**
  - File: `sgio/iofunc/abaqus/_abaqus.py:236-240`
  - Change: Use `nid2pid[nid]` to convert to array indices
  - Test: Round-trip with non-consecutive node IDs [100, 200, 300]

- [ ] **Add validation before VABS/SwiftComp write**
  - Files: `sgio/iofunc/vabs/_mesh.py`, `sgio/iofunc/swiftcomp/_mesh.py`
  - Add: Check numbering is consecutive from 1 when `renumber_nodes=False`
  - Error: Raise `ValueError` with helpful message if validation fails

### Phase 2: Add Validation Framework (HIGH PRIORITY)

- [ ] **Create validation module**
  - New file: `sgio/core/numbering.py`
  - Functions:
    - `validate_node_ids(node_ids, format='generic')`
    - `validate_element_ids(element_ids, format='generic')`
    - `get_node_id_mapping(mesh)`
    - `ensure_element_ids(mesh)`

- [ ] **Add duplicate detection**
  - Check for duplicate node/element IDs
  - Check for forbidden ID=0 in Abaqus

- [ ] **Add error handling in `renumber_elements()`**
  - File: `sgio/core/mesh.py:360-368`
  - Add: Check `mesh.cell_data['element_id']` exists

### Phase 3: Improve API & Documentation (MEDIUM PRIORITY)

- [ ] **Rename confusing parameters**
  - `renumber_nodes` → `use_sequential_node_ids`
  - `renumber_elements` → `use_sequential_element_ids`
  - Add deprecation warnings for old names

- [ ] **Create numbering documentation**
  - New file: `docs/source/developer/numbering.md`
  - Content: Dual numbering system, format requirements, common pitfalls

- [ ] **Add module-level docstrings**
  - File: `sgio/core/mesh.py`
  - Explain: Numbering contract, data structure conventions

### Phase 4: Testing (REQUIRED)

- [ ] **Create comprehensive numbering tests**
  - New file: `tests/unit/test_numbering.py`
  - Tests:
    - `test_abaqus_arbitrary_numbering()`: Non-consecutive IDs
    - `test_vabs_requires_consecutive()`: Validation catches errors
    - `test_duplicate_node_ids()`: Duplicate detection
    - `test_round_trip_numbering()`: Preserve IDs through read/write cycle
    - `test_node_id_mapping()`: Verify ID→index conversion

---

## Testing Strategy

### Unit Tests (Required)

```python
# tests/unit/test_numbering.py

def test_abaqus_arbitrary_numbering():
    """Test reading Abaqus with non-consecutive node IDs."""
    # Create test file with nodes [100, 200, 300]
    sg = read('test_arbitrary.inp', sgdim=3, model='sd1')
    
    # Verify original IDs preserved
    assert sg.mesh.point_data['node_id'] == [100, 200, 300]
    
    # Verify connectivity uses array indices (0, 1, 2) not original IDs
    assert sg.mesh.cells[0].data[0].tolist() == [0, 1, 2]
    
    # Verify can access points without IndexError
    for idx in sg.mesh.cells[0].data[0]:
        point = sg.mesh.points[idx]  # Should work!

def test_vabs_requires_consecutive():
    """Test VABS writer validates consecutive numbering."""
    mesh = create_mesh_with_arbitrary_ids([10, 50, 100])
    
    with pytest.raises(ValueError, match="consecutive.*starting from 1"):
        write('output.vab', mesh, renumber_nodes=False)

def test_duplicate_node_ids():
    """Test validation catches duplicate node IDs."""
    result = validate_node_ids([1, 2, 2, 3])
    assert not result['valid']
    assert 'duplicate' in result['errors'][0].lower()

def test_round_trip_numbering():
    """Test numbering preserved through read→write→read cycle."""
    # Read Abaqus with arbitrary IDs
    sg1 = read('test.inp', sgdim=3, model='sd1')
    original_nids = sg1.mesh.point_data['node_id']
    original_eids = sg1.mesh.cell_data['element_id']
    
    # Write back to Abaqus (preserves IDs)
    write('output.inp', sg1, renumber_nodes=False)
    
    # Read again
    sg2 = read('output.inp', sgdim=3, model='sd1')
    
    # Verify IDs preserved
    assert sg2.mesh.point_data['node_id'] == original_nids
    assert sg2.mesh.cell_data['element_id'] == original_eids
```

### Integration Tests (Recommended)

```python
def test_format_conversion_abaqus_to_vabs():
    """Test converting Abaqus (arbitrary IDs) to VABS (consecutive)."""
    sg = read('test_arbitrary.inp', sgdim=2, model='pl1')
    
    # Should automatically renumber for VABS
    write('output.vab', sg, renumber_nodes=True)
    
    # Read back and verify consecutive numbering
    sg2 = read_vabs('output.vab', sgdim=2)
    node_ids = sg2.mesh.point_data['node_id']
    assert node_ids == list(range(1, len(node_ids) + 1))
```

---

## Questions for Discussion

1. **Backward Compatibility**: The Abaqus reader fix will change behavior. Should we add a flag to maintain old behavior temporarily?

2. **Auto-Renumbering**: Should writers automatically renumber if validation fails (with a warning), or strictly fail?

3. **Performance**: The validation functions will add overhead. Should they be optional via a global flag?

4. **Migration Path**: How to communicate breaking changes to existing users?

---

## Related Documentation

- Main README: `README.md`
- Developer guide: `AGENTS.md`
- Test configuration: `tests/pytest.ini`
- Documentation source: `docs/source/`

---

**Last Updated**: 2026-02-06  
**Reviewed By**: Claude Code (AI Assistant)  
**Next Review**: After implementing Phase 1 fixes
