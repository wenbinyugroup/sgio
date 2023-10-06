import copy
import numpy as np

from .sg import StructureGene
# from sgio.model.solid import MaterialProperty
# from sgio.model import CauchyContinuumModel
from sgio.meshio._mesh import Mesh
import sgio.model as smdl

import logging
logger = logging.getLogger(__name__)


def buildSG1D(
    name, layup, sgdb, smdim, mesh_size=0,
    k11=0, k22=0, lame1=1, lame2=1,
    load_cases=[], analysis='', physics=0,
    submodel=0, geo_correct=None, elem_type=5,
    sgdb_map = {},
    ):
    """Preprocessor of 1D SG.

    Parameters
    ----------
    layup : msgpi.materials.Layup
        Layup design.
    material_db : dict
        Material database.

    Returns
    -------
    msgpi.sg.sg.StructureGene
        1D structure gene.
    """

    logger.info('building 1D SG: {}...'.format(name))

    sg = StructureGene(name, 1)
    # sg = mss.StructureGene(name, 1)

    # Design
    # ----------------------------------------------------------------

    # Layup
    nsym = layup.get('symmetry', 0)
    layers = layup['layers']

    # Record used materials and create material-orientation combinations
    mid = 0
    cid = 0
    tt = 0.0  # total thickness
    for layer in layers:
        _lyr_m_name = layer['material']
        # print('_lm_name:', _lyr_m_name)

        try:
            _lyr_ipo = layer['in-plane_rotation']
        except KeyError:
            try:
                _lyr_ipo = layer['in-plane_orientation']
            except KeyError:
                _lyr_ipo = 0

        try:
            _lyr_np = layer['number_of_plies']
        except KeyError:
            _lyr_np = 1
            layer['number_of_plies'] = _lyr_np

        # print(_lyr_np)

        # Check used material-orientation combination first
        try:
            _lyr_m_name = sgdb_map[_lyr_m_name]
        except KeyError:
            pass
        logger.debug('checking material {}...'.format(_lyr_m_name))
        cid = sg.findComboByMaterialOrientation(_lyr_m_name, _lyr_ipo)
        if cid == 0:
            # Not found
            # Check used material
            mid = sg.findMaterialByName(_lyr_m_name)

            if mid == 0:
                # Not found
                mid = len(sg.materials) + 1
                # m = MaterialProperty(_lyr_m_name)
                # m = smdl.MaterialSection(_lyr_m_name)
                # m = mms.MaterialProperty(_lyr_m_name)
                m = smdl.CauchyContinuumModel()
                m.name = _lyr_m_name
                # print(sgdb)
                # mprop = sgdb[_lyr_m_name][0]['property']['md3']
                # mprop = muc.getValueByKey(sgdb[_lyr_m_name][0], 'prop')
                mprop = sgdb[_lyr_m_name][0]['property']['md3']
                # print(f'mprop = {mprop}')

                m.density = float(mprop['density'])
                m.temperature = float(mprop.get('temperature', 0))

                # Constitutive model
                # ------------------
                _isotropy = mprop.get('type', 'isotropic')
                m.set('isotropy', _isotropy)
                # cm = smdl.Cauchy()

                # Elastic property
                # _c = mprop.get('stiffness', [])
                # cm.setElasticProperty(mprop['elasticity'], _isotropy)
                _elastic = mprop.get('elasticity')
                # print(f'_elastic = {_elastic}')
                m.set('elastic', _elastic, input_type=_isotropy)

                # Thermal property
                m.cte = list(map(float, mprop.get('cte', [])))
                m.specific_heat = float(mprop.get('specific_heat', 0))

                # m.constitutive = cm

                # Strength properties
                # -------------------
                m.strength_constants = mprop.get('strength', None)
                m.failure_criterion = mprop.get('failure_criterion', None)
                m.char_len = float(mprop.get('char_len', 0))

                sg.materials[mid] = m

            cid = len(sg.mocombos) + 1
            sg.mocombos[cid] = [mid, _lyr_ipo]
            # sg.prop_elem[cid] = []
        layer['mocombo'] = cid
        lyr_thk = layer['ply_thickness'] * _lyr_np
        # print('lyr_thk =', lyr_thk)
        tt += lyr_thk

    # Symmetry
    for i in range(nsym):
        # print('i =', i)
        # printLayers(layers, 'layers')
        layers[-1]['number_of_plies'] *= 2
        temp = layers[:-1]
        # printLayers(temp, 'temp')
        for layer in temp[::-1]:
            layers.append(copy.deepcopy(layer))
        # printLayers(layers, 'layers')
        tt = tt * 2

    # print('tt =', tt)
    # printLayers(layers, 'layers')
    logger.debug('full layers')
    for layer in layers:
        logger.debug(layer)


    # Global model settings
    # ----------------------------------------------------------------
    sg.smdim = smdim
    sg.model = submodel  # model (0: classical, 1: shear refined)
    sg.trans_element = 1  # Always include element orientation data
    # sg.geo_correct = geo_correct
    sg.initial_curvature = [k11, k22]
    sg.lame_params = [lame1, lame2]

    if smdim == 2:
        sg.omega = 1
    elif smdim == 3:
        sg.omega = tt




    # Analysis settings
    # ----------------------------------------------------------------
    if isinstance(physics, str):
        sg.physics = {
            'elastic': 0,
            'thermoelastic': 1
        }[physics]
    else:
        sg.physics = physics
    # sg.degen_element = 0
    # sg.trans_element = 0
    # sg.nonuniform_temperature = 0




    # Meshing
    # ----------------------------------------------------------------
    min_thk = 0  # minimum layer thickness
    if mesh_size == 0:
        # Use the minimum layer thickness as the mesh size
        for lyr in layers:
            lyr_thk = layer['ply_thickness'] * layer['number_of_plies']
            if min_thk == 0 or min_thk > lyr_thk:
                min_thk = lyr_thk
        mesh_size = min_thk
    pan = 0.0  # Translation of the origin from the midplane

    # nply = len(ld_layer)
    # tthk = thickness * nply
    ht = tt / 2.0
    # print tthk

    # nodes_major = np.array([-ht + pan, ])
    # nid = 1
    glb_orientation = {
        'a': [1, 0, 0],
        'b': [0, 1, 0],
        'c': [0, 0, 0]
    }

    points = []
    cells = []
    point_data = {}
    cell_data = []

    nid1 = 1
    eid = 0
    yprev = -ht - pan
    # sg.nodes[nid1] = [yprev, ]
    points.append([0, 0, yprev])  # First point

    cell_type = 'line{}'.format(elem_type) if elem_type > 2 else 'line'

    for lyr in layers:
        ne = 0
        t = lyr['ply_thickness'] * lyr['number_of_plies']

        _lyr_glo = lyr.get('global_orientation', copy.copy(glb_orientation))

        if mesh_size > 0:
            ne = int(round(t / mesh_size))  # number of element for this layer
        if ne == 0:
            ne += 1
        # lyr['nelem'] = ne
        ns = np.linspace(yprev, yprev+t, ne+1)  # end points of elements

        for i in range(ne):
            _y3 = ns[i+1]
            points.append([0, 0, _y3])
            cells.append([len(points)-2, len(points)-1])
            cell_data.append(lyr['mocombo'])

            # nid2 = nid1 + elem_type - 1
            # sg.nodes[nid2] = [ns[i+1], ]
            eid = eid + 1
            # sg.elements[eid] = [nid1, nid2]

            # sg.elem_prop[eid] = lyr['mocombo']
            # sg.prop_elem[lyr['mocombo']].append(eid)
            # sg.elem_orient[eid] = [_lyr_glo['a'], _lyr_glo['b'], _lyr_glo['c']]
            # sg.elementids1d.append(eid)

            # nid1 = nid2

        yprev = yprev + t

    # Change the order of each element
    if elem_type > 2:
        # for eid in sg.elements.keys():
        for _ei in range(len(cells)):
            _n1i = cells[_ei][0]
            _n2i = cells[_ei][1]
            _y3n1 = points[_n1i][2]
            _y3n2 = points[_n2i][2]
            # nid3 = nid1 + 1
            # sg.elements[eid].append(nid3)
            if elem_type == 4:
                pass
            else:
                _y3q2 = (_y3n1 + _y3n2) / 2.0
                _y3q1 = (_y3n1 + _y3q2) / 2.0
                _y3q3 = (_y3q2 + _y3n2) / 2.0
                if elem_type == 5:
                    # node 3
                    points.append([0, 0, _y3q1])
                    cells[_ei].append(len(points)-1)
                    # node 4
                    points.append([0, 0, _y3q3])
                    cells[_ei].append(len(points)-1)
                    # node 5
                    points.append([0, 0, _y3q2])
                    cells[_ei].append(len(points)-1)
                    # nid = nid + 1
                    # nid5 = nid3 + 1
                    # nid4 = nid5 + 1
                    # sg.nodes[nid3] = [nq1y3, ]
                    # sg.nodes[nid5] = [nq2y3, ]
                    # sg.nodes[nid4] = [nq3y3, ]
                    # sg.elements[eid].append(nid3)
                    # sg.elements[eid].append(nid4)
                    # sg.elements[eid].append(nid5)
                else:
                    # node 3
                    points.append([0, 0, _y3q2])
                    cells[_ei].append(len(points)-1)
                    # sg.nodes[nid3] = [nq2y3, ]

    # sg.summary()

    cells = [(cell_type, cells)]
    cell_data = {'property_id': [cell_data,]}

    sg.mesh = Mesh(
        points, cells,
        point_data=point_data, cell_data=cell_data
    )

    if analysis == 'fi' or analysis == 'fe':
        sg.global_loads = load_cases



    return sg









# TODO
# def generateLayerList(layup_design):
#     """Generate the list of layers from the layup design input
#     """

#     print('layup_design')
#     print(layup_design)

#     layers = []

#     # Layup
#     nsym = layup_design.get('symmetry', 0)
#     # layers = layup_design['layers']

#     # Record used materials and create material-orientation combinations
#     mid = 0
#     cid = 0
#     tt = 0.0  # total thickness
#     for layer in layup_design['layers']:
#         _lyr_m_name = layer['material']
#         # print('_lm_name:', _lyr_m_name)

#         try:
#             _lyr_ipo = layer['in-plane_rotation']
#         except KeyError:
#             try:
#                 _lyr_ipo = layer['in-plane_orientation']
#             except KeyError:
#                 _lyr_ipo = 0

#         try:
#             _lyr_np = layer['number_of_plies']
#         except KeyError:
#             _lyr_np = 1
#             layer['number_of_plies'] = _lyr_np

#         # print(_lyr_np)

#         # Check used material-orientation combination first
#         try:
#             _lyr_m_name = sgdb_map[_lyr_m_name]
#         except KeyError:
#             pass
#         logger.debug('checking material {}...'.format(_lyr_m_name))
#         cid = sg.findComboByMaterialOrientation(_lyr_m_name, _lyr_ipo)
#         if cid == 0:
#             # Not found
#             # Check used material
#             mid = sg.findMaterialByName(_lyr_m_name)

#             if mid == 0:
#                 # Not found
#                 mid = len(sg.materials) + 1
#                 m = MaterialProperty(_lyr_m_name)
#                 # m = mms.MaterialProperty(_lyr_m_name)
#                 # print(sgdb)
#                 # mprop = sgdb[_lyr_m_name][0]['property']['md3']
#                 # mprop = muc.getValueByKey(sgdb[_lyr_m_name][0], 'prop')
#                 mprop = sgdb[_lyr_m_name][0]['property']['md3']
#                 # mprop = mprop['md3']

#                 m.density = float(mprop['density'])

#                 try:
#                     m.stff = mprop['stiffness']
#                 except KeyError:
#                     pass

#                 # Add elastic properties
#                 m.setElasticProperty(mprop['elasticity'], mprop['type'])

#                 # Add strength properties (if any)
#                 try:
#                     m.strength_constants = mprop['strength']
#                 except KeyError:
#                     pass

#                 try:
#                     m.failure_criterion = mprop['failure_criterion']
#                 except KeyError:
#                     pass

#                 try:
#                     m.char_len = float(mprop['char_len'])
#                 except KeyError:
#                     pass

#                 try:
#                     m.cte = list(map(float, mprop['cte']))
#                 except KeyError:
#                     pass

#                 try:
#                     m.specific_heat = float(mprop['specific_heat'])
#                 except KeyError:
#                     pass

#                 sg.materials[mid] = m

#             cid = len(sg.mocombos) + 1
#             sg.mocombos[cid] = [mid, _lyr_ipo]
#             sg.prop_elem[cid] = []
#         layer['mocombo'] = cid
#         lyr_thk = layer['ply_thickness'] * _lyr_np
#         # print('lyr_thk =', lyr_thk)
#         tt += lyr_thk

#     # Symmetry
#     for i in range(nsym):
#         # print('i =', i)
#         # printLayers(layers, 'layers')
#         layers[-1]['number_of_plies'] *= 2
#         temp = layers[:-1]
#         # printLayers(temp, 'temp')
#         for layer in temp[::-1]:
#             layers.append(copy.deepcopy(layer))
#         # printLayers(layers, 'layers')
#         tt = tt * 2

#     return layers
