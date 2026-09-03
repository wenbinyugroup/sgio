"""Reader for Gmsh's MSH file format version 4.0.

MSH 4.0 declares itself as ``4`` (not ``4.0``) in ``$MeshFormat``, and its
``$Entities`` / ``$Nodes`` / ``$Elements`` blocks are laid out differently from
MSH 4.1 -- most notably a point entity carries a full 6-double bounding box
rather than 3 coordinates. It must therefore not be parsed with the 4.1 reader.

MSH 4.0 is a read-only legacy input path: sgio writes only 2.2 and 4.1, so this
module deliberately provides no writer. Block parsing is delegated to
``meshio``, which already implements the 4.0 layout correctly; sgio only adds
its own SG cell-data post-processing on top so that a 4.0 file yields the same
mesh IR as any other supported version.
"""

from __future__ import annotations

from meshio.gmsh import _gmsh40 as _meshio_gmsh40

from sgio.core.mesh import SGMesh

from ._common import finalize_sg_cell_data


def read_buffer(f, is_ascii: bool, data_size) -> SGMesh:
    """Read a Gmsh 4.0 mesh from an open binary buffer.

    Parameters
    ----------
    f : file-like
        Buffer opened in binary mode, positioned just after ``$EndMeshFormat``.
    is_ascii : bool
        Whether the file body is ASCII (as opposed to binary).
    data_size : int
        Size in bytes of the file's floating-point/size types.

    Returns
    -------
    SGMesh
        Parsed mesh with SG cell data (``property_id``, local coordinate
        systems, additional rotations) resolved.
    """
    mesh = SGMesh.from_meshio(_meshio_gmsh40.read_buffer(f, is_ascii, data_size))

    finalize_sg_cell_data(mesh.cell_data, mesh.cells)

    # MSH 4.0 has no $SGLayerDef / $SGConfig blocks; keep the attributes the
    # downstream SG conversion expects.
    mesh.sg_layer_defs = {}
    mesh.sg_configs = {}
    return mesh
