"""
Main Example: Comprehensive SGIO Logging Demonstration

This is the main example demonstrating all logging patterns in one place.
Run this to see all features and best practices.

Usage:
    python main.py
"""

import logging
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

print("\n" + "="*70)
print("  SGIO Logging Comprehensive Example")
print("="*70)

def setup_logging(log_file='run.log', console_level='INFO', file_level='DEBUG'):
    """
    Set up centralized logging for multi-package applications.
    
    This is the recommended pattern for applications using SGIO
    along with other packages.
    
    Parameters
    ----------
    log_file : str
        Path to log file
    console_level : str
        Console output level
    file_level : str
        File output level
    
    Returns
    -------
    logging.Logger
        Configured root logger
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    
    # Console handler with Rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_path=False
    )
    console_handler.setLevel(console_level.upper())
    console_formatter = logging.Formatter(
        fmt='%(name)s: %(message)s',
        datefmt='[%X]'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(file_level.upper())
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Optional: Filter verbose third-party packages
    verbose_packages = ['matplotlib', 'PIL', 'h5py', 'paramiko']
    for pkg in verbose_packages:
        logging.getLogger(pkg).setLevel(logging.WARNING)
    
    return root_logger

def demonstrate_basic_logging(logger):
    """Demonstrate basic logging functionality."""
    print("\n[1] Basic Logging")
    print("-" * 70)
    
    logger.info("Starting basic logging demonstration")
    logger.debug("This is a debug message (appears in file only)")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    
    print("  ✓ Basic logging messages generated")

def demonstrate_sgio_integration(logger):
    """Demonstrate SGIO integration."""
    print("\n[2] SGIO Integration")
    print("-" * 70)
    
    import sgio
    
    logger.info("Importing and using SGIO")
    
    # SGIO's internal loggers automatically work with root logger
    sgio.logger.info("SGIO initialized")
    sgio.logger.debug("SGIO debug information")
    
    # Simulate SGIO operations
    logger.info("Simulating SGIO operations...")
    for i in range(3):
        sgio.logger.debug(f"Processing internal step {i+1}")
        logger.info(f"Operation {i+1} completed")
    
    print("  ✓ SGIO logs integrated with application logs")

def demonstrate_hierarchical_logging(logger):
    """Demonstrate hierarchical logger structure."""
    print("\n[3] Hierarchical Logging")
    print("-" * 70)
    
    # Create hierarchical loggers
    module_logger = logging.getLogger('myapp.module')
    submodule_logger = logging.getLogger('myapp.module.submodule')
    
    logger.info("Demonstrating logger hierarchy")
    module_logger.info("Message from module")
    submodule_logger.info("Message from submodule")
    
    # All these propagate to root logger
    module_logger.debug("Module debug information")
    
    print("  ✓ Hierarchical loggers working correctly")

def demonstrate_error_handling(logger):
    """Demonstrate error logging."""
    print("\n[4] Error Handling")
    print("-" * 70)
    
    logger.info("Demonstrating error logging")
    
    try:
        # Simulate an error
        result = 1 / 0
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        logger.exception("Full traceback:")  # Includes stack trace
    
    print("  ✓ Error logged with traceback")

def demonstrate_log_file_management():
    """Show log file information."""
    print("\n[5] Log File Management")
    print("-" * 70)
    
    log_file = Path('run.log')
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"  Log file: {log_file}")
        print(f"  Size: {size} bytes")
        print(f"  Mode: Append (logs accumulate across runs)")
    else:
        print(f"  Log file: {log_file} (will be created)")
    
    print("  ✓ Log file management info displayed")

def print_summary():
    """Print summary of what was demonstrated."""
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
This example demonstrated:

1. ✓ Centralized logging setup
   - Configure root logger before importing packages
   - All package logs captured automatically

2. ✓ SGIO integration
   - SGIO logs flow to centralized log file
   - Child module loggers work correctly

3. ✓ Hierarchical logging
   - Module and submodule loggers
   - Proper propagation to root logger

4. ✓ Error handling
   - Exception logging with tracebacks
   - Structured error messages

5. ✓ Log file management
   - Append mode (accumulates logs)
   - Detailed file formatting

Next Steps:
- Review 'run.log' to see detailed log output
- Try other examples: example_1_basic.py, example_2_centralized.py, etc.
- Read the logging guide: docs/source/guide/logging.md

""")

def main():
    """Main application entry point."""
    # STEP 1: Configure logging BEFORE importing packages
    logger = setup_logging(
        log_file='run.log',
        console_level='INFO',
        file_level='DEBUG'
    )
    
    print("\n✓ Logging configured")
    print(f"  Console level: INFO")
    print(f"  File level: DEBUG")
    print(f"  Log file: run.log")
    
    # STEP 2: Now import and use packages
    logger.info("="*50)
    logger.info("Application started")
    logger.info("="*50)
    
    # Run demonstrations
    try:
        demonstrate_basic_logging(logger)
        demonstrate_sgio_integration(logger)
        demonstrate_hierarchical_logging(logger)
        demonstrate_error_handling(logger)
        demonstrate_log_file_management()
        
        logger.info("="*50)
        logger.info("Application completed successfully")
        logger.info("="*50)
        
        print_summary()
        
    except Exception as e:
        logger.exception(f"Application error: {e}")
        raise

if __name__ == '__main__':
    main()
