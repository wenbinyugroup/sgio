# Building SGIO as a One-File Executable

This document explains how to build SGIO as a standalone, one-file executable that can be distributed without requiring Python installation.

## Quick Start

### Windows
```batch
# Run the build script
build_executable.bat

# Or run directly with Python
python build_executable.py
```

### Linux/macOS
```bash
# Run the build script
./build_executable.sh

# Or run directly with Python
python3 build_executable.py
```

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- All project dependencies (will be installed automatically)

## Build Process

The build process includes:

1. **Dependency Installation**: Installs PyInstaller and other build dependencies
2. **Data File Collection**: Gathers all necessary data files (especially vendor files)
3. **Executable Creation**: Uses PyInstaller to create a one-file executable
4. **Testing**: Runs basic tests to ensure the executable works
5. **Distribution Package**: Creates a distribution folder with the executable and documentation

## Build Options

```bash
# Clean build (removes previous artifacts)
python build_executable.py --clean

# Skip dependency installation
python build_executable.py --no-deps

# Skip testing
python build_executable.py --no-test

# Combine options
python build_executable.py --clean --no-test
```

## Output

After a successful build, you'll find:

- `dist/sgio.exe` (Windows) or `dist/sgio` (Linux/macOS) - The standalone executable
- `dist/sgio-standalone/` - Distribution package with executable and README

## Technical Details

### PyInstaller Configuration

The build uses an enhanced PyInstaller spec file (`sgio.spec`) that:

- Includes all vendor data files (especially `inprw` module data)
- Specifies hidden imports for dynamic modules
- Configures one-file mode for easy distribution
- Optimizes for size and performance

### Data Files Included

The executable includes:
- All Python modules and dependencies
- Vendor data files (`elInfoDict.txt`, `keyword_names.txt`, etc.)
- Configuration files
- Documentation files

### Dependencies Bundled

The executable bundles:
- meshio (mesh I/O library)
- matplotlib (plotting)
- scipy (scientific computing)
- PyYAML (YAML parsing)
- numpy (numerical computing)
- All vendor modules (inprw, etc.)

## Troubleshooting

### Common Issues

1. **Missing Data Files Error**
   ```
   FileNotFoundError: [Errno 2] No such file or directory: '...\elInfoDict.txt'
   ```
   - Solution: The updated spec file should fix this by properly including vendor data files

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'xyz'
   ```
   - Solution: Add missing modules to `hiddenimports` in `sgio.spec`

3. **Large Executable Size**
   - The executable may be 100-200MB due to bundled scientific libraries
   - This is normal for Python applications with scientific dependencies

### Manual Build

If the automated script fails, you can build manually:

```bash
# Install PyInstaller
pip install pyinstaller

# Clean previous builds
pyinstaller sgio.spec --clean --noconfirm

# Test the executable
dist/sgio.exe --version  # Windows
dist/sgio --version      # Linux/macOS
```

### Debugging

To debug build issues:

1. Check the PyInstaller output for warnings
2. Test the executable with `--help` and `--version` flags
3. Run with a simple conversion to test core functionality
4. Check the `build/` directory for detailed logs

## Distribution

The standalone executable can be distributed as:

1. **Single File**: Just the `sgio.exe`/`sgio` file
2. **Package**: The `dist/sgio-standalone/` folder with documentation
3. **Installer**: Create an installer using tools like NSIS (Windows) or create a .deb/.rpm package (Linux)

## Performance Notes

- First run may be slower due to extraction of bundled files
- Subsequent runs should be faster
- The executable is larger than a regular Python script but requires no installation
- Memory usage is similar to running the Python script directly

## Maintenance

When updating the project:

1. Update dependencies in `pyproject.toml`
2. Update `hiddenimports` in `sgio.spec` if new modules are added
3. Update data file patterns if new data files are added
4. Test the executable thoroughly after changes
5. Update version numbers and documentation

## Alternative Build Tools

While this setup uses PyInstaller, other options include:

- **cx_Freeze**: Cross-platform alternative to PyInstaller
- **Nuitka**: Compiles Python to C++ for better performance
- **auto-py-to-exe**: GUI wrapper for PyInstaller
- **briefcase**: Part of the BeeWare suite for app packaging

Choose PyInstaller for its maturity, wide compatibility, and good handling of complex dependencies like those in SGIO.
