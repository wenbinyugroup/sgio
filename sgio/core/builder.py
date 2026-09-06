from __future__ import annotations

import copy
import logging

import numpy as np

import sgio.model as smdl
from sgio.core.mesh import SGMesh
from sgio.core.sg import StructureGene

logger = logging.getLogger(__name__)


def build_sg_1d(
    name, layup, sgdb, model, mesh_size=0,
    k11=0, k22=0, lame1=1, lame2=1,
    load_cases=[], analysis='', physics=0,
    geo_correct=None, elem_type=5,
    sgdb_map = {},
    ):
    """Build a 1D structure gene

    Parameters
    ----------
    name : str
        Name of the structure gene
    layup : dict
        Layup design
    sgdb : dict
        Material database
    smdim : int
        Spatial dimension (2 or 3)
    mesh_size : float
        Mesh size
    k11 : float
        Curvature in the 1-direction
    k22 : float
        Curvature in the 2-direction
    lame1 : float
        Lame constant 1
    lame2 : float
        Lame constant 2
    load_cases : list
        List of load cases
    analysis : str
        Analysis type
    physics : int
        Physics type
    submodel : int
        Submodel type
    geo_correct : dict
        Geometric correction
    elem_type : int
        Element type
    sgdb_map : dict
        Material database map

    Returns
    -------
    sg : StructureGene
        Structure gene
    """

    # print(f'building 1D SG: {name}...')
    logger.debug(f'building 1D SG: {name}...')

    sg = StructureGene(name, 1)

    # Design
    # ----------------------------------------------------------------

    # Generate complete layup data from design inputs
    layers = generate_layer_list(layup)
    # nsym = layup.get('symmetry', 0)
    # layers = layup['layers']
    # print(f'layers: {layers}')
    logger.debug(layers)

    # Record used materials and create material-orientation combinations
    mid = 0
    cid = 0
    tt = 0.0  # total thickness
    for layer in layers:
        _lyr_m_name = layer['material']
        _lyr_ply_thk = layer['ply_thickness']
        _lyr_ipo = layer['in-plane_rotation']
        _lyr_np = layer['number_of_plies']

        # print(_lyr_np)

        # Check used material-orientation combination first
        _lyr_m_name = sgdb_map.get(_lyr_m_name, _lyr_m_name)

        logger.debug(f'checking material {_lyr_m_name}...')

        cid = sg.find_combo_by_material_orientation(_lyr_m_name, _lyr_ipo)
        if cid is None:
            # Combo not found - check if material exists
            if _lyr_m_name not in sg.materials:
                # Material not found - add it
                mprop = sgdb[f'{_lyr_m_name}']

                if isinstance(mprop, smdl.CauchyContinuumModel):
                    m = mprop
                else:
                    m = add_material(_lyr_m_name, mprop['property'])

                sg.materials[_lyr_m_name] = m

            section = sg.add_section(
                name=f"section_{len(sg.sections) + 1}",
                material=_lyr_m_name,
                orientation=_lyr_ipo,
            )
            cid = int(section.property_id)
            
        layer['mocombo'] = cid
        lyr_thk = _lyr_ply_thk * _lyr_np
        # print('lyr_thk =', lyr_thk)
        tt += lyr_thk


    # Global model settings
    # ----------------------------------------------------------------
    sg.smdim = smdl.getModelDim(model)
    sg.analysis_config.model = int(model[2:]) - 1  # model (0: classical, 1: shear refined)
    sg.trans_element = 1  # Always include element orientation data
    sg.initial_curvature = [k11, k22]
    sg.lame_params = [lame1, lame2]

    if sg.smdim == 2:
        sg.omega = 1
    elif sg.smdim == 3:
        sg.omega = tt




    # Analysis settings
    # ----------------------------------------------------------------
    if isinstance(physics, str):
        sg.analysis_config.physics = {
            'elastic': 0,
            'thermoelastic': 1
        }[physics]
    else:
        sg.analysis_config.physics = physics




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

    ht = tt / 2.0

    points = []
    cells = []
    point_data = {}
    cell_data = []

    yprev = -ht - pan
    points.append([0, 0, yprev])  # First point

    cell_type = 'line{}'.format(elem_type) if elem_type > 2 else 'line'

    for lyr in layers:
        ne = 0
        t = lyr['ply_thickness'] * lyr['number_of_plies']

        if mesh_size > 0:
            ne = int(round(t / mesh_size))  # number of element for this layer
        if ne == 0:
            ne += 1
        ns = np.linspace(yprev, yprev+t, ne+1)  # end points of elements

        for i in range(ne):
            _y3 = ns[i+1]
            points.append([0, 0, _y3])
            cells.append([len(points)-2, len(points)-1])
            cell_data.append(lyr['mocombo'])

        yprev = yprev + t

    # Change the order of each element
    if elem_type > 2:
        for _ei in range(len(cells)):
            _n1i = cells[_ei][0]
            _n2i = cells[_ei][1]
            _y3n1 = points[_n1i][2]
            _y3n2 = points[_n2i][2]
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
                else:
                    # node 3
                    points.append([0, 0, _y3q2])
                    cells[_ei].append(len(points)-1)

    cells = [(cell_type, cells)]
    cell_data = {'property_id': [cell_data,]}

    sg.mesh = SGMesh(
        points, cells,
        point_data=point_data, cell_data=cell_data
    )

    if analysis == 'fi' or analysis == 'fe':
        sg.global_loads = load_cases



    return sg









def generate_layer_list(layup_design):
    """Generate the list of layers from the layup design input
    """

    logger.debug('generating layer list...')

    logger.debug('layup_design')
    logger.debug(layup_design)

    layers = []

    nsym = layup_design.get('symmetry', 0)

    # Record used materials and create material-orientation combinations
    # tt = 0.0  # total thickness
    for layer_design in layup_design['layers']:
        layer = {}

        _lyr_m_name = layer_design['material']
        layer['material'] = _lyr_m_name

        _lyr_ply_thk = layer_design['ply_thickness']
        layer['ply_thickness'] = _lyr_ply_thk

        _lyr_ipo = layer_design.get(
            'in-plane_rotation', layer_design.get('in-plane_orientation', 0))
        layer['in-plane_rotation'] = _lyr_ipo

        _lyr_np = layer_design.get('number_of_plies', 1)
        layer['number_of_plies'] = _lyr_np

        # print(_lyr_np)

        # layer['mocombo'] = cid
        # lyr_thk = layer['ply_thickness'] * _lyr_np
        # print('lyr_thk =', lyr_thk)
        # tt += lyr_thk
        if _lyr_np > 0:
            layers.append(layer)

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
        # tt = tt * 2

    return layers









def add_material(mname, mprop):
    """
    """

    m = smdl.CauchyContinuumModel()
    m.name = mname

    # mprop = mprop['property']

    # m.density = float(mprop['density'])
    _density = float(mprop['density'])
    m.density = _density
    m.temperature = float(mprop.get('temperature', 0))

    # Constitutive model
    # ------------------
    _isotropy = mprop.get('type', 'isotropic')
    m.set_isotropy(_isotropy)

    # Elastic property
    _elastic = mprop.get('elasticity')
    m.set_elastic(_elastic, input_type=_isotropy)

    # Thermal property
    _cte = list(map(float, mprop.get('cte', [])))
    if _cte:  # Only set if non-empty (validator requires None or 6 components)
        m.cte = _cte
    _specific_heat = float(mprop.get('specific_heat', 0))
    m.specific_heat = _specific_heat

    # Strength properties
    # -------------------
    m.failure_criterion = mprop.get('failure_criterion', 0)

    _strength_constants = list(map(float, mprop.get('strength', [])))
    # print('strength_constants:', _strength_constants)
    m.set_strength_constants(_strength_constants)
    _char_len = float(mprop.get('char_len', 0))
    m.char_len = _char_len

    return m
