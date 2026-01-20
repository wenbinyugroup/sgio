# Critical Issue #3: Missing Error Handling in StateCase.getState()

**Date:** 2026-01-20  
**File:** `sgio/model/general.py`  
**Class:** `StateCase`  
**Method:** `getState()`  
**Severity:** 🔴 Critical

## Problem

### Description
The `StateCase.getState()` method would raise an unhandled `KeyError` if the requested state didn't exist. This was inconsistent with the class's property methods (`displacement`, `rotation`, `load`, `distributed_load`) which return `None` for missing states.

### Affected Code (Before Fix)

**Line 242-255:**
```python
def getState(self, name):
    """Get state by name.

    Parameters
    ----------
    name : str
        State name.

    Returns
    -------
    State
        State object.
    """
    return self._states[name]  # ⚠️ Raises KeyError if name not found
```

**Comparison with property methods (lines 257-276):**
```python
@property
def displacement(self):
    try:
        return self._states['displacement']
    except KeyError:
        return None  # ✅ Returns None instead of raising
```

### Impact

1. **Inconsistent API:** Same class has two different error handling patterns
2. **Unexpected Exceptions:** Callers must wrap in try/except or check if state exists first
3. **Poor Developer Experience:** Inconsistency makes the API harder to learn and use correctly

### Example of the Bug

```python
# Before fix - inconsistent behavior
state_case = StateCase()

# Property method - returns None gracefully
disp = state_case.displacement  # Returns None if not found ✅

# getState method - raises exception
stress = state_case.getState('stress')  # KeyError! ❌

# Caller had to do this:
try:
    stress = state_case.getState('stress')
except KeyError:
    stress = None
```

## Solution

### Fix Applied

Modified `getState()` to catch `KeyError` and return `None`, making it consistent with the property methods:

```python
def getState(self, name):
    """Get state by name.

    Parameters
    ----------
    name : str
        State name.

    Returns
    -------
    State or None
        State object if found, None otherwise.
        
    Notes
    -----
    This method returns None if the state is not found, consistent with
    the property methods (displacement, rotation, load, distributed_load).
    
    Examples
    --------
    >>> state = state_case.getState('displacement')
    >>> if state is not None:
    ...     # use state
    """
    try:
        return self._states[name]
    except KeyError:
        return None
```

### Why This Approach

**Considered Alternatives:**

1. **Keep KeyError, Document It:**
   - ❌ Inconsistent with existing property methods
   - ❌ Less user-friendly API

2. **Change Properties to Raise:**
   - ❌ Breaking change for existing code
   - ❌ More disruptive

3. **Return None (Chosen):** ✅
   - ✅ Consistent with existing property methods
   - ✅ More Pythonic (easier to use)
   - ✅ Matches common pattern in the codebase

### Benefits

1. **Consistency:** All state access methods now behave the same way
2. **Simpler Code:** No need for try/except blocks in calling code
3. **Better Documentation:** Clear examples of proper usage

## Testing Recommendations

1. **Test Missing State:** Verify `None` is returned for non-existent states
2. **Test Existing State:** Verify correct `State` object is returned
3. **Test Consistency:** Verify behavior matches property methods

```python
def test_getState_returns_none_for_missing_state():
    state_case = StateCase()
    result = state_case.getState('nonexistent')
    assert result is None

def test_getState_returns_state_for_existing():
    state = State(name='test', data=[1, 2, 3])
    state_case = StateCase()
    state_case.addState('test', state=state)
    
    result = state_case.getState('test')
    assert result is not None
    assert result.name == 'test'

def test_getState_consistent_with_properties():
    state_case = StateCase()
    
    # Both should return None
    assert state_case.getState('displacement') is None
    assert state_case.displacement is None
```

## Migration Guide

### Before (Old Code)
```python
# Had to use try/except
try:
    state = state_case.getState('stress')
    process(state)
except KeyError:
    # Handle missing state
    pass
```

### After (New Code)
```python
# Simpler, more Pythonic
state = state_case.getState('stress')
if state is not None:
    process(state)
```

## Code Review Guidance

When reviewing code that uses `StateCase.getState()`:
- Ensure return value is checked for `None` before use
- Look for old try/except KeyError blocks that can be simplified
- Verify consistency with property method usage patterns

## Future Considerations

- Consider adding a `has_state(name)` method for explicit existence checking
- Consider adding type hints: `def getState(self, name: str) -> Optional[State]:`
- Document the complete list of standard state names in the class docstring

## References

- Python EAFP principle: "Easier to Ask for Forgiveness than Permission"
- API design: Consistency is key to good developer experience
- "Effective Python" Item 23: Accept Functions Instead of Classes for Simple Interfaces

