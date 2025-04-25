from __future__ import annotations

import logging

import numpy as np
# from meshio._files import is_buffer, open_file
from inpRW import inpRW
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
            cells[cell_block_i][1].append(_elem.data[1:])
            cell_elem_ids[meshio_type].append(_eid)
            eid2cid[_eid] = (cell_block_i, len(cells[cell_block_i][1]) - 1)
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
    logger.debug('eid2cid:')
    for _k, _v in list(eid2cid.items())[:10]:
        logger.debug(f'{_k}: {_v}')
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
        name = _material_block.parameter['name']
        logger.debug(f'name: {name}')

        density = inprw.findKeyword('density', parentBlock=_material_block)
        logger.debug(f'density: {density}')
        density = density[0].data[0][0]
        logger.debug(f'density: {density}')

        elastic = inprw.findKeyword('elastic', parentBlock=_material_block)
        logger.debug(f'elastic: {elastic}')
        elastic_type = elastic[0].parameter['type']
        elastic_constants = []
        for _row in elastic[0].data:
            try:
                elastic_constants.extend(list(map(float, _row)))
            except ValueError:
                pass

        materials[name] = {
            'id': 0,
            'density': float(density),
            'type': elastic_type._value.lower(),
            'elastic': list(map(float, elastic_constants)),
        }

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
    # cell_sections = []
    # """
    # cell_sections = [
    #     {
    #         'material': 'material_name',
    #         'angle': 'angle',
    #         'elset': 'elset_name',
    #         'orientation': 'orientation_name',
    #     }
    # ]
    # """
    used_materials = []
    mocombos = {}
    """
    mocombos = {
        prop_id: [material_id, angle]
    }
    """
    used_orientations = []

    for _section_block in inprw.findKeyword('shell section'):
        params = _section_block.parameter
        logger.debug(f'params: {params}')

        elset_name = params.get('elset')
        logger.debug(f'elset: {elset_name}')

        material_name = params.get('material', None)
        logger.debug(f'material: {material_name}')

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


        # cell_sections.append({
        #     'material': material_name,
        #     'angle': 0,
        #     'elset': elset_name,
        #     'orientation': orient_name,
        # })

    # logger.debug('----------')
    # logger.debug('cell_sections:')
    # logger.debug(cell_sections)
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
        'property_ref_csys': init_cell_data_list(cells, [1, 0, 0, 0, 1, 0]),
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
            cell_data['property_ref_csys'][_cbi][_ci] = _coords

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

