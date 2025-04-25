from __future__ import annotations

import numpy as np
from meshio.gmsh.common import (
    c_int,
    c_double,
    _fast_forward_over_blank_lines,
    _fast_forward_to_end_block,
    _gmsh_to_meshio_order,
    _gmsh_to_meshio_type,
    _meshio_to_gmsh_order,
    _meshio_to_gmsh_type,
    _read_data,
    _read_physical_names,
    _write_physical_names,
)

from sgio.iofunc._meshio import (
    WriteError
)

def _write_data(fh, tag, name, data, binary):
    if binary:
        fh.write(f"${tag}\n".encode())
    else:
        fh.write(f"${tag}\n")
    # <http://gmsh.info/doc/texinfo/gmsh.html>:
    # > Number of string tags.
    # > gives the number of string tags that follow. By default the first
    # > string-tag is interpreted as the name of the post-processing view and
    # > the second as the name of the interpolation scheme. The interpolation
    # > scheme is provided in the $InterpolationScheme section (see below).
    if binary:
        fh.write(f"{1}\n".encode())
        fh.write(f'"{name}"\n'.encode())
        fh.write(f"{1}\n".encode())
        fh.write(f"{0.0}\n".encode())
        # three integer tags:
        fh.write(f"{3}\n".encode())
        # time step
        fh.write(f"{0}\n".encode())
    else:
        fh.write(f"{1}\n")
        fh.write(f'"{name}"\n')
        fh.write(f"{1}\n")
        fh.write(f"{0.0}\n")
        # three integer tags:
        fh.write(f"{3}\n")
        # time step
        fh.write(f"{0}\n")

    # number of components
    num_components = data.shape[1] if len(data.shape) > 1 else 1
    if num_components not in [1, 3, 9]:
        raise WriteError("Gmsh only permits 1, 3, or 9 components per data field.")

    # Cut off the last dimension in case it's 1. This avoids problems with
    # writing the data.
    if len(data.shape) > 1 and data.shape[1] == 1:
        data = data[:, 0]

    if binary:
        fh.write(f"{num_components}\n".encode())
        # num data items
        fh.write(f"{data.shape[0]}\n".encode())
        # actually write the data
        if num_components == 1:
            dtype = [("index", c_int), ("data", c_double)]
        else:
            dtype = [("index", c_int), ("data", c_double, num_components)]
        tmp = np.empty(len(data), dtype=dtype)
        tmp["index"] = 1 + np.arange(len(data))
        tmp["data"] = data
        tmp.tofile(fh)
        fh.write(b"\n")
        fh.write(f"$End{tag}\n".encode())
    else:
        fh.write(f"{num_components}\n")
        # num data items
        fh.write(f"{data.shape[0]}\n")
        # actually write the data
        fmt = " ".join(["{}"] + ["{!r}"] * num_components) + "\n"
        # TODO unify
        if num_components == 1:
            for k, x in enumerate(data.tolist()):
                fh.write(fmt.format(k + 1, x))
        else:
            for k, x in enumerate(data.tolist()):
                fh.write(fmt.format(k + 1, *x))
        fh.write(f"$End{tag}\n")

