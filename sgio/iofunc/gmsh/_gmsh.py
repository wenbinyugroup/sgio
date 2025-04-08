from __future__ import annotations

from . import _gmsh22
# from . import _gmsh40
from . import _gmsh41


def read_buffer(file, format_version="4.1", **kwargs):
    ...
#     return mgmsh.read_buffer(file, format_version=format_version)


def write_buffer(file, mesh, format_version="4.1", float_fmt=".16e", binary=False, **kwargs):
    if format_version == "2.2":
        _gmsh22.write_buffer(file, mesh, float_fmt=float_fmt, binary=binary)
    # elif format_version == "4.0":
    #     _gmsh40.write_buffer(file, mesh, format_version=format_version)
    elif format_version == "4.1":
        _gmsh41.write_buffer(file, mesh, float_fmt=float_fmt, binary=binary)
