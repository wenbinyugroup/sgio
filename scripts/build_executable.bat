@echo off
REM Build script for creating SGIO executable on Windows

echo ============================================================
echo SGIO Executable Build Script (Windows)
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Run the Python build script
python build_executable.py %*

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo You can find the executable at: dist\sgio.exe
echo.
pause
