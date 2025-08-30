#!/usr/bin/env python3
"""
Build script for creating a one-file executable of sgio using PyInstaller.

This script handles:
- Installing required dependencies
- Building the executable with proper data file inclusion
- Cleaning up build artifacts
- Testing the executable
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

def run_command(cmd, check=True, shell=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        if check:
            raise
        return e

def install_dependencies():
    """Install required dependencies for building."""
    print("Installing build dependencies...")
    
    # Install PyInstaller and other build dependencies
    deps = [
        "pyinstaller>=5.0",
        "setuptools",
        "wheel",
    ]
    
    for dep in deps:
        run_command(f"pip install {dep}")

def clean_build_artifacts():
    """Clean up previous build artifacts."""
    print("Cleaning up previous build artifacts...")
    
    artifacts = [
        "build",
        "dist/sgio.exe",
        "__pycache__",
        "sgio.spec.bak",
    ]
    
    for artifact in artifacts:
        path = Path(artifact)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {artifact}")
            else:
                path.unlink()
                print(f"Removed file: {artifact}")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    
    # Use the updated spec file
    cmd = "pyinstaller sgio.spec --clean --noconfirm"
    result = run_command(cmd)
    
    if result.returncode == 0:
        print("✓ Executable built successfully!")
        return True
    else:
        print("✗ Failed to build executable")
        return False

def test_executable():
    """Test the built executable."""
    print("Testing the built executable...")
    
    exe_path = Path("dist/sgio.exe")
    if not exe_path.exists():
        print("✗ Executable not found!")
        return False
    
    # Test basic functionality
    test_commands = [
        "dist\\sgio.exe --version",
        "dist\\sgio.exe --help",
    ]
    
    for cmd in test_commands:
        print(f"Testing: {cmd}")
        result = run_command(cmd, check=False)
        if result.returncode != 0:
            print(f"✗ Test failed: {cmd}")
            return False
        print(f"✓ Test passed: {cmd}")
    
    print("✓ All tests passed!")
    return True

def create_distribution():
    """Create a distribution package."""
    print("Creating distribution package...")
    
    # Create a dist directory structure
    dist_dir = Path("dist/sgio-standalone")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy the executable
    exe_src = Path("dist/sgio.exe")
    exe_dst = dist_dir / "sgio.exe"
    
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        print(f"Copied executable to: {exe_dst}")
    
    # Create a README for the distribution
    readme_content = """# SGIO Standalone Executable

This is a standalone executable version of SGIO (Structure Gene I/O).

## Usage

Simply run the executable from the command line:

```
sgio.exe --help
sgio.exe convert input.inp output.sg -ff abaqus -tf vabs -m bm2
```

## Features

- No Python installation required
- All dependencies bundled
- Cross-platform compatible
- Full SGIO functionality

For more information, visit: https://github.com/wenbinyugroup/sgio
"""
    
    readme_path = dist_dir / "README.md"
    readme_path.write_text(readme_content)
    print(f"Created README: {readme_path}")
    
    print(f"✓ Distribution created in: {dist_dir}")

def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build SGIO executable")
    parser.add_argument("--clean", action="store_true", 
                       help="Clean build artifacts before building")
    parser.add_argument("--no-test", action="store_true",
                       help="Skip testing the executable")
    parser.add_argument("--no-deps", action="store_true",
                       help="Skip installing dependencies")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SGIO Executable Build Script")
    print("=" * 60)
    
    try:
        if args.clean:
            clean_build_artifacts()
        
        if not args.no_deps:
            install_dependencies()
        
        success = build_executable()
        if not success:
            sys.exit(1)
        
        if not args.no_test:
            test_success = test_executable()
            if not test_success:
                print("Warning: Tests failed, but executable was built")
        
        create_distribution()
        
        print("\n" + "=" * 60)
        print("✓ Build completed successfully!")
        print("✓ Executable available at: dist/sgio.exe")
        print("✓ Distribution package at: dist/sgio-standalone/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
