# Makefile for SGIO project

.PHONY: help install dev-install test clean build-exe build-wheel upload-test upload docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install the package"
	@echo "  dev-install  - Install in development mode with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  build-exe    - Build standalone executable"
	@echo "  build-wheel  - Build wheel package"
	@echo "  upload-test  - Upload to test PyPI"
	@echo "  upload       - Upload to PyPI"
	@echo "  docs         - Build documentation"

# Installation targets
install:
	pip install .

dev-install:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Build targets
build-exe:
	python build_executable.py

build-exe-clean:
	python build_executable.py --clean

build-wheel:
	python -m build

# Upload targets
upload-test:
	python -m build
	twine upload --repository testpypi dist/*

upload:
	python -m build
	twine upload dist/*

# Documentation
docs:
	cd docs && make html

# Development helpers
format:
	black sgio/
	isort sgio/

lint:
	flake8 sgio/
	pylint sgio/

# Quick development cycle
dev: clean dev-install test

# Full build and test cycle
all: clean dev-install test build-exe build-wheel
