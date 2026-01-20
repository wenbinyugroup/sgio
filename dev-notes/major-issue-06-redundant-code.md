# Major Issue #6: Redundant Code in StateCase.at()

**Date:** 2026-01-20  
**File:** `sgio/model/general.py`  
**Class:** `StateCase`  
**Method:** `at()`  
**Severity:** 🟡 Major

## Problem

### Description
The `StateCase.at()` method called `self.states[_name].at(locs)` twice for each state - once to check if it's `None`, and again to store the result. This is wasteful and inefficient.

### Affected Code (Before Fix)

**Lines 407-410:**
```python
for _name in _state_names:
    _state = self.states[_name].at(locs)  # First call
    if not _state is None:
        states[_name] = self.states[_name].at(locs)  # Second call - REDUNDANT!
```

### Impact

1. **Performance:** Doubles the execution time for this operation
2. **Memory:** Creates temporary objects that are immediately discarded
3. **Code Quality:** Violates DRY (Don't Repeat Yourself) principle
4. **Maintainability:** If `at()` logic changes, this redundancy could cause bugs

### Performance Analysis

For a `StateCase` with N states and M locations:
- **Before:** 2N calls to `State.at()` (including deep copy operations)
- **After:** N calls to `State.at()`
- **Improvement:** 50% reduction in method calls

Example scenario:
- 10 states, 1000 locations each
- Before: 20 calls to `at()`, each doing deep copy of 1000 items
- After: 10 calls to `at()`
- **Result:** ~50% faster execution

## Solution

### Fix Applied

Store the result of the first call and reuse it:

```python
for _name in _state_names:
    _state = self.states[_name].at(locs)
    if _state is not None:
        states[_name] = _state  # Reuse the already-computed result
```

### Additional Improvements

Also fixed the non-Pythonic comparison:
- **Before:** `if not _state is None:`
- **After:** `if _state is not None:`

This follows PEP 8 style guidelines.

## Testing Recommendations

```python
def test_statecase_at_efficiency():
    """Verify at() doesn't call State.at() redundantly."""
    from unittest.mock import Mock, patch
    
    state_case = StateCase()
    state = State(name='test', data={1: [1.0], 2: [2.0]})
    state_case.addState('test', state=state)
    
    # Mock the State.at method to count calls
    with patch.object(State, 'at', wraps=state.at) as mock_at:
        result = state_case.at([1])
        
        # Should only be called once per state
        assert mock_at.call_count == 1

def test_statecase_at_correctness():
    """Verify at() still returns correct results."""
    state_case = StateCase()
    state1 = State(name='s1', data={1: [1.0], 2: [2.0]})
    state2 = State(name='s2', data={1: [3.0], 2: [4.0]})
    
    state_case.addState('s1', state=state1)
    state_case.addState('s2', state=state2)
    
    result = state_case.at([1])
    
    assert result is not None
    assert 's1' in result.states
    assert 's2' in result.states
    assert result.states['s1'].data == [1.0]
```

## Code Quality Improvements

This fix demonstrates several best practices:

1. **DRY Principle:** Don't repeat expensive operations
2. **Performance:** Cache results when possible
3. **PEP 8 Compliance:** Use `is not None` instead of `not is None`
4. **Readability:** Clearer intent - we're reusing the computed value

## References

- DRY Principle: "Every piece of knowledge must have a single, unambiguous, authoritative representation"
- PEP 8: Style Guide for Python Code
- "Clean Code" by Robert C. Martin: Avoid duplication

