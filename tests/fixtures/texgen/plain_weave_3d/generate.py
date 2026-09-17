"""Generate the minimal 3D plain-weave TexGen fixture."""

from __future__ import annotations

import os
import sys
from pathlib import Path


TEXGEN_ROOT = Path(r"C:\Program Files\TexGen")
TEXGEN_PACKAGE_PARENT = TEXGEN_ROOT / "Python" / "libxtra"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = OUTPUT_DIR / "plain_weave_3d.inp"
VOXEL_GRID = (3, 3, 1)


def configure_texgen() -> None:
    """Make the TexGen Python package and DLLs importable."""
    package_dir = TEXGEN_PACKAGE_PARENT / "TexGen"
    if not package_dir.is_dir():
        raise RuntimeError(f"TexGen Python bindings not found at {package_dir}")

    sys.path.insert(0, os.fspath(TEXGEN_PACKAGE_PARENT))
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(os.fspath(TEXGEN_ROOT))
        os.add_dll_directory(os.fspath(package_dir))


def generate_fixture() -> None:
    """Generate the minimal periodic Abaqus input and orientation files."""
    configure_texgen()
    from TexGen.Core import CRectangularVoxelMesh, CTextileWeave2D

    textile = CTextileWeave2D(2, 2, 1.0, 0.2, False)
    textile.SwapPosition(0, 0)
    textile.SwapPosition(1, 1)
    textile.SetYarnWidths(0.8)
    textile.SetYarnHeights(0.1)
    textile.AssignDefaultDomain()

    mesh = CRectangularVoxelMesh("CPeriodicBoundaries")
    mesh.SaveVoxelMesh(textile, os.fspath(OUTPUT_PATH), *VOXEL_GRID, True, True, 0)

    # TexGen always emits this unreferenced auxiliary file. It is not needed by SGIO.
    OUTPUT_PATH.with_suffix(".eld").unlink(missing_ok=True)


if __name__ == "__main__":
    generate_fixture()
