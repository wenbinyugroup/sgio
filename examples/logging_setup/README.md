# SGIO Logging Examples

This directory contains examples demonstrating how to configure and use logging with SGIO in various scenarios.

## Quick Start

Run the main comprehensive example:

```bash
python main.py
```

This will demonstrate all logging features and create a `run.log` file with detailed logs.

## Examples

### Example 1: Basic Usage (`example_1_basic.py`)

**Purpose:** Simplest SGIO logging setup for single-package applications.

**What it shows:**
- Basic `configure_logging()` usage
- Console and file output
- Different log levels

**Run:**
```bash
python example_1_basic.py
```

**Output:** `run.log`

---

### Example 2: Centralized Logging (`example_2_centralized.py`)

**Purpose:** Multi-package application with centralized logging.

**What it shows:**
- Configure root logger to capture all packages
- SGIO integrates automatically
- Multiple loggers writing to single file

**Run:**
```bash
python example_2_centralized.py
```

**Output:** `run_multi.log`

**Key Pattern:**
```python
# 1. Configure root logger FIRST
import logging
root = logging.getLogger()
root.addHandler(logging.FileHandler('run.log'))

# 2. Then import packages
import sgio

# 3. All logs automatically captured!
```

---

### Example 3: Filtering Third-Party Packages (`example_3_filtering.py`)

**Purpose:** Control verbosity of different packages independently.

**What it shows:**
- Reduce noise from verbose packages (matplotlib, PIL, etc.)
- Keep detailed logging for your application and SGIO
- Selective log level control

**Run:**
```bash
python example_3_filtering.py
```

**Output:** `run_filtered.log`

**Key Pattern:**
```python
# Reduce third-party package verbosity
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

# Keep your packages at DEBUG level
logging.getLogger('sgio').setLevel(logging.DEBUG)
logging.getLogger('myapp').setLevel(logging.DEBUG)
```

---

### Example 4: Advanced Patterns (`example_4_advanced.py`)

**Purpose:** Advanced logging techniques for complex applications.

**What it shows:**
- Multiple log files (main, errors, SGIO-specific)
- Isolated SGIO logging with `propagate=False`
- Dynamic log level adjustment
- Error logging with tracebacks

**Run:**
```bash
python example_4_advanced.py
```

**Output:** `run_main.log`, `run_sgio.log`, `run_errors.log`

---

### Main Example (`main.py`)

**Purpose:** Comprehensive demonstration of all features.

**What it shows:**
- Complete logging setup
- SGIO integration
- Hierarchical loggers
- Error handling
- Best practices

**Run:**
```bash
python main.py
```

**Output:** `run.log`

---

## Common Patterns

### Pattern 1: Simple SGIO Application

```python
import sgio

# Configure SGIO logging
sgio.configure_logging(cout_level='INFO', filename='app.log')

# Use SGIO
model = sgio.readOutputModel('file.sg.k', 'vabs', 'BM1')
```

### Pattern 2: Multi-Package Application

```python
import logging

# Configure root logger BEFORE imports
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Now import packages
import sgio
import numpy as np
import myapp

# All logs captured automatically!
```

### Pattern 3: Isolated SGIO Logging

```python
import sgio

# Isolate SGIO logs to separate file
sgio.configure_logging(
    filename='sgio.log',
    propagate=False  # Don't send to root logger
)

# Configure root logger for everything else
import logging
logging.basicConfig(filename='app.log')
```

## Configuration Options

### `sgio.configure_logging()` Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cout_level` | str | 'INFO' | Console output level |
| `fout_level` | str | 'INFO' | File output level |
| `filename` | str | 'sgio.log' | Log file path |
| `file_mode` | str | 'a' | 'a' for append, 'w' for overwrite |
| `propagate` | bool | True | Propagate to parent loggers |
| `clear_handlers` | bool | True | Clear existing handlers |

### Log Levels

In order of increasing severity:
- `DEBUG`: Detailed diagnostic information
- `INFO`: Confirmation that things are working
- `WARNING`: Something unexpected, but code still works
- `ERROR`: Serious problem, function failed
- `CRITICAL`: Program may not continue

## File Management

### Append vs Overwrite

**Append mode (default):**
```python
sgio.configure_logging(file_mode='a', filename='run.log')
```
- Logs accumulate across runs
- Good for long-running applications
- Historical record maintained

**Overwrite mode:**
```python
sgio.configure_logging(file_mode='w', filename='run.log')
```
- Fresh log file each run
- Good for development/testing
- Prevents file from growing

### Log Rotation

For production applications, consider log rotation:

```python
from logging.handlers import RotatingFileHandler

# Rotate when file reaches 10MB, keep 5 backups
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,
    backupCount=5
)
```

## Troubleshooting

### Issue: No logs appearing

**Solution:** Check log levels at both logger and handler:
```python
# Logger level must be <= handler level
logger.setLevel(logging.DEBUG)  # Logger allows DEBUG+
handler.setLevel(logging.INFO)   # Handler shows INFO+
# Result: DEBUG messages captured but not shown
```

### Issue: Duplicate log messages

**Solution:** Clear handlers before adding new ones:
```python
sgio.configure_logging(clear_handlers=True)  # Default behavior
```

### Issue: SGIO logs not in root logger

**Solution:** Ensure propagation is enabled:
```python
sgio.configure_logging(propagate=True)  # Default behavior
```

### Issue: Too many logs from third-party packages

**Solution:** Filter verbose packages:
```python
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
```

## Best Practices

1. **Configure logging early:** Before importing packages
2. **Use append mode:** For production (`file_mode='a'`)
3. **Separate console and file levels:** INFO for console, DEBUG for file
4. **Include logger names:** In file format to identify source
5. **Filter verbose packages:** Reduce noise in logs
6. **Use appropriate levels:** DEBUG for development, INFO for production
7. **Add context:** Include relevant information in log messages
8. **Handle errors:** Use `logger.exception()` to include tracebacks

## Further Reading

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [SGIO Logging Guide](../../docs/source/guide/logging.md)
- [Rich Logging Handler](https://rich.readthedocs.io/en/stable/logging.html)

## Questions?

If you have questions or need help with logging setup, please:
1. Check the [Logging Guide](../../docs/source/guide/logging.md)
2. Review these examples
3. Open an issue on GitHub
