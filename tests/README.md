# SGIO Test Suite

This directory contains the test suite for the SGIO (Structure Gene I/O) package.

---

## Quick Start

### Run All Tests
```bash
uv run pytest
```

### Run Specific Test Category
```bash
uv run pytest -m unit          # Unit tests
uv run pytest -m io            # I/O tests
uv run pytest -m conversion    # Conversion tests
```

### Run Tests in Specific Directory
```bash
uv run pytest tests/unit/
uv run pytest tests/file_io/vabs/
```

---

## Directory Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration
├── unit/                    # Unit tests for individual components
│   └── test_models.py      # ✅ Structural model tests (17 tests)
├── file_io/                 # I/O functionality tests (renamed from 'io')
│   ├── vabs/               # VABS I/O tests
│   │   └── test_vabs_output_state.py  # ✅ VABS output state tests (2 tests)
│   ├── swiftcomp/          # SwiftComp I/O tests
│   ├── abaqus/             # Abaqus I/O tests
│   └── gmsh/               # Gmsh I/O tests
├── conversion/              # Format conversion tests
│   └── test_format_conversions.py  # ✅ Format conversion tests (7 tests)
├── integration/             # Integration tests
├── cli/                     # CLI tests
│   └── test_cli_convert.py # ✅ CLI conversion tests (5 tests)
├── visualization/           # Visualization tests
├── performance/             # Performance benchmarks
├── validation/              # Input validation and error handling
├── ext/                     # External vendor tests
├── fixtures/                # Test input data (version controlled)
├── expected/                # Expected outputs for validation
├── files/                   # Legacy test data (during migration)
└── _temp/                   # Temporary outputs (gitignored)
```

---

## Test Categories

### Unit Tests (`unit/`)
Tests for individual components:
- Model classes (beam, plate, solid)
- Material property handling
- Mesh data structures
- Coordinate transformations

### I/O Tests (`file_io/`)
Tests for reading and writing files:
- **VABS**: Input/output for VABS format (✅ 2 tests migrated)
- **SwiftComp**: Input/output for SwiftComp format
- **Abaqus**: Input/output for Abaqus .inp files
- **Gmsh**: Input/output for Gmsh mesh formats

### Conversion Tests (`conversion/`)
Tests for format conversion:
- VABS ↔ SwiftComp ↔ Abaqus ↔ Gmsh
- Mesh-only conversions
- Element and node renumbering

### Integration Tests (`integration/`)
Tests for complete workflows:
- Solver execution (VABS, SwiftComp)
- End-to-end analysis pipelines

### CLI Tests (`cli/`)
Tests for command-line interface

### Visualization Tests (`visualization/`)
Tests for plotting and visualization

### Performance Tests (`performance/`)
Benchmark tests for:
- Large mesh handling (10,000+ elements)
- Conversion speed
- Memory efficiency

### Validation Tests (`validation/`)
Tests for:
- Input validation
- Error handling
- Malformed input files

---

## Test Markers

Use markers to run specific test subsets:

```bash
# Run only fast tests
uv run pytest -m "not slow"

# Run only VABS tests
uv run pytest -m vabs

# Run tests that don't require external solvers
uv run pytest -m "not requires_solver"
```

Available markers:
- `unit`, `integration`, `io`, `conversion`, `cli`, `visualization`, `performance`
- `slow`, `requires_solver`, `requires_display`
- `vabs`, `swiftcomp`, `abaqus`, `gmsh`
- `legacy` (tests being migrated)

---

## Fixtures

Common fixtures are defined in `conftest.py`:

### Directory Fixtures
- `test_data_dir`: Root directory for test input files
- `expected_data_dir`: Root directory for expected outputs
- `temp_dir`: Temporary directory for test outputs

### Format-Specific Fixtures
- `vabs_test_files`: VABS test file paths
- `sc_test_files`: SwiftComp test file paths
- `abaqus_test_files`: Abaqus test file paths
- `gmsh_test_files`: Gmsh test file paths

### Sample Data Fixtures
- `sample_materials`: Sample material definitions

---

## Writing Tests

### Example Test
```python
import pytest
from sgio import read, write


@pytest.mark.io
@pytest.mark.vabs
def test_vabs_read(vabs_test_files, temp_dir):
    """Test reading VABS input file."""
    # Arrange
    input_file = vabs_test_files['v41'] / "example.sg"
    
    # Act
    sg = read(str(input_file), 'vabs')
    
    # Assert
    assert sg is not None
    assert sg.mesh is not None
    assert len(sg.mesh.points) > 0
```

---

## Documentation

- **Test Plan**: `notes/dev/ai-agents/memory/sgio/dev-notes/tests_plan.md`
- **Migration Guide**: `notes/dev/ai-agents/memory/sgio/dev-notes/migration_guide.md`
- **Quick Reference**: `notes/dev/ai-agents/memory/sgio/dev-notes/test_quick_reference.md`

---

## Status

**Current Phase**: Phase 2 Complete ✅
**Next Phase**: Phase 3 - Fill Coverage Gaps

### Migration Progress
- ✅ **Phase 1**: Foundation Setup (Complete)
- ✅ **Phase 2**: Core Test Migration (Complete - 49 tests passing, 11 skipped, 1 failed)
  - 10 files migrated to new structure
  - 61 total tests in organized structure
  - All legacy test files archived in `_archive/`
  - Test suite reorganized by functionality
- ⏳ **Phase 3**: Fill Coverage Gaps (Pending)
  - Need to add missing unit tests for materials, transformations
  - Need to add validation and error handling tests
  - Need to migrate test data from `files/` to `fixtures/`

### Test Summary (as of 2026-01-21)
- **Total Tests**: 61
- **Passing**: 49 (80%)
- **Skipped**: 11 (18%) - mostly due to missing test data in fixtures
- **Failed**: 1 (2%) - due to missing test data file

### Files Migrated
1. `test_beam_pydantic.py` → `unit/test_models.py`
2. `test_cli_convert.py` → `cli/test_cli_convert.py`
3. `test_convert.py` + `test_convert_to_vabs.py` → `conversion/test_format_conversions.py`
4. `test_gmsh_read.py` → `file_io/gmsh/test_gmsh_io.py`
5. `test_io_vabs_in.py` → `file_io/vabs/test_vabs_input.py`
6. `test_io_vabs_out_state_d.py` + `test_io_vabs_out_state_f.py` → `file_io/vabs/test_vabs_output_state.py`
7. `test_io_sc_out_state_d.py` + `test_read_output_node_strain_stress.py` → `file_io/swiftcomp/test_sc_output_state.py`

See `tests_plan.md` for detailed roadmap.

