from __future__ import annotations

import logging

import sgio.model as smdl
import sgio.utils as sutl
from sgio.core.sg import StructureGene
from ._mesh import (
    read_buffer,
    write_buffer,
)


logger = logging.getLogger(__name__)


def _readHeader(file, format_version:str, smdim:int):
    """
    """

    logger.debug('reading header...')

    configs = {}

    if smdim == 1:
        line = sutl.readNextNonEmptyLine(file)
        configs['model'] = int(line.split()[0])
        line = sutl.readNextNonEmptyLine(file)
        configs['curvature'] = list(map(float, line.split()[:3]))
        line = sutl.readNextNonEmptyLine(file)
        configs['oblique'] = list(map(float, line.split()[:2]))
    elif smdim == 2:
        line = sutl.readNextNonEmptyLine(file)
        configs['model'] = int(line.split()[0])
        line = sutl.readNextNonEmptyLine(file)
        configs['curvature'] = list(map(float, line.split()[:2]))
        if format_version >= '2.2':
            line = sutl.readNextNonEmptyLine(file)
            configs['lame'] = list(map(float, line.split()[:2]))

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['physics'] = int(line[0])
    configs['ndim_degen_elem'] = int(line[1])
    configs['use_elem_local_orient'] = int(line[2])
    configs['is_temp_nonuniform'] = int(line[3])
    if format_version >= '2.2':
        configs['force_flag'] = int(line[4])
        configs['steer_flag'] = int(line[5])

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['sgdim'] = int(line[0])
    configs['num_nodes'] = int(line[1])
    configs['num_elements'] = int(line[2])
    configs['num_materials'] = int(line[3])
    configs['num_slavenodes'] = int(line[4])
    configs['num_mat_angle3_comb'] = int(line[5])

    return configs




def _readMesh(file, sgdim:int, nnode:int, nelem:int, read_local_frame):
    """
    """

    logger.debug('reading mesh...')
    logger.debug(locals())

    mesh = read_buffer(
        file,
        sgdim=sgdim, nnode=nnode, nelem=nelem, read_local_frame=read_local_frame
    )

    return mesh




def _readMaterialRotationCombinations(file, ncomb):
    """
    """

    logger.debug('reading combinations of material and in-plane rotations...')

    combinations = {}

    counter = 0
    while counter < ncomb:
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()

        line = line.split()
        comb_id = int(line[0])
        mate_id = int(line[1])
        ip_ratation = float(line[2])

        combinations[comb_id] = [mate_id, ip_ratation]

        counter += 1

    return combinations




def _readMaterials(file, nmate:int, physics:int):
    """
    """

    logger.debug('reading materials...')

    materials = {}

    counter = 0
    while counter < nmate:
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()

        line = line.split()

        # Read material id, isotropy
        mate_id, isotropy, ntemp = list(map(int, line))

        material = _readMaterial(file, isotropy, ntemp, physics)

        materials[mate_id] = material

        counter += 1

    return materials




def _readMaterial(file, isotropy:int, ntemp:int=1, physics:int=0):
    """
    """

    # mp = smdl.MaterialProperty()
    # mp = smdl.MaterialSection()
    mp = smdl.CauchyContinuumModel()
    # mp.isotropy = isotropy
    mp.set('isotropy', isotropy)

    temp_counter = 0
    while temp_counter < ntemp:

        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()
        line = line.split()
        temperature, density = list(map(float, line))
        mp.temperature = temperature

        # Read conductivity properties

        # Read elastic properties
        elastic_props = _readElasticProperty(file, isotropy)
        mp.setElastic(elastic_props, isotropy)

        # mp.density = density
        mp.set('density', density)

        # Read thermal properties
        if physics in [1, 4, 6]:
            cte, specific_heat = _readThermalProperty(file, isotropy)
            mp.set('cte', cte)
            mp.set('specific_heat', specific_heat)

        temp_counter += 1

    return mp




def _readElasticProperty(file, isotropy:int):
    """
    """

    constants = []

    if isotropy == 0:
        nrow = 1
    elif isotropy == 1:
        nrow = 3
    elif isotropy == 2:
        nrow = 6

    for i in range(nrow):
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()
        constants.extend(list(map(float, line.split())))

    return constants




def _readThermalProperty(file, isotropy:int):
    """
    """
    cte = []
    specific_heat = 0

    line = sutl.readNextNonEmptyLine(file)
    line = list(map(float, line.split()))

    if isotropy == 0:
        cte = line[:1]
        specific_heat = line[1]
    elif isotropy == 1:
        cte = line[:3]
        specific_heat = line[3]
    elif isotropy == 2:
        cte = line[:6]
        specific_heat = line[6]

    return cte, specific_heat























def writeInputBuffer(
    sg, file, analysis, physics, model_space,
    sfi:str='8d', sff:str='20.12e', version=None):
    """
    """

    logger.debug(f'writing sg input...')

    # print(sg)

    ssff = '{:' + sff + '}'
    # if not version is None:
    #     sg.version = sutl.Version(version)
    sg.version = version

    logger.debug('format version: {}'.format(sg.version))

    _writeHeader(sg, file, sfi, sff, version)

    _writeMesh(
        mesh=sg.mesh,
        file=file,
        sgdim=sg.sgdim,
        model_space=model_space,
        int_fmt=sfi, float_fmt=sff
        )

    _writeMOCombos(sg, file, sfi, sff)

    _writeMaterials(
        dict_materials=sg.materials,
        file=file,
        analysis=analysis,
        physics=physics,
        sfi=sfi,
        sff=sff
        )

    file.write((ssff + '\n').format(sg.omega))

    return









def writeInputBufferGlobal(
    file, model, analysis, physics, load_type=0,
    macro_responses:list[smdl.StateCase]=[],
    dict_materials={},
    sfi:str='8d', sff:str='20.12e'
    ):

    # with open(fn, 'w') as file:
    if analysis == 'd' or analysis == 'l':
        # _writeInputDisplacements(sg, file, sff)
        _response = macro_responses[0]

        _disp = _response.displacement
        if _disp is None:
            _disp = [0, 0, 0]
        else:
            _disp = _disp.data

        _rot = _response.rotation
        if _rot is None:
            _rot = [[1,0,0],[0,1,0],[0,0,1]]
        else:
            _rot = _rot.data

        _writeDisplacementRotation(
            file=file,
            displacement=_disp,
            rotation=_rot,
            sff=sff
        )

    elif analysis.startswith('f'):
        # _writeInputMaterialStrength(sg, file, sfi, sff)
        _writeMaterials(
            dict_materials=dict_materials,
            file=file,
            analysis=analysis,
            physics=physics,
            sfi=sfi,
            sff=sff
            )

    sutl.writeFormatIntegers(file, [load_type, ], sfi)

    if analysis != 'f':
        # _writeInputLoads(sg, file, sfi, sff)
        for _i, _response in enumerate(macro_responses):
            _writeLoad(
                file=file,
                macro_response=_response,
                model=model,
                sff=sff
            )









def _writeMesh(mesh, file, sgdim, model_space, int_fmt, float_fmt):
    """
    """
    logger.debug('writing mesh...')

    write_buffer(
        file, mesh, sgdim=sgdim, model_space=model_space,
        int_fmt=int_fmt, float_fmt=float_fmt)

    return









def _writeMOCombos(sg, file, sfi, sff):
    ssfi = '{:' + sfi + '}'
    ssff = '{:' + sff + '}'
    count = 0
    for cid, combo in sg.mocombos.items():
        # print(f'cid: {cid}, combo: {combo}')
        count += 1
        file.write((ssfi + ssfi + ssff).format(cid, combo[0], combo[1]))
        if count == 1:
            file.write('  # combination id, material id, in-plane rotation angle')
        file.write('\n')
    file.write('\n')
    return









def _writeMaterial(
    mid:int, material:smdl.CauchyContinuumModel, file,
    analysis, physics,
    sfi:str='8d', sff:str='20.12e'):
    """
    """

    # logger.debug('writing materials...')

    # counter = 0
    # for mid, m in sg.materials.items():

    # print('writing material {}'.format(mid))

    # print(material)

    # cm = m.constitutive

    # if m.stff:
    #     anisotropy = 2
    # else:
    anisotropy = material.get('isotropy')

    if analysis == 'h':

        sutl.writeFormatIntegers(file, (mid, anisotropy, 1), sfi, newline=False)
        file.write('  # material id, anisotropy, ntemp\n')

        sutl.writeFormatFloats(
            file, (material.get('temperature'), material.get('density')), sff)

        # Write elastic properties
        if anisotropy == 0:
            sutl.writeFormatFloats(
                file, [material.get('e1'), material.get('nu12')], sff)

        elif anisotropy == 1:
            sutl.writeFormatFloats(
                file, [material.get('e1'), material.get('e2'), material.get('e3')], sff)
            sutl.writeFormatFloats(
                file, [material.get('g12'), material.get('g13'), material.get('g23')], sff)
            sutl.writeFormatFloats(
                file, [material.get('nu12'), material.get('nu13'), material.get('nu23')], sff)

        elif anisotropy == 2:
            for i in range(6):
                for j in range(i, 6):
                    _v = material.get(f'c{i+1}{j+1}')
                    file.write(f'{_v:{sff}}')
                    # sutl.writeFormatFloats(
                    #     file, material.get(f'c{i+1}{j+1}'), sff, newline=False)
                file.write('\n')

        if physics in [1, 4, 6]:
            sutl.writeFormatFloats(
                file, material.get('cte')+[material.get('specific_heat'),], sff)

    elif analysis.startswith('f'):
        # Write material properties for failure analysis

        strength = []
        if anisotropy == 0:
            if material.failure_criterion == 1:
                pass
            elif material.failure_criterion == 2:
                pass
            elif material.failure_criterion == 3:
                pass
            elif material.failure_criterion == 4:
                pass
            elif material.failure_criterion == 5:
                pass
        else:
            if material.failure_criterion == 1:
                pass
            elif material.failure_criterion == 2:
                pass
            elif material.failure_criterion == 3:
                pass
            elif material.failure_criterion == 4:
                # Tsai-Wu
                strength = [
                    material.get('x1t'), material.get('x2t'), material.get('x3t'),
                    material.get('x1c'), material.get('x2c'), material.get('x3c'),
                    material.get('x23'), material.get('x13'), material.get('x12'),
                    # strength_constants['r'], m.strength_constants['t'], m.strength_constants['s'],
                ]
            elif material.failure_criterion == 5:
                pass

        sutl.writeFormatIntegers(
            file,
            # (m.strength['criterion'], len(m.strength['constants'])),
            [material.failure_criterion, len(strength)],
            sfi
        )
        # file.write((sff+'\n').format(m.strength['chara_len']))
        sutl.writeFormatFloats(file, [material.get('char_len'),], sff)
        # sutl.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
        sutl.writeFormatFloats(file, strength, sff)

    file.write('\n')
    
    # counter += 1

    # file.write('\n')
    return









def _writeMaterials(
    dict_materials, file, analysis, physics=0,
    sfi:str='8d', sff:str='20.12e'):
    """
    """

    logger.debug('writing materials...')

    # counter = 0
    for mid, m in dict_materials.items():
        _writeMaterial(
            mid=mid,
            material=m,
            file=file,
            analysis=analysis,
            physics=physics,
            sfi=sfi,
            sff=sff)

    file.write('\n')
    return









def _writeHeader(sg:StructureGene, file, sfi, sff, version=None):
    ssfi = '{:' + sfi + '}'

    # Extra inputs for dimensionally reducible structures
    if (sg.smdim == 1) or (sg.smdim == 2):
        # model (0: classical, 1: shear refined)
        file.write(ssfi.format(sg.model))
        file.write('  # structural model (0: classical, 1: shear refined)')
        file.write('\n\n')

        if sg.smdim == 1:  # beam
            # initial twist/curvatures
            sutl.writeFormatFloats(
                file,
                [sg.initial_twist, sg.initial_curvature[0], sg.initial_curvature[1]],
                sff, newline=False
            )
            file.write('  # initial curvatures k11, k12, k13\n')
            file.write('\n')
            # oblique cross section
            sutl.writeFormatFloats(file, sg.oblique, sff)

        elif sg.smdim == 2:  # shell
            # initial twist/curvatures
            sutl.writeFormatFloats(file, sg.initial_curvature, sff, newline=False)
            file.write('  # initial curvatures k12, k21\n')
            if version > '2.1':
                sutl.writeFormatFloats(file, sg.lame_params, sff, newline=False)
                file.write('  # Lame parameters\n')
        file.write('\n')

    # Head
    nums = [
        sg.physics, sg.ndim_degen_elem, sg.use_elem_local_orient,
        sg.is_temp_nonuniform
    ]
    cmt = '  # analysis, elem_flag, trans_flag, temp_flag'
    if version > '2.1':
        nums += [sg.force_flag, sg.steer_flag]
        cmt = cmt + ', force_flag, steer_flag'
    sutl.writeFormatIntegers(file, nums, sfi, newline=False)
    file.write(cmt)
    file.write('\n\n')

    nums = [
        sg.sgdim, sg.nnodes, sg.nelems, sg.nmates,
        sg.num_slavenodes, sg.nma_combs
    ]
    sutl.writeFormatIntegers(file, nums, sfi, newline=False)
    file.write('  # nsg, nnode, nelem, nmate, nslave, nlayer')
    file.write('\n\n')

    return









# def _writeInputMaterialStrength(sg, file, sfi, sff):
#     for i, m in sg.materials.items():
#         # print(m.strength)
#         # print(m.failure_criterion)
#         # print(m.char_len)

#         # file.write('{} {}'.format(m.failure_criterion, len(m.strength)))

#         strength = []
#         if m.type == 0:
#             pass
#         else:
#             if m.failure_criterion == 1:
#                 pass
#             elif m.failure_criterion == 2:
#                 pass
#             elif m.failure_criterion == 3:
#                 pass
#             elif m.failure_criterion == 4:
#                 # Tsai-Wu
#                 strength = [
#                     m.strength_constants['xt'], m.strength_constants['yt'], m.strength_constants['zt'],
#                     m.strength_constants['xc'], m.strength_constants['yc'], m.strength_constants['zc'],
#                     m.strength_constants['r'], m.strength_constants['t'], m.strength_constants['s'],
#                 ]
#             elif m.failure_criterion == 5:
#                 pass

#         sutl.writeFormatIntegers(
#             file,
#             # (m.strength['criterion'], len(m.strength['constants'])),
#             [m.failure_criterion, len(strength)],
#             sfi
#         )
#         # file.write((sff+'\n').format(m.strength['chara_len']))
#         sutl.writeFormatFloats(file, [m.char_len,], sff)
#         # sutl.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
#         sutl.writeFormatFloats(file, strength, sff)
#     return









# def _writeInputDisplacements(sg, file, sff):
#     sutl.writeFormatFloats(file, sg.global_displacements, sff[2:-1])
#     sutl.writeFormatFloatsMatrix(file, sg.global_rotations, sff[2:-1])

def _writeDisplacementRotation(
    file,
    displacement:list[float]=[0, 0, 0],
    rotation:list[list[float]]=[[1,0,0],[0,1,0],[0,0,1]],
    sff:str='20.12e'):

    # sutl.writeFormatFloats(file, macro_response.getDisplacement(), sff)
    # sutl.writeFormatFloatsMatrix(file, macro_response.getDirectionCosine(), sff)
    sutl.writeFormatFloats(file, displacement, sff)
    file.write('\n')
    sutl.writeFormatFloatsMatrix(file, rotation, sff)









# def _writeInputLoads(sg, file, sfi, sff):
#     for load_case in sg.global_loads:
#         sutl.writeFormatFloats(file, load_case, sff)
#     file.write('\n')
#     return

def _writeLoad(
    file, macro_response:smdl.StateCase, model, sff:str='20.12e'):

    # _load = macro_response.getLoad()
    _load = macro_response.load.data

    if model.lower() == 'sd1':
        pass

    elif model.lower() == 'pl1':
        sutl.writeFormatFloats(file, _load, fmt=sff)

    elif model.lower() == 'pl2':
        pass

    elif model.lower() == 'bm1':
        # sutl.writeFormatFloats(file, macro_response.getLoad())
        sutl.writeFormatFloats(file, _load, fmt=sff)

    elif model.lower() == 'bm2':
        sutl.writeFormatFloats(file, [_load[i] for i in [0, 3, 4, 5]], fmt=sff)
        sutl.writeFormatFloats(file, [_load[i] for i in [1, 2]], fmt=sff)
        file.write('\n')

        # _distr_load = macro_response.getDistributedLoad()
        _distr_load = macro_response.distributed_load
        if _distr_load is None:
            _distr_load = [[0,]*6]*4
        else:
            _distr_load = _distr_load.data
        sutl.writeFormatFloats(file, _distr_load[0], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[1], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[2], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[3], fmt=sff)

    file.write('\n')

    return


