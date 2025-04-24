from __future__ import annotations

import logging

import numpy as np
# from meshio._files import is_buffer, open_file
from inpRW import inpRW
from meshio import Mesh, CellBlock
from meshio.abaqus._abaqus import (
    abaqus_to_meshio_type,
    )

from sgio.core.sg import StructureGene

logger = logging.getLogger(__name__)

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
    inprw = inpRW(filename)
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




def process_mesh(inprw:inpRW):
    """
    """

    points = []
    for _nid, _node in inprw.nd.items():
        points.append(_node.data[1:])
    points = np.asarray(points)

    # Process cells
    cells = []
    """
    cells = [
        ('type_name', [[node_ids], [node_ids], ...]),
        ...
    ]
    """
    cell_types = []  # Order of types [type_name, ...]
    cell_elem_ids = {}  # Store the oridinal element ids
    """
    cell_elem_ids = {
        'type_name': [elem_ids],
        ...
    }
    """
    cell_sets = {}
    """
    cell_sets = {
        'set_name': [cell_ids],
        ...
    }
    """
    for _elem_block in inprw.findKeyword('element'):
        params = _elem_block.parameter
        logger.debug(f'params: {params}')

        abq_type = params['type']
        meshio_type = abaqus_to_meshio_type[abq_type]
        try:
            cell_block_i = cell_types.index(meshio_type)
        except ValueError:
            cells.append([meshio_type, []])
            cell_types.append(meshio_type)
            cell_elem_ids[meshio_type] = []
            cell_block_i = len(cell_types) - 1

        set_name = params.get('elset', None)
        logger.debug(f'set_name: {set_name}')
        if set_name is not None:
            if set_name not in cell_sets.keys():
                cell_sets[set_name] = []

        elems = _elem_block.data
        for _eid, _elem in elems.items():
            cells[cell_block_i][1].append(_elem.data[1:])
            cell_elem_ids[meshio_type].append(_eid)
            if set_name is not None:
                cell_sets[set_name].append(_eid)

    logger.debug('cells_types:')
    logger.debug(cell_types)
    logger.debug('----------')
    logger.debug('cells:')
    for _cb in cells:
        logger.debug(_cb[0])
        for _i in range(min(10, len(_cb[1]))):
            logger.debug(f'{_cb[1][_i]}')
    logger.debug('----------')
    logger.debug('cell_elem_ids:')
    for _k, _v in cell_elem_ids.items():
        logger.debug(f'{_k}:')
        for _i in range(min(10, len(_v))):
            logger.debug(f'{_v[_i]}')
    logger.debug('----------')
    logger.debug('cell_sets:')
    for _k, _v in cell_sets.items():
        logger.debug(f'{_k}:')
        for _i in range(min(10, len(_v))):
            logger.debug(f'{_v[_i]}')


    for _i in range(len(cell_types)):
        cells[_i] = tuple(cells[_i])


    cell_data = {
        'element_id': []
    }
    for _ct in cell_types:
        cell_data['element_id'].append(cell_elem_ids[_ct])
    logger.debug('----------')
    logger.debug('cell_data:')
    for _k, _v in cell_data.items():
        logger.debug(f'{_k}:')
        for _cb in _v:
            _ = []
            for _i in range(min(10, len(_cb))):
                _.append(str(_cb[_i]).strip())
            logger.debug(', '.join(_))


    mesh = Mesh(
        points=points,
        cells=cells,
        cell_sets=cell_sets,
        cell_data=cell_data,
    )

    return mesh

