# Node and Element Numbering System

This guide explains SGIO's automatic node/element numbering system and how to implement readers and writers correctly.

## Overview

SGIO implements a **dual numbering system** with **automatic format-aware renumbering**:

1. **Internal (0-based)**: All mesh connectivity uses Python/NumPy array indices (0-based)
2. **External (format-specific)**: Node/element IDs stored in `point_data['node_id']` and `cell_data['element_id']`
3. **Automatic enforcement**: Writers automatically ensure numbering complies with format requirements

### Key Principles

- **Readers** preserve original numbering from files (no modification)
- **Writers** automatically renumber to meet format requirements (with warnings)
- **Users** never need to manage renumbering flags or validate numbering
- **Round-trip** fidelity for formats that support arbitrary numbering (Abaqus, Gmsh)

## Format-Specific Requirements

SGIO enforces these numbering rules automatically:

| Format | Node Numbering | Element Numbering | Enforced By |
|--------|----------------|-------------------|-------------|
| **VABS** | Consecutive 1-based (1,2,3,...) | Consecutive 1-based (1,2,3,...) | `auto_renumber_for_format(mesh, 'vabs')` |
| **SwiftComp** | Consecutive 1-based (1,2,3,...) | Consecutive 1-based (1,2,3,...) | `auto_renumber_for_format(mesh, 'swiftcomp')` |
| **Abaqus** | Arbitrary 1-based (non-zero) | Arbitrary 1-based (non-zero) | `auto_renumber_for_format(mesh, 'abaqus')` |
| **Gmsh** | Format-specific tags | Format-specific tags | No renumbering (meshio handles) |
| **Internal (meshio)** | 0-based array indices | 0-based array indices | Connectivity only |

**Automatic behavior**:
- Converting Abaqus → VABS automatically renumbers `[10, 50, 100]` → `[1, 2, 3]` (with warning)
- Converting VABS → Abaqus preserves sequential `[1, 2, 3]` (no warning)
- Writing Abaqus → Abaqus preserves original IDs `[10, 50, 100]` (no renumbering)

## Data Structure Contract

### Points and Nodes

```python
mesh.points                  # NumPy array shape (n_nodes, 3), 0-based indexing
mesh.point_data['node_id']   # NumPy array of original node IDs from file
```

**Contract**: Element connectivity in `mesh.cells[*].data` MUST contain **0-based indices** into `mesh.points`, NOT original node IDs.

### Cells and Elements

```python
mesh.cells                   # List of CellBlock(type, data)
mesh.cells[i].data           # NumPy array of connectivity, values are 0-based node indices
mesh.cell_data['element_id'] # List of NumPy arrays, original element IDs per cell block
```

### Example

```python
# File contains nodes: ID=100 at [0,0,0], ID=200 at [1,0,0], ID=300 at [0,1,0]
mesh.points = [[0,0,0], [1,0,0], [0,1,0]]  # 0-based array
mesh.point_data['node_id'] = np.array([100, 200, 300])  # Original IDs

# File contains element: ID=5000 with nodes [100, 200, 300]
mesh.cells[0].data = np.array([[0, 1, 2]])  # 0-based indices into mesh.points
mesh.cell_data['element_id'] = [np.array([5000])]  # Original element ID
```

## Automatic Numbering API

### Core Functions

```python
from sgio.core.numbering import (
    ensure_node_ids,           # Create node_id if missing
    ensure_element_ids,        # Create element_id if missing
    auto_renumber_for_format,  # Enforce format requirements
)

# Example: Automatic ID generation
mesh = SGMesh(points, cells)
ensure_node_ids(mesh)         # Adds node_id = [1, 2, 3, ...] if missing
ensure_element_ids(mesh)      # Adds element_id = [1, 2, 3, ...] if missing

# Example: Format-aware renumbering
nodes_changed, elems_changed = auto_renumber_for_format(mesh, format='vabs')
# Returns: (True, True) if renumbering occurred, (False, False) if already compliant
# Emits UserWarning if renumbering was needed
```

### Writer Call Chain

**All writers automatically call**:
```python
def write_buffer(f, mesh, sgdim, model_space, **kwargs):
    # 1. Ensure IDs exist
    ensure_node_ids(mesh)
    ensure_element_ids(mesh)
    
    # 2. Auto-renumber for format
    auto_renumber_for_format(mesh, format='vabs')  # or 'swiftcomp', 'abaqus'
    
    # 3. Write with guaranteed-valid numbering
    _write_nodes(f, mesh.points, mesh.point_data['node_id'])
    _write_elements(f, mesh.cells, mesh.cell_data['element_id'])
```

**Users never need to call these functions** — they're internal to writers.

## Reading Workflow

When implementing a reader for a new format:

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
                ↓
           Call ensure_node_ids() and ensure_element_ids()
```

### Example Implementation

```python
def read_buffer(f, sgdim):
    """Read mesh from format-specific file buffer."""
    points = []
    point_ids_mapping = {}  # {original_id: array_index}
    point_ids_list = []     # Ordered list for point_data['node_id']
    
    counter = 0
    for line in f:
        if line.startswith('NODE'):
            node_id, x, y, z = parse_node_line(line)
            point_ids_mapping[int(node_id)] = counter  # Store mapping
            point_ids_list.append(int(node_id))        # Store original ID
            points.append([x, y, z])
            counter += 1
    
    # Parse elements and convert node IDs → array indices
    cells = []
    element_ids = []
    for line in f:
        if line.startswith('ELEMENT'):
            elem_id, elem_type, *node_ids_orig = parse_element_line(line)
            # CRITICAL: Convert to 0-based indices
            node_indices = [point_ids_mapping[nid] for nid in node_ids_orig]
            cells.append(node_indices)
            element_ids.append(int(elem_id))
    
    # Build mesh
    mesh = SGMesh(
        points=np.array(points),
        cells=[("triangle", np.array(cells))],
        point_data={"node_id": np.array(point_ids_list)},
        cell_data={"element_id": [np.array(element_ids)]}
    )
    
    # Ensure IDs are populated (handles edge cases)
    ensure_node_ids(mesh)
    ensure_element_ids(mesh)
    
    return mesh
```

### Common Reading Mistakes

❌ **WRONG**: Store original node IDs in connectivity
```python
# This is WRONG - stores original IDs, not array indices
for eid, node_ids_original in elements.items():
    cells.append(node_ids_original)  # ERROR: these are IDs, not indices!
```

✅ **CORRECT**: Convert to array indices
```python
# This is CORRECT - converts to 0-based indices
for eid, node_ids_original in elements.items():
    node_indices = [nid2idx[nid] for nid in node_ids_original]
    cells.append(node_indices)  # OK: these are 0-based indices
```

❌ **WRONG**: Forget to store original IDs
```python
# Missing point_data['node_id'] - breaks round-trip fidelity
mesh = SGMesh(points, cells)
```

✅ **CORRECT**: Always preserve original IDs
```python
# Store original IDs for round-trip preservation
mesh = SGMesh(
    points, cells,
    point_data={"node_id": np.array(point_ids_list)},
    cell_data={"element_id": [np.array(element_ids)]}
)
```

## Writing Workflow

When implementing a writer for a new format:

```
Mesh Structure → Writer → File Format
        ↓
   Call ensure_node_ids(mesh)
        ↓
   Call ensure_element_ids(mesh)
        ↓
   Call auto_renumber_for_format(mesh, format)
        ↓
   Write nodes using mesh.point_data['node_id']
        ↓
   Convert connectivity: indices → node IDs
        ↓
   Write elements using mesh.cell_data['element_id']
```

### Example Implementation

```python
from sgio.core.numbering import ensure_node_ids, ensure_element_ids, auto_renumber_for_format

def write_buffer(f, mesh, sgdim, model_space, **kwargs):
    """Write mesh to format-specific file buffer."""
    # Step 1: Ensure IDs exist (generates sequential if missing)
    ensure_node_ids(mesh)
    ensure_element_ids(mesh)
    
    # Step 2: Auto-renumber for format (warns if changes made)
    auto_renumber_for_format(mesh, format='vabs')  # or 'swiftcomp', 'abaqus'
    
    # Step 3: Write nodes
    node_ids = mesh.point_data['node_id']
    for i, point in enumerate(mesh.points):
        nid = node_ids[i]
        f.write(f"{nid:8d} {point[0]:20.12e} {point[1]:20.12e} {point[2]:20.12e}\n")
    
    # Step 4: Write elements (convert connectivity indices → node IDs)
    element_ids = mesh.cell_data['element_id'][0]  # First cell block
    cells = mesh.cells[0].data
    for i, cell in enumerate(cells):
        eid = element_ids[i]
        # Convert 0-based indices to node IDs
        node_ids_for_elem = [node_ids[idx] for idx in cell]
        f.write(f"{eid:8d} {' '.join(map(str, node_ids_for_elem))}\n")
```

**Note**: No manual validation needed! `auto_renumber_for_format` guarantees compliance.

## Validation Utilities (Advanced)

For advanced use cases, validation functions are available:

```python
from sgio.core.numbering import validate_node_ids, validate_element_ids
from sgio.core.format_requirements import FormatNumberingRequirements

# Manual validation (usually not needed - auto_renumber handles this)
validate_node_ids([1, 2, 3, 4], format='vabs')     # OK
validate_node_ids([10, 50, 100], format='vabs')    # Raises ValueError

# Check requirements programmatically
req = FormatNumberingRequirements.get_requirements('vabs')
print(req.node_consecutive)  # True
print(req.node_start)        # 1
```

## Warning Messages

Users will see `UserWarning` when automatic renumbering occurs:

```
UserWarning: Node IDs were automatically renumbered to meet VABS format requirements 
(consecutive numbering starting from 1). Original IDs: [10, 50, 100] → New IDs: [1, 2, 3].
```

**When warnings appear**:
- Converting between formats with different requirements (Abaqus → VABS)
- Writing mesh with non-compliant numbering
- Mesh created programmatically without proper IDs

**No warning when**:
- IDs already comply with format requirements
- Round-trip within same format (Abaqus → Abaqus)
- Sequential 1-based numbering used throughout

## Testing

When writing tests for readers/writers:

```python
def test_round_trip_numbering():
    """Test numbering preserved through read→write→read cycle."""
    # Read file with arbitrary IDs
    sg1 = read('test.inp', file_format='abaqus', sgdim=3, model_type='sd1')
    original_nids = sg1.mesh.point_data['node_id'].copy()
    
    # Write back to same format
    write('output.inp', sg1, file_format='abaqus')
    
    # Read again
    sg2 = read('output.inp', file_format='abaqus', sgdim=3, model_type='sd1')
    
    # Verify IDs preserved (no renumbering for Abaqus → Abaqus)
    np.testing.assert_array_equal(sg2.mesh.point_data['node_id'], original_nids)

def test_auto_renumbering_cross_format():
    """Test automatic renumbering when converting formats."""
    # Create Abaqus mesh with non-consecutive IDs
    sg = read('test.inp', file_format='abaqus', sgdim=2, model_type='bm2')
    assert list(sg.mesh.point_data['node_id']) == [10, 50, 100]
    
    # Write to VABS (requires consecutive)
    with pytest.warns(UserWarning, match="[Nn]ode.*renumbered"):
        write('output.vab', sg, file_format='vabs')
    
    # Verify renumbering occurred
    sg_vabs = read('output.vab', file_format='vabs', sgdim=2, model_type='bm2')
    assert list(sg_vabs.mesh.point_data['node_id']) == [1, 2, 3]

def test_ensure_ids_creates_when_missing():
    """Test ID generation for programmatically-created meshes."""
    from sgio.core.numbering import ensure_node_ids, ensure_element_ids
    
    # Create mesh without IDs
    mesh = SGMesh(
        points=np.array([[0,0,0], [1,0,0], [0,1,0]]),
        cells=[("triangle", np.array([[0, 1, 2]]))]
    )
    
    # Generate IDs
    ensure_node_ids(mesh)
    ensure_element_ids(mesh)
    
    # Verify sequential 1-based numbering
    assert list(mesh.point_data['node_id']) == [1, 2, 3]
    assert list(mesh.cell_data['element_id'][0]) == [1]
```

## Common Pitfalls

### 1. Using Original IDs in Connectivity

❌ **WRONG**:
```python
# Trying to access point using original ID
point = mesh.points[100]  # IndexError if only 3 nodes!
```

✅ **CORRECT**:
```python
# Use array indices from connectivity
for node_idx in mesh.cells[0].data[0]:
    point = mesh.points[node_idx]  # Always works
```

### 2. Modifying Mesh After Writing

❌ **RISKY**:
```python
# Write to VABS (renumbers internally)
write('output.vab', sg, file_format='vabs')

# sg.mesh now has renumbered IDs [1,2,3], not original [10,50,100]!
# Writing to Abaqus would use [1,2,3], not original numbering
```

✅ **SAFE**:
```python
# Make a copy before writing if you need to preserve original
import copy
sg_copy = copy.deepcopy(sg)
write('output.vab', sg_copy, file_format='vabs')

# Original sg.mesh unchanged, can write with original IDs
write('output.inp', sg, file_format='abaqus')
```

### 3. Assuming IDs Equal Indices

❌ **WRONG**:
```python
# Assuming node_id matches array index
for i in range(len(mesh.points)):
    nid = mesh.point_data['node_id'][i]
    assert nid == i + 1  # FAILS for arbitrary numbering!
```

✅ **CORRECT**:
```python
# Use mapping when ID→index lookup needed
nid_to_idx = {nid: i for i, nid in enumerate(mesh.point_data['node_id'])}
idx = nid_to_idx[target_node_id]
point = mesh.points[idx]
```

## Deprecated API (Removed)

The following parameters were **removed** in favor of automatic numbering:

| Parameter (REMOVED) | Replacement | Notes |
|---------------------|-------------|-------|
| `renumber_nodes=True/False` | _Automatic_ | Writers always ensure compliance |
| `renumber_elements=True/False` | _Automatic_ | Writers always ensure compliance |
| `use_sequential_node_ids=True/False` | _Automatic_ | Writers always ensure compliance |
| `use_sequential_element_ids=True/False` | _Automatic_ | Writers always ensure compliance |

**Migration**: Remove these parameters from `read()` and `write()` calls. Numbering is now fully automatic.

```python
# Old API (no longer supported)
write('output.vab', sg, renumber_nodes=True)  # ERROR

# New API (current)
write('output.vab', sg, file_format='vabs')   # Automatic renumbering
```

## References

- Main module documentation: `sgio.core.mesh`
- Numbering utilities: `sgio.core.numbering`
- Format requirements: `sgio.core.format_requirements`
- Developer guide: `AGENTS.md`
- User guide: See `docs/source/guide/io.rst`
