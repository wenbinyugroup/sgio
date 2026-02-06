# AGENTS.md - Developer Guide for SGIO

This document provides essential information for AI coding agents working on the SGIO codebase.

## Environment Setup

- **Package Manager**: Use `uv` for dependency management
- **Virtual Environment**: Activate with `.venv/Scripts/activate.ps1` (Windows) or `source .venv/bin/activate` (Unix)
- **Python Version**: Requires Python >= 3.9
- **Install Dependencies**: `uv sync` or `pip install -e .`

ALWAYS USE PROJECT LOCAL VENV

Ignore the following files and directories with the name containing `temp`, `archive`, `legacy`, `old`, `backup`, `~`, or `#`.

## Build and Test Commands

### Testing

Activate virtual environment first or use `uv run` to run the following commands:

```bash
# Run all tests
pytest

# Run all tests with verbose output (tests are configured with -v by default)
# pytest configuration is in tests/pytest.ini
pytest tests/

# Run a single test file
pytest tests/unit/test_models.py

# Run a single test class
pytest tests/unit/test_models.py::TestEulerBernoulliBeamModelBasic

# Run a single test function
pytest tests/unit/test_models.py::TestEulerBernoulliBeamModelBasic::test_default_creation

# Run tests by marker
pytest -m unit              # Run only unit tests
pytest -m integration       # Run integration tests
pytest -m "not slow"        # Skip slow tests

# Run with coverage (if pytest-cov installed)
pytest --cov=sgio --cov-report=html
```

### Documentation
```bash
# Build documentation
cd docs
make html                   # Build HTML docs
make clean                  # Clean build files

# Documentation is in docs/source/ (Markdown with MyST)
# Built docs are in docs/build/html/
```

### Linting and Formatting
```bash
# Note: No explicit linters configured in pyproject.toml
# Follow PEP 8 style guide and use IDE formatting
```

## Test Structure

- **Test Location**: All tests in `tests/` directory
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - Integration tests
- **Test Discovery**: Files matching `test_*.py`, classes `Test*`, functions `test_*`
- **Test Markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
- **Pytest Config**: `tests/pytest.ini`

## Code Style Guidelines

### Imports
```python
# Standard library imports first
from __future__ import annotations
import math
from typing import Optional, List, Literal

# Third-party imports
import pytest
from pydantic import BaseModel, Field, field_validator

# Local application imports
from sgio.model.beam import EulerBernoulliBeamModel
from sgio.model.solid import CauchyContinuumModel
```

### Type Hints
- **Always use type hints** for function signatures
- Use `from __future__ import annotations` for forward references
- Prefer `Optional[Type]` over `Type | None` for consistency with Python 3.9+
- Use `Literal` for restricted value sets
- Example:
  ```python
  def process_data(value: float, isotropy: Literal[0, 1, 2]) -> Optional[List[float]]:
      """Process data with type-safe parameters."""
      pass
  ```

### Docstrings
- **Format**: NumPy style docstrings
- **Required for**: All public functions, classes, and methods
- **Structure**:
  ```python
  def function_name(param1: int, param2: str) -> bool:
      """Brief one-line description.
      
      Longer description if needed, explaining what the function does
      and any important details.
      
      Parameters
      ----------
      param1 : int
          Description of param1
      param2 : str
          Description of param2
          
      Returns
      -------
      bool
          Description of return value
          
      Raises
      ------
      ValueError
          When invalid input is provided
          
      Examples
      --------
      >>> function_name(42, "hello")
      True
      """
  ```

### Naming Conventions
- **Classes**: PascalCase (e.g., `CauchyContinuumModel`, `StructureGene`)
- **Functions/Methods**: snake_case (e.g., `build_sg_1d`, `read_output`)
- **Variables**: snake_case (e.g., `stiffness_matrix`, `young_modulus`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_ITERATIONS`)
- **Private attributes**: Prefix with underscore (e.g., `_internal_state`)

### Pydantic Models
- Use Pydantic v2+ features (`BaseModel`, `Field`, `field_validator`)
- Set `ConfigDict(validate_assignment=True)` for runtime validation
- Use `Field()` with descriptions for all model fields
- Implement custom `__init__` for backward compatibility if needed
- Example:
  ```python
  from pydantic import BaseModel, Field, ConfigDict
  
  class MaterialModel(BaseModel):
      name: str = Field(default='', description="Material name")
      density: float = Field(default=0, ge=0, description="Material density")
      
      model_config = ConfigDict(validate_assignment=True)
  ```

### Error Handling
- **Custom Exceptions**: Defined in `sgio/_exceptions.py`
- Use specific exceptions: `VABSError`, `SwiftCompError`, `OutputFileError`, etc.
- Raise `ValueError` for invalid parameter values
- Raise `TypeError` for incorrect parameter types
- Always include descriptive error messages:
  ```python
  if value < 0:
      raise ValueError(f'Parameter must be >= 0, got {value}')
  ```

### Code Organization
- **Keep methods short**: Aim for < 50 lines per method
- **Extract helper functions**: Use module-level helper functions (prefix with `_`) for complex logic
- **Avoid very long classes**: Break into smaller, focused classes or use composition
- **Example structure**:
  ```python
  # Helper functions (module-level)
  def _build_matrix(params: dict) -> List[List[float]]:
      """Private helper function."""
      pass
  
  # Main class
  class Model(BaseModel):
      """Public model class."""
      pass
  ```

### Testing Guidelines
- **One test file per module**: `test_models.py` for `model/*.py`
- **Use descriptive test names**: `test_initialization_with_aliases`
- **Structure**: Arrange tests in classes by feature area
- **AAA Pattern**: Arrange, Act, Assert
  ```python
  def test_feature(self):
      """Test description."""
      # Arrange
      mat = CauchyContinuumModel(isotropy=0, e=200e9, nu=0.3)
      
      # Act
      result = mat.compute_stiffness()
      
      # Assert
      assert result is not None
      assert len(result) == 6
  ```

## Common Patterns

### Parameter Aliases
Support both canonical and alias names:
```python
@staticmethod
def _resolve_aliases(data: dict) -> dict:
    """Map aliases to canonical names."""
    aliases = {'e': 'e1', 'nu': 'nu12'}
    for alias, canonical in aliases.items():
        if alias in data and canonical not in data:
            data[canonical] = data.pop(alias)
    return data
```

### Property Aliases
Provide convenient property accessors:
```python
@property
def e(self) -> Optional[float]:
    """Alias for e1 (Young's modulus)."""
    return self.e1

@e.setter
def e(self, value: float) -> None:
    self.e1 = float(value)
```

## Git Workflow
- Create feature branches from main
- Write tests before implementing features
- Ensure all tests pass before committing
- Use descriptive commit messages

## Additional Resources
- Documentation: https://wenbinyugroup.github.io/sgio/
- GitHub: https://github.com/wenbinyugroup/sgio
- Issues: Report bugs and feature requests on GitHub
