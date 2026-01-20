# Critical Issue #1: Mutable Default Arguments

**Date:** 2026-01-20  
**File:** `sgio/model/general.py`  
**Classes:** `State`, `StateCase`  
**Severity:** 🔴 Critical

## Problem

### Description
Both `State.__init__()` and `StateCase.__init__()` used mutable default arguments (empty dictionaries and lists). This is a classic Python anti-pattern that leads to unexpected behavior where all instances share the same default object.

### Affected Code (Before Fix)

**State class (line 81-82):**
```python
def __init__(self, name='', data={}, label=[], location=''):
    self.name = name
    self.label = label
    self.location = location
    self.data = data
```

**StateCase class (line 211):**
```python
def __init__(self, case:dict={}, states:dict={}):
    self._case = case
    self._states = states
```

### Impact

1. **Shared State Bug:** Multiple instances created without explicit arguments would share the same dictionary/list objects
2. **Data Corruption:** Modifying data in one instance would affect all other instances using the default
3. **Hard to Debug:** The bug only manifests when default arguments are used, making it intermittent and difficult to trace

### Example of the Bug

```python
# Before fix - BUGGY CODE
state1 = State()  # Uses default data={}
state2 = State()  # Uses the SAME default data={}

state1.data[1] = [1.0, 2.0, 3.0]
print(state2.data)  # Output: {1: [1.0, 2.0, 3.0]} - UNEXPECTED!
```

## Solution

### Fix Applied

Changed mutable default arguments to `None` and initialize them inside the constructor:

**State class:**
```python
def __init__(self, name='', data=None, label=None, location=''):
    self.name = name
    self.label = label if label is not None else []
    self.location = location
    self.data = data if data is not None else {}
```

**StateCase class:**
```python
def __init__(self, case:dict=None, states:dict=None):
    self._case = case if case is not None else {}
    self._states = states if states is not None else {}
```

### Why This Works

- Each instance now gets its own unique empty dictionary/list
- The pattern `x if x is not None else {}` is the standard Python idiom for mutable defaults
- Maintains backward compatibility - existing code passing explicit arguments works unchanged

### Documentation Updates

Updated docstrings to indicate that `data` and `label` parameters are optional and describe the default behavior.

## Testing Recommendations

1. **Unit Test:** Create multiple instances without arguments and verify they don't share state
2. **Integration Test:** Verify existing code that passes explicit arguments still works
3. **Edge Case:** Test with `None` explicitly passed as an argument

```python
# Recommended test
def test_state_independent_defaults():
    state1 = State()
    state2 = State()
    
    state1.data[1] = [1.0, 2.0]
    assert 1 not in state2.data  # Should pass now
    
    state1.label.append('test')
    assert 'test' not in state2.label  # Should pass now
```

## References

- [Python Anti-Patterns: Mutable Default Arguments](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)
- PEP 8 Programming Recommendations
- "Effective Python" by Brett Slatkin, Item 24

## Related Issues

This fix also improves consistency with Python best practices and makes the code more maintainable.

