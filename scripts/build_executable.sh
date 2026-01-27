#!/bin/bash
# Build script for creating SGIO executable on Unix-like systems

echo "============================================================"
echo "SGIO Executable Build Script (Unix/Linux/macOS)"
echo "============================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ and try again"
    exit 1
fi

# Run the Python build script
python3 build_executable.py "$@"

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo ""
echo "Build completed successfully!"
echo "You can find the executable at: dist/sgio"
echo ""
