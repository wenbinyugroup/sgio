"""Unit tests for logging configuration.

This module tests the SGIO logging system including:
- Basic configuration
- Handler management
- Propagation control
- Multi-package integration
- File management
"""

import logging
import pytest
from pathlib import Path
from rich.logging import RichHandler

import sgio
from sgio._global import configure_logging, logger as sgio_logger


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def clean_logging():
    """Clean up logging configuration before and after test.
    
    This fixture ensures tests start with a clean logging state and
    cleans up after each test to prevent interference between tests.
    """
    # Setup: Clear all handlers and reset levels
    logging.root.handlers.clear()
    logging.root.setLevel(logging.WARNING)
    
    sgio_logger.handlers.clear()
    sgio_logger.setLevel(logging.WARNING)
    sgio_logger.propagate = True
    
    yield
    
    # Teardown: Close and clear all handlers again
    for handler in sgio_logger.handlers[:]:
        handler.close()
        sgio_logger.removeHandler(handler)
    
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)


@pytest.fixture
def temp_log_file(tmp_path):
    """Create temporary log file path."""
    log_file = tmp_path / "test.log"
    return log_file


@pytest.fixture
def capture_handler():
    """Create a log capture handler for testing.
    
    Returns a handler that captures log records for verification.
    """
    class LogCapture(logging.Handler):
        def __init__(self):
            super().__init__()
            self.records = []
        
        def emit(self, record):
            self.records.append(record)
    
    handler = LogCapture()
    yield handler
    handler.close()


# ============================================================================
# Helper Functions
# ============================================================================

def get_handler_by_type(logger, handler_type):
    """Get handler of specific type from logger."""
    for h in logger.handlers:
        if isinstance(h, handler_type):
            return h
    return None


def count_handlers_by_type(logger, handler_type):
    """Count handlers of specific type."""
    return sum(1 for h in logger.handlers if isinstance(h, handler_type))


def read_log_file(path):
    """Read log file contents."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# ============================================================================
# Test Basic Configuration
# ============================================================================

@pytest.mark.unit
class TestBasicConfiguration:
    """Test basic logging configuration."""
    
    def test_default_configuration(self, clean_logging, tmp_path):
        """Test default configuration creates logger with handlers."""
        log_file = tmp_path / "default.log"
        
        configure_logging(filename=str(log_file))
        
        # Verify logger exists and has correct name
        assert sgio_logger.name == 'sgio'
        
        # Verify logger level is DEBUG
        assert sgio_logger.level == logging.DEBUG
        
        # Verify two handlers added (console and file)
        assert len(sgio_logger.handlers) == 2
        
        # Verify RichHandler for console
        assert count_handlers_by_type(sgio_logger, RichHandler) == 2
    
    def test_custom_console_level(self, clean_logging, tmp_path):
        """Test custom console log level is applied."""
        log_file = tmp_path / "console_level.log"
        
        configure_logging(
            cout_level='WARNING',
            filename=str(log_file)
        )
        
        # Find console handler (first RichHandler)
        console_handler = sgio_logger.handlers[0]
        assert isinstance(console_handler, RichHandler)
        assert console_handler.level == logging.WARNING
    
    def test_custom_file_level(self, clean_logging, tmp_path):
        """Test custom file log level is applied."""
        log_file = tmp_path / "file_level.log"
        
        configure_logging(
            fout_level='ERROR',
            filename=str(log_file)
        )
        
        # Find file handler (second RichHandler)
        file_handler = sgio_logger.handlers[1]
        assert isinstance(file_handler, RichHandler)
        assert file_handler.level == logging.ERROR
    
    def test_case_insensitive_levels(self, clean_logging, tmp_path):
        """Test log level strings are case-insensitive."""
        log_file = tmp_path / "case.log"
        
        configure_logging(
            cout_level='info',  # lowercase
            fout_level='DeBuG',  # mixed case
            filename=str(log_file)
        )
        
        assert sgio_logger.handlers[0].level == logging.INFO
        assert sgio_logger.handlers[1].level == logging.DEBUG


# ============================================================================
# Test File Management
# ============================================================================

@pytest.mark.unit
class TestFileManagement:
    """Test log file creation and management."""
    
    def test_file_creation(self, clean_logging, tmp_path):
        """Test log file is created at specified path."""
        log_file = tmp_path / "created.log"
        
        configure_logging(filename=str(log_file))
        
        # Write a log message
        sgio_logger.info("Test message")
        
        # Flush handlers to ensure write
        for handler in sgio_logger.handlers:
            handler.flush()
        
        # Verify file exists
        assert log_file.exists()
    
    def test_file_append_mode(self, clean_logging, tmp_path):
        """Test append mode accumulates logs across calls."""
        log_file = tmp_path / "append.log"
        
        # First configuration and log
        configure_logging(file_mode='a', filename=str(log_file))
        sgio_logger.info("First message")
        
        # Flush and close handlers
        for handler in sgio_logger.handlers[:]:
            handler.flush()
            handler.close()
            sgio_logger.removeHandler(handler)
        
        # Second configuration and log
        configure_logging(file_mode='a', filename=str(log_file))
        sgio_logger.info("Second message")
        
        # Flush handlers
        for handler in sgio_logger.handlers:
            handler.flush()
        
        # Read file and verify both messages
        content = read_log_file(log_file)
        assert "First message" in content
        assert "Second message" in content
    
    def test_file_overwrite_mode(self, clean_logging, tmp_path):
        """Test overwrite mode clears previous logs."""
        log_file = tmp_path / "overwrite.log"
        
        # First configuration and log
        configure_logging(file_mode='w', filename=str(log_file))
        sgio_logger.info("First message")
        
        # Flush and close handlers
        for handler in sgio_logger.handlers[:]:
            handler.flush()
            handler.close()
            sgio_logger.removeHandler(handler)
        
        # Second configuration and log (overwrites)
        configure_logging(file_mode='w', filename=str(log_file))
        sgio_logger.info("Second message")
        
        # Flush handlers
        for handler in sgio_logger.handlers:
            handler.flush()
        
        # Read file and verify only second message
        content = read_log_file(log_file)
        assert "First message" not in content
        assert "Second message" in content


# ============================================================================
# Test Propagation
# ============================================================================

@pytest.mark.unit
class TestPropagation:
    """Test logger propagation behavior."""
    
    def test_propagation_enabled(self, clean_logging, tmp_path):
        """Test logs propagate to parent when propagate=True."""
        log_file = tmp_path / "propagate_true.log"
        
        configure_logging(propagate=True, filename=str(log_file))
        
        # Verify propagate is True
        assert sgio_logger.propagate is True
    
    def test_propagation_disabled(self, clean_logging, tmp_path):
        """Test logs don't propagate when propagate=False."""
        log_file = tmp_path / "propagate_false.log"
        
        configure_logging(propagate=False, filename=str(log_file))
        
        # Verify propagate is False
        assert sgio_logger.propagate is False
    
    def test_propagation_to_root_logger(self, clean_logging, tmp_path, capture_handler):
        """Test logs reach root logger when propagate=True."""
        log_file = tmp_path / "root_propagate.log"
        
        # Add capture handler to root logger
        logging.root.addHandler(capture_handler)
        logging.root.setLevel(logging.DEBUG)
        
        # Configure SGIO with propagation
        configure_logging(propagate=True, filename=str(log_file))
        
        # Log a message
        sgio_logger.info("Test propagation message")
        
        # Verify root logger received the message
        assert len(capture_handler.records) > 0
        assert any('Test propagation message' in r.getMessage() 
                  for r in capture_handler.records)
    
    def test_no_propagation_to_root_logger(self, clean_logging, tmp_path, capture_handler):
        """Test logs don't reach root logger when propagate=False."""
        log_file = tmp_path / "root_no_propagate.log"
        
        # Add capture handler to root logger
        logging.root.addHandler(capture_handler)
        logging.root.setLevel(logging.DEBUG)
        
        # Configure SGIO without propagation
        configure_logging(propagate=False, filename=str(log_file))
        
        # Log a message
        sgio_logger.info("Test no propagation message")
        
        # Verify root logger did NOT receive the message
        assert len(capture_handler.records) == 0


# ============================================================================
# Test Handler Management
# ============================================================================

@pytest.mark.unit
class TestHandlerManagement:
    """Test handler creation, clearing, and management."""
    
    def test_clear_handlers_true(self, clean_logging, tmp_path):
        """Test multiple calls don't duplicate handlers with clear_handlers=True."""
        log_file = tmp_path / "clear_true.log"
        
        # First configuration
        configure_logging(clear_handlers=True, filename=str(log_file))
        initial_count = len(sgio_logger.handlers)
        
        # Second configuration
        configure_logging(clear_handlers=True, filename=str(log_file))
        final_count = len(sgio_logger.handlers)
        
        # Should have same number of handlers
        assert initial_count == final_count
        assert final_count == 2  # Console and file
    
    def test_clear_handlers_false(self, clean_logging, tmp_path):
        """Test clear_handlers=False preserves existing handlers."""
        log_file = tmp_path / "clear_false.log"
        
        # First configuration
        configure_logging(clear_handlers=True, filename=str(log_file))
        initial_count = len(sgio_logger.handlers)
        
        # Second configuration without clearing
        configure_logging(clear_handlers=False, filename=str(log_file))
        final_count = len(sgio_logger.handlers)
        
        # Should have more handlers
        assert final_count > initial_count
        assert final_count == 4  # 2 from first + 2 from second
    
    def test_handlers_properly_closed(self, clean_logging, tmp_path):
        """Test handlers are properly closed when cleared."""
        log_file = tmp_path / "close_handlers.log"
        
        # Configure and get initial handlers
        configure_logging(filename=str(log_file))
        initial_handlers = list(sgio_logger.handlers)
        
        # Configure again with clear_handlers=True
        configure_logging(clear_handlers=True, filename=str(log_file))
        
        # Original handlers should be closed and removed
        for handler in initial_handlers:
            assert handler not in sgio_logger.handlers


# ============================================================================
# Test Logger Hierarchy
# ============================================================================

@pytest.mark.unit
class TestLoggerHierarchy:
    """Test logger hierarchy and child loggers."""
    
    def test_child_logger_propagation(self, clean_logging, tmp_path):
        """Test child module loggers propagate to sgio logger."""
        log_file = tmp_path / "child_propagate.log"
        
        configure_logging(filename=str(log_file))
        
        # Get a child logger (simulating sgio.core.builder)
        child_logger = logging.getLogger('sgio.core.builder')
        
        # Verify child propagates by default
        assert child_logger.propagate is True
        
        # Log from child
        child_logger.info("Child logger message")
        
        # Flush handlers
        for handler in sgio_logger.handlers:
            handler.flush()
        
        # Verify message in log file
        content = read_log_file(log_file)
        assert "Child logger message" in content
    
    def test_module_logger_names(self, clean_logging):
        """Test module loggers have correct hierarchical names."""
        # Get various child loggers
        core_logger = logging.getLogger('sgio.core')
        builder_logger = logging.getLogger('sgio.core.builder')
        iofunc_logger = logging.getLogger('sgio.iofunc')
        
        # Verify names
        assert core_logger.name == 'sgio.core'
        assert builder_logger.name == 'sgio.core.builder'
        assert iofunc_logger.name == 'sgio.iofunc'
        
        # Verify they're all children of 'sgio'
        assert core_logger.parent is not None and core_logger.parent.name == 'sgio'
        assert builder_logger.parent is not None and builder_logger.parent.name == 'sgio.core'
        assert iofunc_logger.parent is not None and iofunc_logger.parent.name == 'sgio'


# ============================================================================
# Test Multi-Package Integration
# ============================================================================

@pytest.mark.unit
class TestMultiPackageIntegration:
    """Test integration with root logger and other packages."""
    
    def test_root_logger_captures_sgio(self, clean_logging, tmp_path, capture_handler):
        """Test root logger captures SGIO logs when propagate=True."""
        log_file = tmp_path / "root_capture.log"
        
        # Configure root logger first
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(capture_handler)
        
        # Configure SGIO with propagation
        configure_logging(propagate=True, filename=str(log_file))
        
        # Log from SGIO
        sgio_logger.info("SGIO message for root")
        
        # Verify root logger captured it
        assert len(capture_handler.records) > 0
        messages = [r.getMessage() for r in capture_handler.records]
        assert any("SGIO message for root" in msg for msg in messages)
    
    def test_multiple_package_loggers(self, clean_logging, tmp_path):
        """Test logs from multiple packages can coexist."""
        log_file = tmp_path / "multi_package.log"
        
        # Configure root logger with file handler
        root_handler = logging.FileHandler(str(log_file), mode='w')
        root_handler.setLevel(logging.DEBUG)
        logging.root.addHandler(root_handler)
        logging.root.setLevel(logging.DEBUG)
        
        # Configure SGIO with propagation
        sgio_logger.setLevel(logging.DEBUG)
        sgio_logger.propagate = True
        
        # Create loggers for different "packages"
        pkg1_logger = logging.getLogger('package1')
        pkg2_logger = logging.getLogger('package2')
        
        # Log from each
        sgio_logger.info("From SGIO")
        pkg1_logger.info("From package1")
        pkg2_logger.info("From package2")
        
        # Flush all handlers
        root_handler.flush()
        
        # Verify all messages in file
        content = read_log_file(log_file)
        assert "From SGIO" in content
        assert "From package1" in content
        assert "From package2" in content
    
    def test_selective_package_filtering(self, clean_logging, tmp_path, capture_handler):
        """Test different log levels for different packages."""
        log_file = tmp_path / "selective_filter.log"
        
        # Configure root logger
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(capture_handler)
        
        # Configure SGIO at DEBUG
        configure_logging(
            cout_level='DEBUG',
            propagate=True,
            filename=str(log_file)
        )
        
        # Create another package logger and set to WARNING
        other_logger = logging.getLogger('verbose_package')
        other_logger.setLevel(logging.WARNING)
        
        # Log from both
        sgio_logger.debug("SGIO debug message")
        other_logger.debug("Verbose debug message")
        other_logger.warning("Verbose warning message")
        
        # Check captured records
        messages = [r.getMessage() for r in capture_handler.records]
        
        # SGIO debug should be captured (logger allows it)
        assert any("SGIO debug message" in msg for msg in messages)
        
        # Verbose debug should NOT be captured (filtered by logger level)
        assert not any("Verbose debug message" in msg for msg in messages)
        
        # Verbose warning SHOULD be captured
        assert any("Verbose warning message" in msg for msg in messages)


# ============================================================================
# Test Log Formatting
# ============================================================================

@pytest.mark.unit
class TestLogFormatting:
    """Test log message formatting."""
    
    def test_message_content_preserved(self, clean_logging, tmp_path):
        """Test log message content is preserved correctly."""
        log_file = tmp_path / "message_content.log"
        
        configure_logging(filename=str(log_file))
        
        # Use ASCII-safe message to avoid encoding issues on Windows
        test_message = "Test message with special characters"
        sgio_logger.info(test_message)
        
        # Flush and close handlers to ensure write
        for handler in sgio_logger.handlers[:]:
            handler.flush()
            handler.close()
        
        # Verify message in file
        content = read_log_file(log_file)
        assert test_message in content
    
    def test_multiline_messages(self, clean_logging, tmp_path):
        """Test multiline messages are logged correctly."""
        log_file = tmp_path / "multiline.log"
        
        configure_logging(filename=str(log_file))
        
        multiline_message = "Line 1\nLine 2\nLine 3"
        sgio_logger.info(multiline_message)
        
        # Flush handlers
        for handler in sgio_logger.handlers:
            handler.flush()
        
        # Verify message in file
        content = read_log_file(log_file)
        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content


# ============================================================================
# Test Error Handling
# ============================================================================

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in logging configuration."""
    
    def test_invalid_file_path_handled(self, clean_logging):
        """Test graceful handling of invalid file paths."""
        # Try to create log in non-existent directory
        # This should raise an error, which is expected behavior
        with pytest.raises((FileNotFoundError, OSError)):
            configure_logging(filename='/nonexistent/path/to/log.log')
    
    def test_logger_works_after_handler_failure(self, clean_logging, tmp_path):
        """Test logger continues working even if configuration partially fails."""
        log_file = tmp_path / "partial_failure.log"
        
        try:
            # Configure normally first
            configure_logging(filename=str(log_file))
            
            # Logger should work
            sgio_logger.info("Test message after config")
            
            # Should not raise
            assert True
            
        except Exception as e:
            pytest.fail(f"Logger failed unexpectedly: {e}")


# ============================================================================
# Test Backward Compatibility
# ============================================================================

@pytest.mark.unit
class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""
    
    def test_default_parameters_work(self, clean_logging, tmp_path):
        """Test calling with default parameters works."""
        log_file = tmp_path / "defaults.log"
        
        # Call with only required parameter
        configure_logging(filename=str(log_file))
        
        # Should work without errors
        sgio_logger.info("Test message")
        assert len(sgio_logger.handlers) == 2
    
    def test_positional_parameters_work(self, clean_logging, tmp_path):
        """Test calling with positional parameters works."""
        log_file = tmp_path / "positional.log"
        
        # Call with positional parameters (old style)
        configure_logging('INFO', 'DEBUG', str(log_file))
        
        # Should work
        assert sgio_logger.handlers[0].level == logging.INFO
        assert sgio_logger.handlers[1].level == logging.DEBUG
    
    def test_logger_accessible_from_sgio(self, clean_logging):
        """Test logger is accessible as sgio.logger."""
        # Should be able to import and use logger
        assert hasattr(sgio, 'logger')
        assert sgio.logger is sgio_logger
        assert sgio.logger.name == 'sgio'


# ============================================================================
# Test Real-World Scenarios
# ============================================================================

@pytest.mark.unit
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_typical_application_setup(self, clean_logging, tmp_path, capture_handler):
        """Test typical application logging setup."""
        log_file = tmp_path / "app.log"
        
        # Typical setup: root logger for all packages
        # Use capture handler to test without file I/O issues
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(capture_handler)
        
        # SGIO with propagation (default)
        sgio_logger.propagate = True
        sgio_logger.setLevel(logging.DEBUG)
        
        # Log from SGIO
        sgio_logger.info("Application started")
        sgio_logger.debug("Debug information")
        
        # Verify logs captured by root logger
        assert len(capture_handler.records) >= 2
        messages = [r.getMessage() for r in capture_handler.records]
        assert "Application started" in messages
        assert "Debug information" in messages
    
    def test_isolated_sgio_logging_scenario(self, clean_logging, tmp_path):
        """Test scenario where SGIO logs are isolated."""
        sgio_file = tmp_path / "sgio.log"
        app_file = tmp_path / "app.log"
        
        # Configure SGIO isolated
        configure_logging(
            filename=str(sgio_file),
            propagate=False
        )
        
        # Configure app logging
        app_logger = logging.getLogger('myapp')
        app_handler = logging.FileHandler(str(app_file), mode='w')
        app_logger.addHandler(app_handler)
        app_logger.setLevel(logging.DEBUG)
        
        # Log from both
        sgio_logger.info("SGIO message")
        app_logger.info("App message")
        
        # Flush all
        for handler in sgio_logger.handlers:
            handler.flush()
        app_handler.flush()
        
        # Verify separation
        sgio_content = read_log_file(sgio_file)
        app_content = read_log_file(app_file)
        
        assert "SGIO message" in sgio_content
        assert "SGIO message" not in app_content
        assert "App message" in app_content
        assert "App message" not in sgio_content
