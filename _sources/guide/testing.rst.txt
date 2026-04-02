Testing with SGIO
==================

This guide shows how to write tests for code that uses SGIO, based on patterns
from the SGIO test suite.

Overview
--------

The SGIO test suite uses:

- **pytest** for test framework
- **fixtures** for reusable test data
- **markers** for test categorization
- **parametrization** for testing multiple cases

Basic Test Structure
--------------------

Simple Test Example
^^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    import sgio
    from pathlib import Path
    
    def test_read_vabs_file():
        """Test reading a VABS input file."""
        # Arrange
        input_file = Path('test_data/cross_section.sg')
        
        # Act
        sg = sgio.read(str(input_file), 'vabs', model_type='BM2')
        
        # Assert
        assert sg is not None
        assert sg.mesh is not None
        assert len(sg.mesh.points) > 0
        assert len(sg.mesh.cells) > 0

Using Fixtures
--------------

Fixtures provide reusable test data and setup.

Directory Fixtures
^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    from pathlib import Path
    
    @pytest.fixture
    def test_data_dir():
        """Root directory for test data."""
        return Path(__file__).parent / 'test_data'
    
    @pytest.fixture
    def temp_dir(tmp_path):
        """Temporary directory for test outputs."""
        return tmp_path
    
    def test_with_fixtures(test_data_dir, temp_dir):
        """Test using fixtures."""
        input_file = test_data_dir / 'input.sg'
        output_file = temp_dir / 'output.sg'
        
        sg = sgio.read(str(input_file), 'vabs')
        sgio.write(sg, str(output_file), 'vabs')
        
        assert output_file.exists()

Sample Data Fixtures
^^^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    
    @pytest.fixture
    def sample_beam_properties():
        """Sample beam properties for testing."""
        return {
            'ea': 1.5e8,    # Axial stiffness
            'gj': 5.0e6,    # Torsional stiffness
            'ei22': 3.0e6,  # Bending stiffness
            'ei33': 8.0e6,  # Bending stiffness
        }
    
    def test_beam_model(sample_beam_properties):
        """Test beam model creation."""
        from sgio.model.beam import EulerBernoulliBeamModel
        
        beam = EulerBernoulliBeamModel(**sample_beam_properties)
        
        assert beam.ea == sample_beam_properties['ea']
        assert beam.gj == sample_beam_properties['gj']

Parametrized Tests
------------------

Test multiple cases with one test function.

Basic Parametrization
^^^^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    import sgio
    
    @pytest.mark.parametrize("model_type,expected_label", [
        ('BM1', 'bm1'),
        ('BM2', 'bm2'),
        ('PL1', 'pl1'),
        ('PL2', 'pl2'),
        ('SD1', 'sd1'),
    ])
    def test_model_labels(model_type, expected_label):
        """Test that model types have correct labels."""
        # This is a simplified example
        assert model_type.lower() == expected_label

File Conversion Tests
^^^^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    import sgio
    
    @pytest.mark.parametrize("input_format,output_format", [
        ('vabs', 'gmsh'),
        ('abaqus', 'vabs'),
        ('vabs', 'swiftcomp'),
    ])
    def test_format_conversion(input_format, output_format, test_data_dir, temp_dir):
        """Test conversion between formats."""
        input_file = test_data_dir / f'sample.{input_format}'
        output_file = temp_dir / f'output.{output_format}'
        
        if not input_file.exists():
            pytest.skip(f"Input file not found: {input_file}")
        
        sgio.convert(
            str(input_file),
            str(output_file),
            input_format,
            output_format,
            model_type='BM2'
        )
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0

Test Markers
------------

Use markers to categorize and selectively run tests.

Defining Markers
^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    
    @pytest.mark.unit
    def test_model_creation():
        """Unit test for model creation."""
        from sgio.model.beam import EulerBernoulliBeamModel
        beam = EulerBernoulliBeamModel()
        assert beam is not None
    
    @pytest.mark.io
    @pytest.mark.vabs
    def test_vabs_read():
        """I/O test for VABS reading."""
        # Test code here
        pass
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_full_workflow():
        """Integration test (slow)."""
        # Test code here
        pass

Running Specific Tests
^^^^^^^^^^^^^^^^^^^^^^

..  code-block:: bash

    # Run all tests
    pytest
    
    # Run only unit tests
    pytest -m unit
    
    # Run only VABS tests
    pytest -m vabs
    
    # Run fast tests (exclude slow)
    pytest -m "not slow"
    
    # Run specific test file
    pytest tests/test_conversion.py
    
    # Run specific test function
    pytest tests/test_conversion.py::test_vabs_to_gmsh

Error Handling Tests
--------------------

Test that your code handles errors appropriately.

Testing Exceptions
^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    import sgio
    from sgio import SwiftCompError

    def test_invalid_file_raises_error():
        """Test that reading invalid file raises error."""
        with pytest.raises(FileNotFoundError):
            sgio.read('nonexistent.sg', 'vabs')

    def test_invalid_format_raises_error():
        """Test that invalid format raises error."""
        with pytest.raises(ValueError):
            sgio.read('file.sg', 'invalid_format')

Testing File Existence
^^^^^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    from pathlib import Path

    def test_file_exists_before_reading(test_data_dir):
        """Test file existence check."""
        input_file = test_data_dir / 'cross_section.sg'

        if not input_file.exists():
            pytest.skip(f"Test file not found: {input_file}")

        # Proceed with test
        sg = sgio.read(str(input_file), 'vabs')
        assert sg is not None

Output Validation Tests
-----------------------

Validate that outputs match expected results.

Comparing Numerical Values
^^^^^^^^^^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    import sgio

    def test_beam_properties_accuracy(test_data_dir):
        """Test that beam properties match expected values."""
        output_file = test_data_dir / 'beam_output.sg.K'

        model = sgio.readOutputModel(str(output_file), 'vabs', model_type='BM2')

        # Use pytest.approx for floating point comparison
        assert model.ea == pytest.approx(1.5e8, rel=1e-6)
        assert model.gj == pytest.approx(5.0e6, rel=1e-6)

Comparing Files
^^^^^^^^^^^^^^^

..  code-block:: python

    import pytest
    import sgio
    from pathlib import Path

    def test_conversion_output_matches_expected(test_data_dir, temp_dir):
        """Test that conversion output matches expected file."""
        input_file = test_data_dir / 'input.sg'
        output_file = temp_dir / 'output.msh'
        expected_file = test_data_dir / 'expected_output.msh'

        # Convert
        sgio.convert(str(input_file), str(output_file), 'vabs', 'gmsh')

        # Compare file sizes (simple check)
        assert output_file.stat().st_size > 0

        # For exact comparison, read and compare content
        # (implementation depends on file format)

Best Practices
--------------

1. **Use descriptive test names**: ``test_vabs_read_with_materials()`` not ``test1()``
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **One assertion per test**: Focus on testing one thing
4. **Use fixtures for setup**: Avoid code duplication
5. **Skip unavailable tests**: Use ``pytest.skip()`` for missing data
6. **Test edge cases**: Empty files, invalid data, etc.
7. **Use markers**: Categorize tests for selective running
8. **Clean up after tests**: Use ``tmp_path`` for temporary files

Example Test Module
-------------------

Complete example of a well-structured test module:

..  code-block:: python

    """Test module for VABS I/O operations."""
    import pytest
    from pathlib import Path
    import sgio


    @pytest.fixture
    def vabs_test_files(test_data_dir):
        """VABS test file paths."""
        return {
            'v40': test_data_dir / 'vabs' / 'version_4_0',
            'v41': test_data_dir / 'vabs' / 'version_4_1',
        }


    @pytest.mark.io
    @pytest.mark.vabs
    class TestVABSInput:
        """Tests for VABS input file reading."""

        def test_read_vabs_40(self, vabs_test_files):
            """Test reading VABS 4.0 format."""
            input_file = vabs_test_files['v40'] / 'sample.sg'

            if not input_file.exists():
                pytest.skip(f"Test file not found: {input_file}")

            sg = sgio.read(str(input_file), 'vabs', format_version='4.0')

            assert sg is not None
            assert len(sg.mesh.points) > 0

        def test_read_vabs_41(self, vabs_test_files):
            """Test reading VABS 4.1 format."""
            input_file = vabs_test_files['v41'] / 'sample.sg'

            if not input_file.exists():
                pytest.skip(f"Test file not found: {input_file}")

            sg = sgio.read(str(input_file), 'vabs', format_version='4.1')

            assert sg is not None
            assert len(sg.mesh.points) > 0


    @pytest.mark.conversion
    @pytest.mark.vabs
    class TestVABSConversion:
        """Tests for VABS format conversion."""

        @pytest.mark.parametrize("output_format", ['gmsh', 'swiftcomp'])
        def test_vabs_to_format(self, vabs_test_files, temp_dir, output_format):
            """Test converting VABS to other formats."""
            input_file = vabs_test_files['v41'] / 'sample.sg'
            output_file = temp_dir / f'output.{output_format}'

            if not input_file.exists():
                pytest.skip(f"Test file not found: {input_file}")

            sgio.convert(
                str(input_file),
                str(output_file),
                'vabs',
                output_format,
                model_type='BM2'
            )

            assert output_file.exists()
            assert output_file.stat().st_size > 0

Running Tests
-------------

Configuration
^^^^^^^^^^^^^

Create ``pytest.ini`` in your project root:

..  code-block:: ini

    [pytest]
    testpaths = tests
    python_files = test_*.py
    python_classes = Test*
    python_functions = test_*
    markers =
        unit: Unit tests
        io: I/O tests
        conversion: Format conversion tests
        integration: Integration tests
        slow: Slow tests
        vabs: VABS-specific tests
        swiftcomp: SwiftComp-specific tests

Command Line Options
^^^^^^^^^^^^^^^^^^^^

..  code-block:: bash

    # Verbose output
    pytest -v

    # Show print statements
    pytest -s

    # Stop on first failure
    pytest -x

    # Run last failed tests
    pytest --lf

    # Show test coverage
    pytest --cov=sgio

    # Generate HTML coverage report
    pytest --cov=sgio --cov-report=html

See Also
--------

- `SGIO Test Suite <../../../tests/README.md>`_ - Complete test suite documentation
- `pytest Documentation <https://docs.pytest.org/>`_ - Official pytest docs
- `Examples <../../../examples/>`_ - Working code examples
- :doc:`io` - I/O operations guide
- :doc:`convert` - Format conversion guide

