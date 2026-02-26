"""
Example 3: Filtering Third-Party Package Logs

This example demonstrates how to control verbosity of different packages
independently, reducing noise from verbose third-party libraries.
"""

import logging
from rich.logging import RichHandler

print("\n=== Example 3: Filtering Third-Party Package Logs ===\n")

def setup_logging_with_filtering(log_file='run_filtered.log'):
    """
    Set up logging with selective filtering of third-party packages.
    
    This reduces log noise from verbose packages while maintaining
    detailed logging for your application and SGIO.
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = RichHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt='%(name)s: %(message)s',
        datefmt='[%X]'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Filter verbose third-party packages
    # These packages are commonly very verbose and clutter logs
    VERBOSE_PACKAGES = [
        'matplotlib',
        'matplotlib.font_manager',
        'matplotlib.pyplot',
        'PIL',
        'PIL.PngImagePlugin',
        'h5py',
        'paramiko',
        'urllib3',
        'requests',
        'asyncio',
    ]
    
    print("Filtering verbose packages:")
    for package_name in VERBOSE_PACKAGES:
        pkg_logger = logging.getLogger(package_name)
        pkg_logger.setLevel(logging.WARNING)  # Only show warnings and above
        print(f"  - {package_name}: WARNING and above only")
    
    # You can also selectively enable debug logging for specific packages
    logging.getLogger('sgio').setLevel(logging.DEBUG)
    logging.getLogger('my_app').setLevel(logging.DEBUG)
    
    print("\nDebug logging enabled for:")
    print("  - sgio: All debug messages")
    print("  - my_app: All debug messages")
    
    return root_logger

# Set up logging with filtering
logger = setup_logging_with_filtering()

# Import packages
import sgio

# Application logger
app_logger = logging.getLogger('my_app')

print("\n" + "="*60)
logger.info("Starting application with filtered logging")

# Demonstrate logging from different sources
sgio.logger.info("SGIO: Starting operations")
sgio.logger.debug("SGIO: This debug message appears in logs")
app_logger.info("App: Application initialized")
app_logger.debug("App: Detailed application state")

# Simulate a verbose third-party package
matplotlib_logger = logging.getLogger('matplotlib.font_manager')
matplotlib_logger.debug("This matplotlib debug is filtered out")
matplotlib_logger.info("This matplotlib info is filtered out")
matplotlib_logger.warning("This matplotlib warning DOES appear")

# More application logging
for i in range(3):
    logger.info(f"Main: Processing item {i+1}")
    sgio.logger.debug(f"SGIO: Internal processing details for item {i+1}")
    app_logger.debug(f"App: Additional context for item {i+1}")

logger.info("Application completed")

print("="*60)
print("\n✓ Verbose packages filtered to WARNING level")
print("✓ SGIO and app logs include DEBUG messages")
print("✓ Console remains clean and readable")
print("✓ All logs (including filtered) in 'run_filtered.log'")
