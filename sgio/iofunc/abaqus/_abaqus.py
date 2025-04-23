from __future__ import annotations

import logging

import inpRW
# from meshio._files import is_buffer, open_file
from meshio import Mesh, CellBlock
from meshio.abaqus._abaqus import (
    abaqus_to_meshio_type,
    )

from sgio.core.sg import StructureGene

abaqus_to_meshio_type.update({
    "WARP2D4": "quad",
    "WARPF2D4": "quad",
    "WARPF2D8": "quad8",
    "WARP2D3": "triangle",
    "WARPF2D3": "triangle",
    "WARPF2D6": "triangle6",
})
meshio_to_abaqus_type = {v: k for k, v in abaqus_to_meshio_type.items()}



# ====================================================================
# Readers
# ====================================================================


# Read input
# ----------

def read(filename, **kwargs):
    """Reads a Abaqus inp file."""

    # Parse input file
    inprw = inpRW.inpRW(filename)
    inprw.parse()

    # Process parsed data

    sg = StructureGene()
    sg.sgdim = kwargs['sgdim']

    model = kwargs.get('model')
    if isinstance(model, int):
        smdim = kwargs.get('model')
        _submodel = model
    elif isinstance(model, str):
        if model.upper()[:2] == 'SD':
            smdim = 3
        elif model.upper()[:2] == 'PL':
            smdim = 2
        elif model.upper()[:2] == 'BM':
            smdim = 1
        _submodel = int(model[2]) - 1

    sg.smdim = smdim
    sg.model = _submodel


    # Process mesh
    mesh = process_mesh(inprw)
    print(mesh)
    sg.mesh = mesh


    # Process materials


    # Process material-orientation combinations

    return sg




def process_mesh(inprw):
    """
    """

    points = []
    cells = []


    mesh = Mesh(
        points=points,
        cells=cells,
    )

    return mesh

