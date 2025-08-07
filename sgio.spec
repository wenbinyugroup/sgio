# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Get the project root directory (current working directory when running pyinstaller)
project_root = Path.cwd()

# Define data files that need to be included
datas = []

# Add vendor data files
vendor_data_dir = project_root / 'sgio' / '_vendors' / 'inprw' / 'inpRW'
if vendor_data_dir.exists():
    for file_pattern in ['*.txt', '*.pdf']:
        for file_path in vendor_data_dir.glob(file_pattern):
            datas.append((str(file_path), 'sgio/_vendors/inprw/inpRW/'))
            print(f"Adding data file: {file_path}")

# Add any other data files that might be needed
# datas.append(('path/to/other/data', 'destination/path/'))

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'sgio._vendors.inprw.inpRW',
    'sgio._vendors.inprw.config',
    'sgio._vendors.inprw.mesh',
    'sgio._vendors.inprw.elType',
    'sgio._vendors.inprw.csid',
    'meshio',
    'matplotlib',
    'scipy',
    'yaml',
    'numpy',
]

a = Analysis(
    ['sgio/__main__.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='sgio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
