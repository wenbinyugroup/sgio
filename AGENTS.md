# AGENTS.md

## First Principles

Use first-principles thinking. Do not assume that I always clearly understand what I want or how to achieve it. Stay cautious and start from the fundamental needs and problems. If the motivation or goal is unclear, stop and discuss it with me.

## Environment Setup

- **Package Manager**: Use `uv` for dependency management
- **Virtual Environment**: Activate with `.venv/Scripts/activate.ps1` (Windows) or `source .venv/bin/activate` (Unix). In WSL, use `.venv/Scripts/python.exe` to run scripts.
- **Python Version**: Requires Python >= 3.9
- **Install Dependencies**: `uv sync` or `pip install -e .`

ALWAYS USE PROJECT LOCAL VENV

Ignore the following files and directories with the name containing `temp`, `archive`, `legacy`, `old`, `backup`, `~`, or `#`.

## Build and Test Commands

### Testing

Activate virtual environment first or use `uv run` to run pytest.

## Documentation
```bash
# Build documentation
cd docs
make html                   # Build HTML docs
make clean                  # Clean build files

# Documentation is in docs/source/ (Markdown with MyST)
# Built docs are in docs/build/html/
```

### Examples

Document each example in the following structure:
- Problem description
- Explaination of the solution (mainly how to use sgio to tackle this problem)
- Result
- List of all files (download link)

One file for one example.
Use myst markdown.


## Test Structure

- **Test Location**: All tests in `tests/` directory
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - Integration tests
- **Test Discovery**: Files matching `test_*.py`, classes `Test*`, functions `test_*`
- **Test Markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
- **Test Fixtures**: `tests/conftest.py`
- **Pytest Config**: `tests/pytest.ini`

## Code Style Guidelines

- Encourage **modularity** and **reusability** in code design.
- Discourage **monolithic** code design.
- Avoid one giant function/file.
- When creating new functions, classes, modules, etc., start from simplest possible implementation, and gradually add features. **Do not overengineer**.
- Always use numpy style docstrings.
- Use comments to annotate key steps in the code.

- When developing new functions, make use of existing functions as much as possible. Try to avoid reinventing the wheel.

- When proposing modifications or refactoring plans, you must follow these rules:
  - Do not provide compatibility or workaround-based solutions.
  - Avoid over-engineering; follow the shortest path to implementation while still adhering to the first-principles requirement.
  - Do not introduce solutions beyond the requirements I provided (e.g., fallback or downgrade strategies), as they may cause deviations in business logic.
  - Ensure the logical correctness of the solution; it must be validated through end-to-end reasoning.


### Type Hints
- **Always use type hints** for function signatures
- Use `from __future__ import annotations` for forward references


### Docstrings
- **Format**: NumPy style docstrings
- **Required for**: All public functions, classes, and methods


### Naming Conventions
- **Classes**: PascalCase (e.g., `CauchyContinuumModel`, `StructureGene`)
- **Functions/Methods**: snake_case (e.g., `build_sg_1d`, `read_output`)
- **Variables**: snake_case (e.g., `stiffness_matrix`, `young_modulus`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_ITERATIONS`)
- **Private attributes**: Prefix with underscore (e.g., `_internal_state`)


### Error Handling
- **Custom Exceptions**: Defined in `sgio/_exceptions.py`
- Use specific exceptions: `VABSError`, `SwiftCompError`, `OutputFileError`, etc.
- Raise `ValueError` for invalid parameter values
- Raise `TypeError` for incorrect parameter types
- Always include descriptive error messages


### Code Organization
- **Keep methods short**: Aim for < 50 lines per method
- **Avoid very long classes**: Break into smaller, focused classes or use composition


### Testing Guidelines
- **One test file per module**: `test_models.py` for `model/*.py`
- **Use descriptive test names**: `test_initialization_with_aliases`
- **Structure**: Arrange tests in classes by feature area

