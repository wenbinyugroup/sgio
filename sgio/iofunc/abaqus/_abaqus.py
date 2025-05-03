from __future__ import annotations

import logging

import numpy as np
# from meshio._files import is_buffer, open_file
from inpRW import inpRW
from misc_functions import rsl
from meshio import Mesh, CellBlock
from meshio.abaqus._abaqus import (
    abaqus_to_meshio_type,
    )

import sgio.model as smdl
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
    mesh, materials, mocombos = process_mesh(inprw)
    print(mesh)
    sg.mesh = mesh


    # Process materials
    for _mname, _mdata in materials.items():
        _mid = _mdata['id']
        if _mid == 0:  # Skip not used materials
            continue

        m = smdl.CauchyContinuumModel(_mname)
        m.temperature = _mdata.get('temperature', 0)
        m.set('density', _mdata.get('density', 0))

        _type = _mdata['type']
        _elastic = _mdata['elastic']
        logger.debug(f'{_type}: {_elastic}')
        if _type == 'isotropic':
            m.set('isotropy', 0)
            m.set('elastic', _elastic)
        elif _type == 'engineering constants':
            m.set('isotropy', 1)
            _e1, _e2, _e3 = _elastic[:3]
            _g12, _g13, _g23 = _elastic[6:9]
            _nu12, _nu13, _nu23 = _elastic[3:6]
            m.set(
                'elastic',
                [_e1, _e2, _e3, _g12, _g13, _g23, _nu12, _nu13, _nu23],
                input_type='engineering')

        elif _type == 'anisotropic':
            _c = [
                [_elastic[0], _elastic[1], _elastic[3], _elastic[6], _elastic[10], _elastic[15]],
                [_elastic[1], _elastic[2], _elastic[4], _elastic[7], _elastic[11], _elastic[16]],
                [_elastic[3], _elastic[4], _elastic[5], _elastic[8], _elastic[12], _elastic[17]],
                [_elastic[6], _elastic[7], _elastic[8], _elastic[9], _elastic[13], _elastic[18]],
                [_elastic[10], _elastic[11], _elastic[12], _elastic[13], _elastic[14], _elastic[19]],
                [_elastic[15], _elastic[16], _elastic[17], _elastic[18], _elastic[19], _elastic[20]],
            ]
            m.set('isotropy', 2)
            m.set('elastic', _c, input_type='stiffness')

        sg.materials[_mid] = m

    # Process material-orientation combinations
    sg.mocombos = mocombos

    return sg




def init_cell_data_list(cells, default_value=None):
    """
    """
    cell_data = []
    for _cell_block in cells:
        cell_data.append([default_value,] * len(_cell_block[1]))
    return cell_data




def process_mesh(inprw:inpRW):
    """
    """

    points = []
    for _nid, _node in inprw.nd.items():
        # points.append([x._evalDecimal for x in _node.data[1:]])
        points.append(list(map(float, _node.data[1:])))
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
    eid2cid = {}
    """
    eid2cid = {
        elem_id: (cell_block_i, cell_i),
        ...
    }
    """
    cell_sets = {}
    """
    cell_sets = {
        'set_name': [elem_ids],
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
            _nids = [i - 1 for i in _elem.data[1:]]  # Convert to 0-based
            cells[cell_block_i][1].append(_nids)
            cell_elem_ids[meshio_type].append(_eid)  # Store the original element id
            eid2cid[_eid] = (cell_block_i, len(cells[cell_block_i][1]) - 1)  # Store the mapping from original element id to cell block index and cell index
            if set_name is not None:
                cell_sets[set_name].append(_eid)  # Store the element ids in the cell set

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
    logger.debug('eid2cid:')
    for _k, _v in list(eid2cid.items())[:10]:
        logger.debug(f'{_k}: {_v}')


    # Process sets
    for _set_block in inprw.findKeyword('elset'):
        params = _set_block.parameter
        logger.debug(f'params: {params}')

        set_name = params['elset']._value
        logger.debug(f'set_name: {set_name}')

        generate = params.get('generate', None)
        logger.debug(f'generate: {generate}')

        if set_name not in cell_sets.keys():
            cell_sets[set_name] = []

        if generate is not None:
            _eid_start, _eid_end, _eid_inc = _set_block.data[0]
            for _eid in range(_eid_start, _eid_end + 1, _eid_inc):
                cell_sets[set_name].append(_eid)
        else:
            for _row in _set_block.data:
                cell_sets[set_name].extend(_row)

    logger.debug('----------')
    logger.debug('cell_sets:')
    for _k, _v in cell_sets.items():
        logger.debug(f'{_k}:')
        for _i in range(min(10, len(_v))):
            logger.debug(f'{_v[_i]}')


    # Process distributions and orientations
    distrs = {}
    """
    distrs = {
        'distr_name': {
            elem_id: [ax, ay, az, bx, by, bz],
            ...
        },
        ...
    }
    """
    for _distr_block in inprw.findKeyword('distribution'):
        params = _distr_block.parameter
        logger.debug(f'params: {params}')

        distr_name = params['name']._value
        logger.debug(f'distr_name: {distr_name}')
        if distr_name is not None:
            if distr_name not in distrs.keys():
                distrs[distr_name] = {}

        for _i in range(1, len(_distr_block.data)):
            _elem_id = _distr_block.data[_i][0]
            _distr = _distr_block.data[_i][1:]
            distrs[distr_name][_elem_id] = list(map(float, _distr))
            # distrs[distr_name][_elem_id] = [x._evalDecimal for x in _distr]

    logger.debug('----------')
    logger.debug('distrs:')
    for _k, _v in distrs.items():
        logger.debug('')
        logger.debug(f'{_k}:')
        _ = 0
        for _eid, _coords in _v.items():
            _ += 1
            logger.debug(f'{_eid}: {_coords}')
            if _ >= 10:
                break

    orients = {}
    """
    orients = {
        'orientation_name': 'distr_name',
        ...
    }
    """
    for _orient_block in inprw.findKeyword('orientation'):
        params = _orient_block.parameter
        logger.debug(f'params: {params}')

        orient_name = params['name']._value
        logger.debug(f'orient_name: {orient_name}')

        distr_name = _orient_block.data[0][0]._value

        orients[orient_name] = distr_name
    logger.debug('----------')
    logger.debug(orients)


    # Process materials
    materials = {}
    """
    materials = {
        'material_name': {
            'id': 'material_id',
            'density': 'density',
            'type': 'material_type',
            'elastic': [],
        },
        ...
    }
    """
    for _material_block in inprw.findKeyword('material'):
        process_material(_material_block, inprw, materials)


    logger.debug('----------')
    logger.debug('materials:')
    logger.debug(materials)

    # Process sections
    cell_prop_ids = {}
    """
    cell_prop_ids = {
        prop_id: [elem_ids],
        ...
    }
    """

    used_materials = []
    mocombos = {}
    """
    mocombos = {
        prop_id: [material_id, angle]
    }
    """
    used_orientations = []

    for _section_block in inprw.findKeyword('solid section'):
        process_section(
            _section_block, materials, mocombos, cell_sets, cell_prop_ids,
            used_materials, used_orientations)

    for _section_block in inprw.findKeyword('shell section'):
        process_section(
            _section_block, materials, mocombos, cell_sets, cell_prop_ids,
            used_materials, used_orientations)


    logger.debug('----------')
    logger.debug('mocombos:')
    logger.debug(mocombos)
    logger.debug('----------')
    logger.debug('cell_prop_ids:')
    for _k, _v in cell_prop_ids.items():
        logger.debug(f'{_k}: {_v[:10]}')


    for _i in range(len(cell_types)):
        cells[_i] = tuple(cells[_i])


    cell_data = {
        'element_id': [],
        'property_id': init_cell_data_list(cells, None),
        'property_ref_csys': init_cell_data_list(cells, [1, 0, 0, 0, 1, 0, 0, 0, 0]),
    }

    # Convert element id to cell data
    for _ct in cell_types:
        cell_data['element_id'].append(cell_elem_ids[_ct])

    # Convert property id to cell data
    for _prop_id, _elem_ids in cell_prop_ids.items():
        for _eid in _elem_ids:
            _cbi, _ci = eid2cid[_eid]
            cell_data['property_id'][_cbi][_ci] = _prop_id

    # Convert orientation to cell data
    # print(distrs)
    for _orient_name in used_orientations:
        # logger.debug(f'orient_name: {_orient_name}')
        # logger.debug(orients.keys())
        _distr_name = orients[_orient_name]
        # logger.debug('distr_name')
        # logger.debug(_distr_name)
        # logger.debug('distrs')
        # logger.debug(distrs.keys())
        _distr = distrs[_distr_name]
        # logger.debug('_distr')
        # logger.debug(_distr)
        for _eid, _coords in distrs[_distr_name].items():
            _cbi, _ci = eid2cid[_eid]
            cell_data['property_ref_csys'][_cbi][_ci] = _coords + [0, 0, 0]

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

    return mesh, materials, mocombos




def process_material(_material_block, inprw, materials):
    """
    """
    name = _material_block.parameter['name']._value
    logger.debug(f'name: {name}')

    density = inprw.findKeyword('density', parentBlock=_material_block)
    if density:
        logger.debug(f'density: {density}')
        density = float(density[0].data[0][0])
        logger.debug(f'density: {density}')
    else:
        density = 0.0

    elastic = inprw.findKeyword('elastic', parentBlock=_material_block)
    logger.debug(f'elastic: {elastic}')

    try:
        elastic_type = elastic[0].parameter['type']._value.lower()
    except KeyError:
        elastic_type = 'isotropic'

    elastic_constants = []
    logger.debug(f'elastic[0].data: {elastic[0].data}')
    for _row in elastic[0].data:
        for _v in _row:
            try:
                elastic_constants.append(float(_v))
            except ValueError:
                pass

    materials[name] = {
        'id': 0,
        'density': density,
        'type': elastic_type,
        'elastic': list(map(float, elastic_constants)),
    }




def process_section(
    _section_block, materials, mocombos, cell_sets, cell_prop_ids,
    used_materials, used_orientations):
    """
    """
    params = _section_block.parameter
    logger.debug(f'params: {params}')

    elset_name = params.get('elset')
    logger.debug(f'elset: {elset_name}')

    material_name = params.get('material', None)
    logger.debug(f'material: {material_name}')
    if material_name is None:
        if 'composite' in params.keys():
            material_name = _section_block.data[0][2]
    material_name = material_name._value

    orient_name = params.get('orientation', None)
    logger.debug(f'orient_name: {orient_name}')

    if orient_name is not None:
        if orient_name not in used_orientations:
            used_orientations.append(orient_name._value)

    angle = 0
    try:
        angle = float(_section_block.data[-2])
    except ValueError:
        pass
    except IndexError:
        pass

    if material_name not in used_materials:
        used_materials.append(material_name)
        materials[material_name]['id'] = len(used_materials)

    prop_id = 0
    for _k, _v in mocombos.items():
        if _v[0] == material_name and _v[1] == angle:
            prop_id = _k
            break

    if prop_id == 0:  # New material-angle combination
        prop_id = len(mocombos) + 1
        mat_id = materials[material_name]['id']
        mocombos[prop_id] = [mat_id, angle]
        cell_prop_ids[prop_id] = []

    cell_prop_ids[prop_id].extend(cell_sets[elset_name])
