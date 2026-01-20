# Major Issue #5: Inconsistent Documentation

**Date:** 2026-01-20  
**File:** `sgio/model/general.py`  
**Class:** `State`  
**Severity:** 🟡 Major

## Problem

### Description
The documentation for the `location` parameter was inconsistent between the class docstring and the `__init__` method docstring. The class docstring stated location could be `'node'` or `'element'`, but the `__init__` docstring mentioned a third option: `'element_node'`.

### Affected Code (Before Fix)

**Class docstring (line 78):**
```python
location : str
    The location type of the state, either 'node' or 'element'.
```

**__init__ docstring (line 95):**
```python
location : str
    The location type of the state, either 'node', 'element', or 'element_node.
```

### Impact

1. **API Confusion:** Developers don't know which values are actually valid
2. **Documentation Mismatch:** Inconsistent docs reduce trust in the codebase
3. **Integration Issues:** Code using `'element_node'` might seem wrong based on class docs

### Evidence from Codebase

Looking at actual usage in the codebase (from `sgio/iofunc/main.py`):

```python
# Line 399
state=sgmodel.State(
    name="u", data=u, label=["u1", "u2", "u3"], location="node"
)

# Line 437
state=sgmodel.State(
    name=_comp,
    data=_data,
    label=[_comp,],
    location='element_node'  # ✅ element_node IS used!
)
```

This confirms that `'element_node'` is a valid and actively used location type.

## Solution

### Fix Applied

Updated the class docstring to include all three valid location types:

```python
location : str
    The location type of the state, either 'node', 'element', or 'element_node'.
```

### Why This Fix

- **Accuracy:** Reflects actual usage in the codebase
- **Completeness:** Documents all valid options
- **Consistency:** Both docstrings now match

## Valid Location Types

Based on the codebase analysis, the three valid location types are:

1. **`'node'`** - Data associated with mesh nodes (e.g., displacement)
2. **`'element'`** - Data associated with elements (e.g., element-averaged stress)
3. **`'element_node'`** - Data associated with nodes within elements (e.g., element nodal stress)

## Testing

No functional changes - documentation only. Verified by:
1. Searching codebase for all uses of `location=` parameter
2. Confirming all three types are used in production code

## References

- Consistent documentation is critical for API usability
- Documentation should reflect actual implementation and usage

