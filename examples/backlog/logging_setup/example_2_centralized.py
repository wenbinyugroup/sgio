"""
Example 2: Centralized Logging for Multi-Package Applications

This example shows how to configure logging to capture logs from SGIO
and other packages in a single log file.

Pattern: Configure root logger BEFORE importing packages
"""

import logging
from rich.logging import RichHandler

print("\n=== Example 2: Centralized Multi-Package Logging ===\n")

def setup_centralized_logging(log_file='run.log', console_level='INFO', file_level='DEBUG'):
    """
    Set up centralized logging for all packages.
    
    This configures the root logger to capture logs from:
    - SGIO and all its submodules
    - Any other packages that use standard logging
    - Your own application code
    
    Parameters
    ----------
    log_file : str
        Path to log file
    console_level : str
        Console output level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    file_level : str
        File output level
    
    Returns
    -------
    logging.Logger
        Root logger instance
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler with Rich formatting
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(console_level.upper())
    console_formatter = logging.Formatter(
        fmt='%(name)s: %(message)s',  # Include logger name to identify source
        datefmt='[%X]'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, mode='a')  # Append mode
    file_handler.setLevel(file_level.upper())
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger

# IMPORTANT: Configure logging BEFORE importing packages
logger = setup_centralized_logging(
    log_file='run_multi.log',
    console_level='INFO',
    file_level='DEBUG'
)

# Now import packages - their logs will be captured
import sgio
import numpy as np

# Log from main application
logger.info("Application started with centralized logging")

# Use SGIO - its internal logs will appear in run_multi.log
print("\nUsing SGIO...")
sgio.logger.info("SGIO operations starting")
sgio.logger.debug("This is a debug message from SGIO")

# Your own application logging
app_logger = logging.getLogger('my_application')
app_logger.info("Application logic executing")
app_logger.debug("Detailed application information")

# Simulate some operations
for i in range(3):
    logger.info(f"Main: Processing iteration {i+1}")
    sgio.logger.debug(f"SGIO: Detailed step {i+1}")
    app_logger.info(f"App: Completed iteration {i+1}")

logger.info("Application completed successfully")

print("\n✓ All logs written to 'run_multi.log'")
print("✓ Logs from multiple packages captured")
print("✓ Console shows INFO and above with logger names")
print("✓ File contains DEBUG and above with timestamps")
