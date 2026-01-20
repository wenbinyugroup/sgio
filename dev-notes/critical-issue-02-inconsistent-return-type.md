# Critical Issue #2: Inconsistent Return Type in State.at()

**Date:** 2026-01-20  
**File:** `sgio/model/general.py`  
**Class:** `State`  
**Method:** `at()`  
**Severity:** 🔴 Critical

## Problem

### Description
The `State.at()` method returns either a `State` object or `None`, but this was not clearly documented. This creates an inconsistent API that can lead to `AttributeError` exceptions if callers don't check for `None` before accessing methods or attributes on the returned value.

### Affected Code (Before Fix)

**Line 165-205:**
```python
def at(self, locs:Iterable):
    """Get the state data at a list of given locations.

    Parameters
    ----------
    locs : list
        List of note/element IDs.

    Returns
    -------
    State
        A copy of the State object with the data at the given locations.
    """
    _data = []
    
    # ... processing logic ...
    
    if len(_data) == 0:
        return None  # ⚠️ Returns None but docstring says State
    
    return State(...)
```

### Impact

1. **Runtime Errors:** Code that doesn't check for `None` will crash with `AttributeError`
2. **API Confusion:** Docstring claimed to return `State`, but actually returns `State | None`
3. **Inconsistent Error Handling:** Callers must remember to check for `None`, which is error-prone

### Example of the Bug

```python
# Before fix - could cause AttributeError
state = my_state.at([999])  # Location doesn't exist
print(state.name)  # AttributeError: 'NoneType' object has no attribute 'name'

# Caller had to remember to check:
state = my_state.at([999])
if state is not None:  # Easy to forget this check!
    print(state.name)
```

## Solution

### Fix Applied

Updated the docstring to clearly document the `None` return case and provide usage guidance:

```python
def at(self, locs:Iterable):
    """Get the state data at a list of given locations.

    Parameters
    ----------
    locs : list
        List of node/element IDs.

    Returns
    -------
    State or None
        A copy of the State object with the data at the given locations.
        Returns None if no data is found at the specified locations.
        
    Notes
    -----
    Callers should check for None before using the returned value:
    
        state = my_state.at([1, 2, 3])
        if state is not None:
            # use state
    """
    # ... implementation unchanged ...
```

### Why This Approach

**Considered Alternatives:**

1. **Raise Exception:** Could raise `ValueError` when no data found
   - ❌ Would break existing code that expects `None`
   - ❌ More disruptive change

2. **Return Empty State:** Return `State` with empty data
   - ❌ Harder to distinguish "no data" from "empty data"
   - ❌ Could mask errors

3. **Document Current Behavior:** ✅ Chosen approach
   - ✅ No breaking changes to existing code
   - ✅ Makes API contract explicit
   - ✅ Provides usage guidance

### Additional Fixes

Also fixed typo: "note/element" → "node/element" in the docstring.

## Testing Recommendations

1. **Test None Return:** Verify `None` is returned when locations don't exist
2. **Test Valid Return:** Verify `State` object is returned for valid locations
3. **Test Edge Cases:** Empty location list, single location, multiple locations

```python
def test_state_at_returns_none_for_missing_data():
    state = State(name='test', data={1: [1.0], 2: [2.0]})
    result = state.at([999])  # Non-existent location
    assert result is None

def test_state_at_returns_state_for_valid_data():
    state = State(name='test', data={1: [1.0], 2: [2.0]})
    result = state.at([1])
    assert result is not None
    assert isinstance(result, State)
    assert result.data == [1.0]
```

## Code Review Guidance

When reviewing code that uses `State.at()`, ensure:
- Return value is checked for `None` before use
- Or use defensive programming: `state = my_state.at([1]) or State()`

## Future Considerations

In a future major version (breaking change allowed), consider:
- Using Optional[State] type hint for clarity
- Raising a custom exception for better error messages
- Adding a `get_or_default()` method variant

## References

- Python typing module: `Optional[T]` for nullable returns
- "Effective Python" Item 20: Prefer Raising Exceptions to Returning None

