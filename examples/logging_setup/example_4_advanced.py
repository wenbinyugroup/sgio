"""
Example 4: Advanced Logging Patterns

This example demonstrates advanced logging techniques:
- Multiple log files for different purposes
- Isolated SGIO logging
- Custom formatters
- Dynamic log level adjustment
"""

import logging
from rich.logging import RichHandler
from pathlib import Path

print("\n=== Example 4: Advanced Logging Patterns ===\n")

def setup_advanced_logging():
    """
    Set up advanced logging with multiple handlers and files.
    
    Creates:
    - run_main.log: All application logs
    - run_sgio.log: SGIO-specific logs (isolated)
    - run_errors.log: Only ERROR and CRITICAL messages
    """
    # Root logger for general application
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    
    # Console handler - INFO level
    console_handler = RichHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt='%(levelname)s | %(name)s | %(message)s',
        datefmt='[%X]'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Main log file - all logs
    main_handler = logging.FileHandler('run_main.log', mode='a')
    main_handler.setLevel(logging.DEBUG)
    main_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main_handler.setFormatter(main_formatter)
    root_logger.addHandler(main_handler)
    
    # Error log file - only errors
    error_handler = logging.FileHandler('run_errors.log', mode='a')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(main_formatter)
    root_logger.addHandler(error_handler)
    
    print("✓ Root logger configured")
    print("  - Console: INFO+")
    print("  - run_main.log: DEBUG+")
    print("  - run_errors.log: ERROR+")
    
    return root_logger

def setup_sgio_isolated():
    """
    Configure SGIO with isolated logging (separate log file).
    
    This pattern is useful when you want SGIO logs completely separated
    from your application logs.
    """
    # Use SGIO's configure_logging with propagate=False
    # This prevents SGIO logs from reaching root logger
    import sgio
    sgio.configure_logging(
        cout_level='INFO',
        fout_level='DEBUG',
        filename='run_sgio.log',
        file_mode='a',
        propagate=False,  # Isolate SGIO logs
        clear_handlers=True
    )
    
    print("\n✓ SGIO logger configured (isolated)")
    print("  - run_sgio.log: DEBUG+")
    print("  - Isolated from root logger")

def demonstrate_dynamic_levels(logger):
    """Demonstrate dynamic log level adjustment."""
    print("\n" + "="*60)
    logger.info("Starting demonstration of dynamic log levels")
    
    # Initial logging at INFO level
    logger.debug("This debug message is hidden initially")
    logger.info("This info message is visible")
    
    # Change log level dynamically
    print("\n>>> Changing console level to DEBUG...")
    for handler in logging.getLogger().handlers:
        if isinstance(handler, RichHandler) and handler.level == logging.INFO:
            handler.setLevel(logging.DEBUG)
    
    logger.debug("Now this debug message is visible in console!")
    logger.info("Info messages still visible")
    
    # Change back
    print("\n>>> Changing console level back to INFO...")
    for handler in logging.getLogger().handlers:
        if isinstance(handler, RichHandler):
            handler.setLevel(logging.INFO)
    
    logger.debug("This debug is hidden again")
    logger.info("Back to normal INFO level")

def demonstrate_error_logging(logger):
    """Demonstrate error logging."""
    print("\n" + "="*60)
    logger.info("Demonstrating error logging")
    
    try:
        # Simulate an error
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error(f"Mathematical error occurred: {e}")
        logger.debug("Error details: division by zero in calculation")
    
    try:
        # Simulate another error
        data = {'key': 'value'}
        _ = data['missing_key']
    except KeyError as e:
        logger.error(f"Data access error: {e}", exc_info=True)  # Include traceback

def main():
    """Main application logic."""
    # Set up logging
    logger = setup_advanced_logging()
    setup_sgio_isolated()
    
    # Import SGIO after configuration
    import sgio
    
    # Application logging
    app_logger = logging.getLogger('advanced_app')
    
    print("\n" + "="*60)
    logger.info("Advanced logging demonstration started")
    app_logger.info("Application module initialized")
    
    # Use SGIO
    sgio.logger.info("SGIO operations starting")
    sgio.logger.debug("SGIO internal details")
    
    # Demonstrate various features
    demonstrate_dynamic_levels(logger)
    demonstrate_error_logging(logger)
    
    # Final messages
    print("\n" + "="*60)
    logger.info("Demonstration completed successfully")
    sgio.logger.info("SGIO operations completed")
    
    print("\n" + "="*60)
    print("\n✓ Logs written to multiple files:")
    print("  - run_main.log: All application logs")
    print("  - run_sgio.log: SGIO-specific logs (isolated)")
    print("  - run_errors.log: Errors only")
    print("\n✓ Demonstrated features:")
    print("  - Multiple log files")
    print("  - Isolated SGIO logging")
    print("  - Dynamic log level adjustment")
    print("  - Error logging with tracebacks")

if __name__ == '__main__':
    main()
