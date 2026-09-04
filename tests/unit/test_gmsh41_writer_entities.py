"""Regression test for Gmsh 4.1 entity-block writing without physical tags.

Covers the fix where an entity with a matching cell block but no
``gmsh:physical`` cell data used to write nothing for the physical-tag-count
field, corrupting the $Entities block structure. It must now write a zero
count, matching the "no matching cell block" branch.
"""

from __future__ import annotations

import numpy as np
import pytest

from sgio.core.mesh import CellBlock, SGMesh
from sgio.iofunc.gmsh.adapter import GmshReader, GmshWriter


def _build_triangle_mesh_without_physical_tags() -> SGMesh:
    """A minimal mesh-only triangle mesh with no gmsh:physical cell data."""
    return SGMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
        cells=[CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))],
    )


@pytest.mark.unit
@pytest.mark.gmsh
def test_gmsh41_entities_roundtrip_without_physical_tags(tmp_path):
    """Writing entities (mesh_only=False) with no physical groups must
    still produce a structurally valid, readable .msh file.

    Binary Gmsh 4.1 writing has a pre-existing, unrelated bug (writing str
    to a binary file handle at _gmsh41.write_buffer's $MeshFormat line), so
    this regression test only covers ASCII, which is what actually exercises
    the physical-tag-count fix.
    """
    mesh = _build_triangle_mesh_without_physical_tags()
    msh_path = tmp_path / "no_physical.msh"

    GmshWriter().write_input(
        str(msh_path), mesh, format_version="4.1",
        mesh_only=False, binary=False, sgdim=2,
    )

    text = msh_path.read_text()
    assert "$Entities" in text
    # Regression check: the physical-tag-count field for the 2D entity
    # must be an explicit "0", not silently omitted.
    entities_block = text.split("$Entities")[1].split("$EndEntities")[0]
    assert "\n0 " in entities_block or entities_block.strip().endswith("0")

    read_mesh = GmshReader().read_input(str(msh_path), format_version="4.1")
    assert len(read_mesh.cells) == 1
    assert read_mesh.cells[0].data.shape == (1, 3)
