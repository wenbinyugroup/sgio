from __future__ import annotations

import logging

import numpy as np

from . import _gmsh22
# from . import _gmsh40
from . import _gmsh41

logger = logging.getLogger(__name__)

def read_buffer(file, format_version="4.1", **kwargs):
    ...
#     return mgmsh.read_buffer(file, format_version=format_version)


def write_buffer(
<<<<<<< HEAD
    file, mesh, format_version="4.1", float_fmt=".16e", sgdim=3,
    mesh_only=False, binary=False,
    **kwargs):
    """
    """
    logger.debug(locals())

    if format_version == "":
        format_version = "4.1"

=======
    file, mesh, format_version="4.1", float_fmt=".16e",
    binary=False, sgdim=3, **kwargs):
    logger.debug('writing gmsh buffer...')
    logger.debug(locals())

>>>>>>> dev
    if format_version == "2.2":
        _gmsh22.write_buffer(file, mesh, float_fmt=float_fmt, binary=binary)
    # elif format_version == "4.0":
    #     _gmsh40.write_buffer(file, mesh, format_version=format_version)
    elif format_version == "4.1":
        # handle gmsh:dim_tags
        # mesh.point_data['gmsh:dim_tags'] = np.array([[sgdim, 0]])
        mesh.point_data['gmsh:dim_tags'] = np.array([[sgdim, 1] for i in range(len(mesh.points))])
        mesh.cell_data['gmsh:geometrical'] = np.array([[i+1,] for i in range(len(mesh.cells))])
        _gmsh41.write_buffer(file, mesh, float_fmt=float_fmt, mesh_only=mesh_only, binary=binary)
