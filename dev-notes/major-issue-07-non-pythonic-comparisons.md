# Major Issue #7: Non-Pythonic Comparisons

**Date:** 2026-01-20  
**File:** `sgio/model/general.py`  
**Class:** `StateCase`  
**Method:** `addState()`  
**Severity:** 🟡 Major

## Problem

### Description
The code used `not x is None` instead of the Pythonic `x is not None` for None comparisons. This violates PEP 8 style guidelines and reduces code readability.

### Affected Code (Before Fix)

**Lines 364, 367:**
```python
if not state is None:
    self._states[name] = state

elif not entity_id is None:
    self._states[name].addData(
        data=data, loc=entity_id
    )
```

### Impact

1. **Code Style:** Violates PEP 8 recommendations
2. **Readability:** Less intuitive to read than the standard form
3. **Consistency:** Inconsistent with Python community standards
4. **Code Review:** Triggers warnings in linters and IDE tools

### PEP 8 Guidance

From PEP 8 - Programming Recommendations:

> Comparisons to singletons like None should always be done with `is` or `is not`, never the equality operators.
> 
> Use `if foo is not None:` rather than `if not foo is None:`

### Why `is not None` is Better

1. **Operator Precedence:** More explicit about the intended operation
2. **Readability:** Reads more naturally in English
3. **Standard Practice:** Universally recognized Python idiom
4. **Tool Support:** Linters expect this form

## Solution

### Fix Applied

Changed all instances to use the Pythonic form:

**Lines 364, 367:**
```python
if state is not None:
    self._states[name] = state

elif entity_id is not None:
    self._states[name].addData(
        data=data, loc=entity_id
    )
```

### Locations Fixed

1. Line 364: `if not state is None:` → `if state is not None:`
2. Line 367: `elif not entity_id is None:` → `elif entity_id is not None:`

## Additional Context

This fix was also applied in Issue #6 (Redundant Code) where we changed:
- Line 409: `if not _state is None:` → `if _state is not None:`

## Linter Configuration

Most Python linters will flag `not x is None` as a style violation:

**Pylint:** E0712 - Comparison should be 'expr is not None'  
**Flake8:** E714 - test for object identity should be 'is not'  
**Ruff:** SIM201 - Use 'is not' instead of 'not is'

## Testing

No functional changes - style improvement only. The logic remains identical:

```python
# Both are logically equivalent, but the second is preferred
assert (not x is None) == (x is not None)  # Always True
```

## Migration Pattern

When reviewing code, replace:
```python
# ❌ Non-Pythonic
if not x is None:
    ...

# ✅ Pythonic
if x is not None:
    ...
```

## References

- [PEP 8 - Programming Recommendations](https://www.python.org/dev/peps/pep-0008/#programming-recommendations)
- [Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- "Effective Python" by Brett Slatkin - Item 2: Follow the PEP 8 Style Guide

