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
    file, mesh, format_version, float_fmt, sgdim,
    mesh_only, binary,
    **kwargs):
    """
    """
    logger.debug(locals())

    if format_version == "":
        format_version = "4.1"

    if format_version == "2.2":
        _gmsh22.write_buffer(file, mesh, float_fmt=float_fmt, binary=binary)
    # elif format_version == "4.0":
    #     _gmsh40.write_buffer(file, mesh, format_version=format_version)
    elif format_version == "4.1":
        # handle gmsh:dim_tags
        # mesh.point_data['gmsh:dim_tags'] = np.array([[sgdim, 0]])
        mesh.point_data['gmsh:dim_tags'] = np.array([[sgdim, 1] for i in range(len(mesh.points))])
        # mesh.cell_data['gmsh:geometrical'] = np.array([[i,] for i in range(len(mesh.cells))])
        mesh.cell_data['gmsh:geometrical'] = [[1,],] * len(mesh.cells)
        _gmsh41.write_buffer(file, mesh, float_fmt, mesh_only, binary)
