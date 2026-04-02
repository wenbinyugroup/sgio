# Logging Configuration Guide

This guide explains how to configure and use logging with SGIO in various scenarios, from simple single-package applications to complex multi-package environments.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Multi-Package Applications](#multi-package-applications)
- [Configuration Reference](#configuration-reference)
- [Filtering Third-Party Packages](#filtering-third-party-packages)
- [Advanced Topics](#advanced-topics)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

### Python's Logging Hierarchy

SGIO uses Python's standard `logging` module with Rich formatting for enhanced output. Understanding the logger hierarchy is key to effective logging:

```
root logger
├── sgio (main logger)
│   ├── sgio.core.builder
│   ├── sgio.core.merge
│   ├── sgio.iofunc.vabs._input
│   └── sgio.execu
├── numpy
├── matplotlib
└── your_app
```

**Key Concepts:**

- **Logger Hierarchy**: Child loggers (e.g., `sgio.core.builder`) automatically propagate messages to their parent (`sgio`)
- **Propagation**: When `propagate=True` (default), logs flow up the hierarchy to parent loggers
- **Handlers**: Determine where logs go (console, file, network, etc.)
- **Levels**: Control verbosity (DEBUG < INFO < WARNING < ERROR < CRITICAL)

### How SGIO Fits In

- Main logger: `'sgio'` (accessible as `sgio.logger`)
- Module loggers: Each SGIO module uses `logging.getLogger(__name__)`
- Default behavior: Logs propagate to parent loggers for easy integration

## Quick Start

### Single-Package Application

If you're only using SGIO:

```python
import sgio

# Configure SGIO logging
sgio.configure_logging(
    cout_level='INFO',      # Console output level
    fout_level='DEBUG',     # File output level
    filename='run.log'      # Log file path
)

# Use SGIO - logs appear automatically
model = sgio.readOutputModel('file.sg.k', 'vabs', 'BM1')
```

**Result:**
- Console shows INFO and above
- File contains DEBUG and above
- Logs append across runs (accumulate)

### Multi-Package Application

If you're using SGIO with other packages:

```python
import logging
from rich.logging import RichHandler

# STEP 1: Configure root logger BEFORE importing packages
root = logging.getLogger()
root.setLevel(logging.DEBUG)

# Console handler
console = RichHandler()
console.setLevel(logging.INFO)
root.addHandler(console)

# File handler
file_handler = logging.FileHandler('run.log', mode='a')
file_handler.setLevel(logging.DEBUG)
root.addHandler(file_handler)

# STEP 2: Now import packages - their logs will be captured
import sgio
import numpy as np
import your_app

# STEP 3: Use packages - all logs go to run.log
sgio.logger.info("Starting analysis")
your_app.process_data()
```

**Result:**
- All package logs captured in single file
- Centralized log management
- Easy filtering by package name

## Multi-Package Applications

### Pattern: Centralized Logging Setup

This is the **recommended pattern** for applications using multiple packages:

```python
import logging
from rich.logging import RichHandler

def setup_logging(log_file='run.log', console_level='INFO', file_level='DEBUG'):
    """
    Configure centralized logging for all packages.
    
    Call this BEFORE importing other packages to ensure all logs are captured.
    """
    # Configure root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # Capture all levels
    root.handlers.clear()  # Clear any existing handlers
    
    # Console handler with Rich formatting
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(console_level.upper())
    console_formatter = logging.Formatter(
        fmt='%(name)s: %(message)s',  # Include logger name
        datefmt='[%X]'
    )
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(file_level.upper())
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root.addHandler(file_handler)
    
    return root

# Use it
if __name__ == '__main__':
    logger = setup_logging(log_file='run.log')
    
    # Now import and use packages
    import sgio
    # ... rest of your code
```

**Benefits:**
- Single log file for all packages
- Consistent formatting
- Easy to filter by package name
- Standard Python pattern

### Pattern: Isolated SGIO Logging

If you want SGIO logs in a separate file:

```python
import logging
import sgio

# Configure SGIO with isolation
sgio.configure_logging(
    filename='sgio.log',
    propagate=False  # Prevent logs from reaching root logger
)

# Configure root logger for other packages
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler('app.log')]
)

# Result:
# - SGIO logs go to sgio.log only
# - Other package logs go to app.log only
```

## Configuration Reference

### `sgio.configure_logging()` Parameters

```python
sgio.configure_logging(
    cout_level='INFO',
    fout_level='INFO',
    filename='sgio.log',
    file_mode='a',
    propagate=True,
    clear_handlers=True
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cout_level` | str | `'INFO'` | Console output level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `fout_level` | str | `'INFO'` | File output level (same options as cout_level) |
| `filename` | str | `'sgio.log'` | Path to log file |
| `file_mode` | str | `'a'` | File mode: 'a' for append (accumulate logs), 'w' for overwrite (fresh file each run) |
| `propagate` | bool | `True` | If True, logs propagate to parent loggers (enables centralized logging). If False, logs are isolated to SGIO handlers only. |
| `clear_handlers` | bool | `True` | If True, clear existing handlers before adding new ones to prevent duplicate log messages |

### Log Levels

Levels in order of increasing severity:

| Level | Numeric Value | Usage |
|-------|---------------|-------|
| DEBUG | 10 | Detailed diagnostic information |
| INFO | 20 | Confirmation that things are working as expected |
| WARNING | 30 | Something unexpected, but code still works |
| ERROR | 40 | Serious problem, a function failed |
| CRITICAL | 50 | Very serious error, program may not continue |

**Level Filtering:**
```python
# Logger level filters first
logger.setLevel(logging.INFO)  # Blocks DEBUG messages

# Handler level filters what gets output
handler.setLevel(logging.WARNING)  # Only WARNING and above

# Result: Only WARNING, ERROR, CRITICAL appear
```

### File Mode Comparison

| Mode | Behavior | Use Case |
|------|----------|----------|
| `'a'` | Append to existing file | Production, accumulate history across runs |
| `'w'` | Overwrite file each time | Development, testing, want fresh start |

```python
# Accumulate logs across runs (default)
sgio.configure_logging(file_mode='a', filename='run.log')

# Fresh log file each run
sgio.configure_logging(file_mode='w', filename='run.log')
```

## Filtering Third-Party Packages

Many third-party packages are very verbose. You can control their log levels independently:

### Common Verbose Packages

```python
import logging

# Reduce noise from verbose packages
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('h5py').setLevel(logging.WARNING)
logging.getLogger('paramiko').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Keep detailed logging for your packages
logging.getLogger('sgio').setLevel(logging.DEBUG)
logging.getLogger('myapp').setLevel(logging.DEBUG)
```

### Complete Example with Filtering

```python
import logging
from rich.logging import RichHandler

def setup_logging_with_filtering(log_file='run.log'):
    """Configure logging with third-party package filtering."""
    # Configure root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()
    
    # Console handler
    console = RichHandler()
    console.setLevel(logging.INFO)
    root.addHandler(console)
    
    # File handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    
    # Filter verbose packages (set AFTER root logger)
    VERBOSE_PACKAGES = [
        'matplotlib', 'PIL', 'h5py', 'paramiko', 'urllib3'
    ]
    for pkg in VERBOSE_PACKAGES:
        logging.getLogger(pkg).setLevel(logging.WARNING)
    
    return root

# Use it
logger = setup_logging_with_filtering()
import sgio  # SGIO logs still at DEBUG level
```

## Advanced Topics

### Multiple Log Files

```python
import logging
import sgio

# SGIO logs to sgio.log (isolated)
sgio.configure_logging(
    filename='sgio.log',
    propagate=False
)

# Application logs to app.log
app_logger = logging.getLogger('myapp')
app_handler = logging.FileHandler('app.log')
app_logger.addHandler(app_handler)

# Errors to errors.log
error_handler = logging.FileHandler('errors.log')
error_handler.setLevel(logging.ERROR)
logging.root.addHandler(error_handler)
```

### Dynamic Log Level Adjustment

```python
import logging
import sgio

# Initial configuration
sgio.configure_logging(cout_level='INFO')

# Later, change console level to DEBUG
for handler in sgio.logger.handlers:
    if hasattr(handler, 'setLevel'):
        handler.setLevel(logging.DEBUG)

# Now DEBUG messages appear in console
sgio.logger.debug("This now appears!")
```

### Log Rotation

For long-running applications, use rotating file handlers:

```python
import logging
from logging.handlers import RotatingFileHandler

# Rotate when file reaches 10MB, keep 5 backups
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setLevel(logging.DEBUG)
logging.root.addHandler(handler)
```

### Custom Formatters

```python
import logging

# Detailed format with extra context
formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s:%(lineno)-4d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# JSON format for log aggregators
import json
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }
        return json.dumps(log_obj)
```

## Troubleshooting

### Problem: No logs appearing

**Possible causes:**
1. Logger level too high
2. Handler level too high
3. Propagation disabled
4. No handlers added

**Solution:**
```python
import logging

# Check logger level
logger = logging.getLogger('sgio')
print(f"Logger level: {logger.level}")  # Should be <= desired level

# Check handler levels
for handler in logger.handlers:
    print(f"Handler {handler}: level={handler.level}")

# Check propagation
print(f"Propagate: {logger.propagate}")  # Should be True for centralized logging

# Verify handlers exist
print(f"Number of handlers: {len(logger.handlers)}")
```

### Problem: Duplicate log messages

**Cause:** Multiple handlers added without clearing

**Solution:**
```python
# Use clear_handlers=True (default)
sgio.configure_logging(clear_handlers=True)

# Or manually clear
sgio.logger.handlers.clear()
```

### Problem: Logs not in centralized file

**Cause:** `propagate=False` prevents logs from reaching root logger

**Solution:**
```python
# Ensure propagation is enabled
sgio.configure_logging(propagate=True)  # This is the default

# Or set directly
sgio.logger.propagate = True
```

### Problem: File not created or empty

**Possible causes:**
1. File path doesn't exist
2. Permission issues
3. Handlers not flushed

**Solution:**
```python
from pathlib import Path

# Ensure directory exists
log_file = Path('logs/run.log')
log_file.parent.mkdir(parents=True, exist_ok=True)

# Configure logging
sgio.configure_logging(filename=str(log_file))

# Write logs
sgio.logger.info("Test message")

# Flush handlers
for handler in sgio.logger.handlers:
    handler.flush()
```

### Problem: Too many logs from third-party packages

**Solution:** Filter verbose packages (see [Filtering](#filtering-third-party-packages) section)

## Best Practices

### For Applications

1. **Configure early**: Set up logging before importing packages
   ```python
   # Do this FIRST
   setup_logging()
   
   # Then import
   import sgio
   ```

2. **Use centralized logging**: Configure root logger for multi-package apps
   ```python
   logging.basicConfig(handlers=[...])
   ```

3. **Use append mode**: Accumulate logs across runs
   ```python
   sgio.configure_logging(file_mode='a')
   ```

4. **Different levels for console vs file**: 
   ```python
   sgio.configure_logging(
       cout_level='INFO',   # Less verbose console
       fout_level='DEBUG'   # Detailed file logs
   )
   ```

5. **Filter verbose packages**: Reduce log noise
   ```python
   logging.getLogger('matplotlib').setLevel(logging.WARNING)
   ```

6. **Include context in messages**:
   ```python
   logger.info(f"Processing {filename} with {num_elements} elements")
   ```

### For Library Developers

1. **Use module-level loggers**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. **Don't configure handlers**: Let applications control configuration
   ```python
   # DON'T do this in libraries
   logging.basicConfig(...)  # ❌
   
   # DO this instead
   logger = logging.getLogger(__name__)  # ✅
   ```

3. **Use appropriate levels**:
   - DEBUG: Internal state, detailed diagnostics
   - INFO: Major operations, confirmations
   - WARNING: Unexpected but handled situations
   - ERROR: Operation failed
   - CRITICAL: Cannot continue

4. **Keep propagate=True**: Don't break logger hierarchy
   ```python
   # DON'T do this in libraries
   logger.propagate = False  # ❌
   ```

### General Guidelines

1. **One configuration per application**: Don't configure in multiple places
2. **DEBUG for development, INFO for production**
3. **Use structured logging**: Include relevant context
4. **Don't log sensitive data**: Passwords, keys, personal information
5. **Use log rotation for long-running apps**: Prevent huge files
6. **Test logging**: Verify logs appear where expected

## Examples

Complete working examples are available in the `examples/logging_setup/` directory:

- **example_1_basic.py**: Simple SGIO logging setup
- **example_2_centralized.py**: Multi-package centralized logging
- **example_3_filtering.py**: Filtering third-party packages
- **example_4_advanced.py**: Advanced patterns (multiple files, dynamic levels)
- **main.py**: Comprehensive demonstration of all features

Run any example:
```bash
python examples/logging_setup/main.py
```

See [examples/logging_setup/README.md](../../../examples/logging_setup/README.md) for details.

## Related Documentation

- [Python logging documentation](https://docs.python.org/3/library/logging.html)
- [Rich logging handler](https://rich.readthedocs.io/en/stable/logging.html)
- [SGIO API reference](../api/index.md)

---

**Questions or Issues?**

If you encounter problems with logging or have questions:
1. Check this guide and the troubleshooting section
2. Review the examples in `examples/logging_setup/`
3. Open an issue on GitHub with details and log output
