"""Unit tests for custom exceptions.

This module tests the exception hierarchy, error messages, and attributes
of all custom exceptions in the SGIO library.
"""

from __future__ import annotations
import pytest
from sgio._exceptions import (
    SGIOError,
    SwiftCompError,
    SwiftCompLicenseError,
    SwiftCompIOError,
    VABSError,
    VABSLicenseError,
    VABSIOError,
    OutputFileError,
)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""
    
    def test_sgio_error_inherits_from_exception(self):
        """SGIOError should inherit from built-in Exception."""
        assert issubclass(SGIOError, Exception)
    
    def test_swiftcomp_error_inherits_from_sgio_error(self):
        """SwiftCompError should inherit from SGIOError."""
        assert issubclass(SwiftCompError, SGIOError)
        assert issubclass(SwiftCompError, Exception)
    
    def test_swiftcomp_license_error_inherits_from_swiftcomp_error(self):
        """SwiftCompLicenseError should inherit from SwiftCompError."""
        assert issubclass(SwiftCompLicenseError, SwiftCompError)
        assert issubclass(SwiftCompLicenseError, SGIOError)
        assert issubclass(SwiftCompLicenseError, Exception)
    
    def test_swiftcomp_io_error_inherits_from_swiftcomp_error(self):
        """SwiftCompIOError should inherit from SwiftCompError."""
        assert issubclass(SwiftCompIOError, SwiftCompError)
        assert issubclass(SwiftCompIOError, SGIOError)
        assert issubclass(SwiftCompIOError, Exception)
    
    def test_vabs_error_inherits_from_sgio_error(self):
        """VABSError should inherit from SGIOError."""
        assert issubclass(VABSError, SGIOError)
        assert issubclass(VABSError, Exception)
    
    def test_vabs_license_error_inherits_from_vabs_error(self):
        """VABSLicenseError should inherit from VABSError."""
        assert issubclass(VABSLicenseError, VABSError)
        assert issubclass(VABSLicenseError, SGIOError)
        assert issubclass(VABSLicenseError, Exception)
    
    def test_vabs_io_error_inherits_from_vabs_error(self):
        """VABSIOError should inherit from VABSError."""
        assert issubclass(VABSIOError, VABSError)
        assert issubclass(VABSIOError, SGIOError)
        assert issubclass(VABSIOError, Exception)
    
    def test_output_file_error_inherits_from_sgio_error(self):
        """OutputFileError should inherit from SGIOError."""
        assert issubclass(OutputFileError, SGIOError)
        assert issubclass(OutputFileError, Exception)


class TestSGIOError:
    """Test base SGIOError exception."""
    
    def test_can_be_raised(self):
        """SGIOError can be raised and caught."""
        with pytest.raises(SGIOError):
            raise SGIOError("Test error")
    
    def test_error_message(self):
        """SGIOError should preserve error message."""
        with pytest.raises(SGIOError) as exc_info:
            raise SGIOError("Custom error message")
        assert str(exc_info.value) == "Custom error message"
    
    def test_catch_all_sgio_exceptions(self):
        """SGIOError should catch all SGIO-related exceptions."""
        with pytest.raises(SGIOError):
            raise SwiftCompError("Test")
        
        with pytest.raises(SGIOError):
            raise VABSError("Test")
        
        with pytest.raises(SGIOError):
            raise OutputFileError("Test")


class TestSwiftCompError:
    """Test SwiftCompError with return codes."""
    
    def test_default_message(self):
        """SwiftCompError should have default message."""
        error = SwiftCompError()
        assert "SwiftComp execution failed" in str(error)
    
    def test_custom_message(self):
        """SwiftCompError should accept custom message."""
        error = SwiftCompError("Custom error")
        assert "Custom error" in str(error)
    
    def test_error_with_return_code(self):
        """SwiftCompError should include return code in message."""
        error = SwiftCompError("Test error", return_code=1)
        assert "Test error" in str(error)
        assert "exit code: 1" in str(error)
        assert error.return_code == 1
    
    def test_error_without_return_code(self):
        """SwiftCompError should work without return code."""
        error = SwiftCompError("Test error")
        assert error.return_code is None
        assert "Test error" in str(error)
        assert "exit code" not in str(error)
    
    def test_can_be_raised_and_caught(self):
        """SwiftCompError can be raised and caught."""
        with pytest.raises(SwiftCompError) as exc_info:
            raise SwiftCompError("Test", return_code=42)
        assert exc_info.value.return_code == 42


class TestSwiftCompLicenseError:
    """Test SwiftCompLicenseError."""
    
    def test_default_message(self):
        """SwiftCompLicenseError should have default message."""
        error = SwiftCompLicenseError()
        assert "license validation failed" in str(error).lower()
    
    def test_custom_message(self):
        """SwiftCompLicenseError should accept custom message."""
        error = SwiftCompLicenseError("License expired")
        assert "License expired" in str(error)
    
    def test_inherits_return_code_support(self):
        """SwiftCompLicenseError should support return codes from parent."""
        error = SwiftCompLicenseError("License error", return_code=5)
        assert error.return_code == 5
        assert "exit code: 5" in str(error)
    
    def test_can_be_caught_as_swiftcomp_error(self):
        """SwiftCompLicenseError can be caught as SwiftCompError."""
        with pytest.raises(SwiftCompError):
            raise SwiftCompLicenseError("Test")


class TestSwiftCompIOError:
    """Test SwiftCompIOError."""
    
    def test_default_message(self):
        """SwiftCompIOError should have default message."""
        error = SwiftCompIOError()
        assert "I/O operation failed" in str(error)
    
    def test_custom_message(self):
        """SwiftCompIOError should accept custom message."""
        error = SwiftCompIOError("Cannot read file")
        assert "Cannot read file" in str(error)
    
    def test_inherits_return_code_support(self):
        """SwiftCompIOError should support return codes from parent."""
        error = SwiftCompIOError("I/O error", return_code=3)
        assert error.return_code == 3
        assert "exit code: 3" in str(error)
    
    def test_can_be_caught_as_swiftcomp_error(self):
        """SwiftCompIOError can be caught as SwiftCompError."""
        with pytest.raises(SwiftCompError):
            raise SwiftCompIOError("Test")


class TestVABSError:
    """Test VABSError with return codes."""
    
    def test_default_message(self):
        """VABSError should have default message."""
        error = VABSError()
        assert "VABS execution failed" in str(error)
    
    def test_custom_message(self):
        """VABSError should accept custom message."""
        error = VABSError("Custom VABS error")
        assert "Custom VABS error" in str(error)
    
    def test_error_with_return_code(self):
        """VABSError should include return code in message."""
        error = VABSError("VABS failed", return_code=2)
        assert "VABS failed" in str(error)
        assert "exit code: 2" in str(error)
        assert error.return_code == 2
    
    def test_error_without_return_code(self):
        """VABSError should work without return code."""
        error = VABSError("VABS failed")
        assert error.return_code is None
        assert "VABS failed" in str(error)
        assert "exit code" not in str(error)
    
    def test_can_be_raised_and_caught(self):
        """VABSError can be raised and caught."""
        with pytest.raises(VABSError) as exc_info:
            raise VABSError("Test", return_code=99)
        assert exc_info.value.return_code == 99


class TestVABSLicenseError:
    """Test VABSLicenseError."""
    
    def test_default_message(self):
        """VABSLicenseError should have default message."""
        error = VABSLicenseError()
        assert "license validation failed" in str(error).lower()
    
    def test_custom_message(self):
        """VABSLicenseError should accept custom message."""
        error = VABSLicenseError("License not found")
        assert "License not found" in str(error)
    
    def test_inherits_return_code_support(self):
        """VABSLicenseError should support return codes from parent."""
        error = VABSLicenseError("License error", return_code=7)
        assert error.return_code == 7
        assert "exit code: 7" in str(error)
    
    def test_can_be_caught_as_vabs_error(self):
        """VABSLicenseError can be caught as VABSError."""
        with pytest.raises(VABSError):
            raise VABSLicenseError("Test")


class TestVABSIOError:
    """Test VABSIOError."""
    
    def test_default_message(self):
        """VABSIOError should have default message."""
        error = VABSIOError()
        assert "I/O operation failed" in str(error)
    
    def test_custom_message(self):
        """VABSIOError should accept custom message."""
        error = VABSIOError("Cannot write output")
        assert "Cannot write output" in str(error)
    
    def test_inherits_return_code_support(self):
        """VABSIOError should support return codes from parent."""
        error = VABSIOError("I/O error", return_code=4)
        assert error.return_code == 4
        assert "exit code: 4" in str(error)
    
    def test_can_be_caught_as_vabs_error(self):
        """VABSIOError can be caught as VABSError."""
        with pytest.raises(VABSError):
            raise VABSIOError("Test")


class TestOutputFileError:
    """Test OutputFileError with file paths."""
    
    def test_default_message(self):
        """OutputFileError should have default message."""
        error = OutputFileError()
        assert "Output file operation failed" in str(error)
    
    def test_custom_message(self):
        """OutputFileError should accept custom message."""
        error = OutputFileError("Invalid format")
        assert "Invalid format" in str(error)
    
    def test_error_with_file_path(self):
        """OutputFileError should include file path in message."""
        error = OutputFileError("Parse error", file_path="output.dat")
        assert "Parse error" in str(error)
        assert "file: output.dat" in str(error)
        assert error.file_path == "output.dat"
    
    def test_error_without_file_path(self):
        """OutputFileError should work without file path."""
        error = OutputFileError("Parse error")
        assert error.file_path is None
        assert "Parse error" in str(error)
        assert "file:" not in str(error)
    
    def test_can_be_raised_and_caught(self):
        """OutputFileError can be raised and caught."""
        with pytest.raises(OutputFileError) as exc_info:
            raise OutputFileError("Test", file_path="/path/to/file.out")
        assert exc_info.value.file_path == "/path/to/file.out"


class TestExceptionCatching:
    """Test exception catching patterns."""
    
    def test_catch_all_swiftcomp_errors(self):
        """SwiftCompError should catch all SwiftComp-related exceptions."""
        with pytest.raises(SwiftCompError):
            raise SwiftCompLicenseError("Test")
        
        with pytest.raises(SwiftCompError):
            raise SwiftCompIOError("Test")
    
    def test_catch_all_vabs_errors(self):
        """VABSError should catch all VABS-related exceptions."""
        with pytest.raises(VABSError):
            raise VABSLicenseError("Test")
        
        with pytest.raises(VABSError):
            raise VABSIOError("Test")
    
    def test_specific_error_not_caught_by_sibling(self):
        """SwiftComp errors should not catch VABS errors and vice versa."""
        with pytest.raises(VABSError):
            try:
                raise VABSError("Test")
            except SwiftCompError:
                pytest.fail("VABSError should not be caught by SwiftCompError")
        
        with pytest.raises(SwiftCompError):
            try:
                raise SwiftCompError("Test")
            except VABSError:
                pytest.fail("SwiftCompError should not be caught by VABSError")
    
    def test_catch_all_sgio_errors_with_base_class(self):
        """SGIOError should catch all custom exceptions."""
        exceptions_to_test = [
            SwiftCompError("Test"),
            SwiftCompLicenseError("Test"),
            SwiftCompIOError("Test"),
            VABSError("Test"),
            VABSLicenseError("Test"),
            VABSIOError("Test"),
            OutputFileError("Test"),
        ]
        
        for exc in exceptions_to_test:
            with pytest.raises(SGIOError):
                raise exc


class TestExceptionAttributes:
    """Test exception attributes and properties."""
    
    def test_return_code_attribute_accessible(self):
        """Return code should be accessible as attribute."""
        error = SwiftCompError("Test", return_code=123)
        assert hasattr(error, "return_code")
        assert error.return_code == 123
    
    def test_file_path_attribute_accessible(self):
        """File path should be accessible as attribute."""
        error = OutputFileError("Test", file_path="test.out")
        assert hasattr(error, "file_path")
        assert error.file_path == "test.out"
    
    def test_return_code_can_be_zero(self):
        """Return code should work with zero value."""
        error = VABSError("Test", return_code=0)
        assert error.return_code == 0
        assert "exit code: 0" in str(error)
    
    def test_attributes_preserved_when_caught(self):
        """Attributes should be preserved when exception is caught."""
        try:
            raise SwiftCompError("Test", return_code=42)
        except SwiftCompError as e:
            assert e.return_code == 42
        
        try:
            raise OutputFileError("Test", file_path="data.out")
        except OutputFileError as e:
            assert e.file_path == "data.out"
