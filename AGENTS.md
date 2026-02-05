# AGENTS.md

## Dev Environment Setup

- Use `uv` to manage the project.
- Run `.venv/Scripts/activate.ps1` from the root of the project to activate the virtual environment.

## Testing Instructions

- Always create test modules and functions in folder `sgio/tests`.
- Use `pytest` to manage testing.

## Documentation Instructions

- Use `sphinx` to manage documentation.
- Use `myst` to write documentation in Markdown.
- Use `make html` to build documentation.
- The documentation source files are in `docs/source`.
- The documentation build files are in `docs/build`.
- Use numpy docstring format for all docstrings.
