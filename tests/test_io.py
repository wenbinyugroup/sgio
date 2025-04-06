"""
tests/
├── files/
│   ├── success/
│   │   ├── minimal/
│   │   │   ├── minimal_2d.sg
│   │   │   ├── minimal_3d.sg
│   │   │   └── minimal_reference.yaml
│   │   ├── complete/
│   │   │   ├── complete_case.sg
│   │   │   └── complete_reference.yaml
│   │   └── complex/
│   │       ├── multiple_materials.sg
│   │       ├── multiple_coords.sg
│   │       └── large_mesh.sg
│   └── failure/
│       ├── invalid/
│       │   ├── missing_nodes.sg
│       │   ├── invalid_connectivity.sg
│       │   └── duplicate_ids.sg
│       ├── corrupted/
│       │   ├── corrupted_header.sg
│       │   └── corrupted_data.sg
│       └── edge_cases/
│           ├── empty.sg
│           └── whitespace_only.sg
└── test_io.py


Key points about test case preparation:
- Start Small: Begin with the minimal success case and basic failure cases
- Incremental Development: Add more complex cases as you implement more features
- Documentation: Each test case should have a clear purpose and expected behavior
- Maintainability: Keep test files small and focused
- Reference Data: Include reference files (like YAML) for easy verification
- Error Messages: Ensure error messages are clear and helpful
- Coverage: Aim to cover all code paths and error conditions
"""

import pytest
from pathlib import Path
from sgio import read_sg, write_sg, SGError

class TestSGIO:
    # Success cases
    def test_minimal_2d(self):
        sg = read_sg("tests/files/success/minimal/minimal_2d.sg")
        assert len(sg.nodes) == 3
        assert len(sg.elements) == 1
        assert len(sg.materials) == 1

    def test_complete_case(self):
        sg = read_sg("tests/files/success/complete/complete_case.sg")
        # Verify all required fields
        assert hasattr(sg, 'nodes')
        assert hasattr(sg, 'elements')
        assert hasattr(sg, 'materials')
        assert hasattr(sg, 'coordinate_systems')

    def test_multiple_materials(self):
        sg = read_sg("tests/files/success/complex/multiple_materials.sg")
        assert len(sg.materials) > 1
        # Verify material assignments
        for element in sg.elements:
            assert element.material_id in range(len(sg.materials))

    # Failure cases
    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            read_sg("nonexistent_file.sg")

    def test_missing_nodes(self):
        with pytest.raises(SGError, match="Missing required nodes"):
            read_sg("tests/files/failure/invalid/missing_nodes.sg")

    def test_invalid_connectivity(self):
        with pytest.raises(SGError, match="Invalid element connectivity"):
            read_sg("tests/files/failure/invalid/invalid_connectivity.sg")

    def test_corrupted_file(self):
        with pytest.raises(SGError, match="Corrupted file header"):
            read_sg("tests/files/failure/corrupted/corrupted_header.sg")

    # Edge cases
    def test_empty_file(self):
        with pytest.raises(SGError, match="Empty file"):
            read_sg("tests/files/failure/edge_cases/empty.sg")

    def test_whitespace_only(self):
        with pytest.raises(SGError, match="No valid data found"):
            read_sg("tests/files/failure/edge_cases/whitespace_only.sg")

