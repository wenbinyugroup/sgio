from __future__ import annotations

import logging

# import sgio._global as GLOBAL
import sgio.utils as sutl
import sgio.model as smdl
import sgio.iofunc._meshio as smsh
from ._mesh import (
    read_buffer,
    write_buffer,
)

logger = logging.getLogger(__name__)



def _readHeader(file, file_format:str, format_version:str, smdim:int):
    """
    """

    logger.debug('reading header...')

    configs = {}

    configs['sgdim'] = 2

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['format'] = int(line[0])
    configs['num_mat_angle3_comb'] = int(line[1])

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['model'] = int(line[0])
    configs['do_damping'] = int(line[1])
    configs['physics'] = 1 if int(line[2]) > 0 else 0

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['is_curve'] = int(line[0])
    configs['is_oblique'] = int(line[1])
    configs['model'] = 3 if line[2] == '1' else configs['model']  # trapeze
    configs['model'] = 2 if line[3] == '1' else configs['model']  # vlasov

    if configs['is_curve'] == 1:
        line = sutl.readNextNonEmptyLine(file)
        line = line.split()
        configs['curvature'] = list(map(float, line[:3]))

    if configs['is_oblique'] == 1:
        line = sutl.readNextNonEmptyLine(file)
        line = line.split()
        configs['oblique'] = list(map(float, line[:2]))

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['num_nodes'] = int(line[0])
    configs['num_elements'] = int(line[1])
    configs['num_materials'] = int(line[2])

    return configs


def _readMesh(file, file_format:str, sgdim:int, nnode:int, nelem:int, read_local_frame):
    """
    """

    logger.debug('reading mesh...')

    mesh = smsh.read(
        file, file_format,
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
        line = file.readline().split('!')[0].strip()
        while line == '':
            line = file.readline().split('!')[0].strip()

        line = line.split()
        comb_id = int(line[0])
        mate_id = int(line[1])
        ip_ratation = float(line[2])

        combinations[comb_id] = [mate_id, ip_ratation]

        counter += 1

    return combinations









def _readMaterials(file, file_format:str, nmate:int):
    """
    """

    logger.debug('reading materials...')

    materials = {}

    counter = 0
    while counter < nmate:
        line = file.readline().split('!')[0].strip()
        while line == '':
            line = file.readline().split('!')[0].strip()

        line = line.split()

        # Read material id, isotropy
        mate_id, isotropy = list(map(int, line))
        ntemp = 1
        # material, line = _readMaterial(file, file_format, isotropy)

        material = _readMaterial(file, file_format, isotropy, ntemp)

        materials[mate_id] = material

        counter += 1

    return materials




def _readMaterial(file, file_format:str, isotropy:int, ntemp:int=1):
    """
    """

    # mp = mmsd.MaterialProperty()
    # mp = smdl.MaterialSection()
    mp = smdl.CauchyContinuumModel()
    # mp.isotropy = isotropy
    mp.set('isotropy', isotropy)

    temp_counter = 0
    while temp_counter < ntemp:

        # Read elastic properties
        elastic_props = _readElasticProperty(file, isotropy)
        mp.setElastic(elastic_props, isotropy)

        line = file.readline().split('!')[0].strip()
        while line == '':
            line = file.readline().split('!')[0].strip()
        density = float(line)

        # mp.density = density
        mp.set('density', density)

        # Read thermal properties

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
        line = file.readline().split('!')[0].strip()
        while line == '':
            line = file.readline().split('!')[0].strip()
        constants.extend(list(map(float, line.split())))

    return constants






# Write input





def _writeMesh(mesh, file, int_fmt, float_fmt):
    """
    """
    logger.debug('writing mesh...')

    write_buffer(
        file, mesh,
        sgdim=2,
        int_fmt=int_fmt, float_fmt=float_fmt
    )

    return




def _writeMOCombos(sg, file, sfi:str='8d', sff:str='20.12e'):
    ssfi = '{:' + sfi + '}'
    ssff = '{:' + sff + '}'
    count = 0
    for cid, combo in sg.mocombos.items():
        count += 1
        file.write((ssfi + ssfi + ssff).format(cid, combo[0], combo[1]))
        if count == 1:
            file.write('  ! combination id, material id, in-plane rotation angle')
        file.write('\n')
    file.write('\n')
    return




def _writeMaterial(
    mid:int, material:smdl.CauchyContinuumModel, file,
    analysis, thermal_flag,
    sfi:str='8d', sff:str='20.12e'):
    """
    """

    anisotropy = material.get('isotropy')

    if analysis == 'h':
        # Write material properties for homogenization

        sutl.writeFormatIntegers(file, (mid, anisotropy), sfi, newline=False)
        file.write('  ! material id, anisotropy\n')

        # Write elastic properties
        if anisotropy == 0:
            sutl.writeFormatFloats(file, [material.get('e'), material.get('nu')], sff)
            if thermal_flag == 3:
                sutl.writeFormatFloats(file, [material.get('alpha'),], sff)

        elif anisotropy == 1:
            sutl.writeFormatFloats(file, [material.get('e1'), material.get('e2'), material.get('e3')], sff)
            sutl.writeFormatFloats(file, [material.get('g12'), material.get('g13'), material.get('g23')], sff)
            sutl.writeFormatFloats(file, [material.get('nu12'), material.get('nu13'), material.get('nu23')], sff)
            if thermal_flag == 3:
                sutl.writeFormatFloats(
                    file, [material.get('alpha11'), material.get('alpha22'), material.get('alpha33')], sff)

        elif anisotropy == 2:
            for _i in range(6):
                for _j in range(_i, 6):
                    sutl.writeFormatFloats(
                        file, material.get(f'c{_i+1}{_j+1}'), sff)
            if thermal_flag == 3:
                sutl.writeFormatFloats(
                    file, [
                        material.get('alpha11'),
                        material.get('alpha12')*2,
                        material.get('alpha13')*2,
                        material.get('alpha22'),
                        material.get('alpha23')*2,
                        material.get('alpha33')
                    ],sff)

        sutl.writeFormatFloats(file, [material.get('density'),], sff)

    elif analysis == 'f':
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
        # sutl.writeFormatFloats(file, [m.char_len,], sff)
        # sutl.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
        sutl.writeFormatFloats(file, strength, sff)


    file.write('\n')

    return




def _writeMaterials(
    dict_materials, file, analysis, thermal_flag=0,
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
            thermal_flag=thermal_flag,
            sfi=sfi,
            sff=sff)

    file.write('\n')
    return









def _writeHeader(
    format_flag, nlayer,
    timoshenko_flag, damping_flag, thermal_flag,
    curve_flag, oblique_flag, trapeze_flag, vlasov_flag,
    initial_curvatures, obliqueness,
    nnode, nelem, nmate,
    file, sfi:str='8d', sff:str='20.12e'):
    # ssfi = '{:' + sfi + '}'

    # format_flag  nlayer
    sutl.writeFormatIntegers(file, [format_flag, nlayer], newline=False)
    file.write('  ! format_flag, nlayer\n\n')

    # timoshenko_flag  damping_flag  thermal_flag
    sutl.writeFormatIntegers(
        file, [timoshenko_flag, damping_flag, thermal_flag], sfi, newline=False)
    file.write('  ! model_flag, damping_flag, thermal_flag\n\n')

    # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
    line = [curve_flag, oblique_flag, trapeze_flag, vlasov_flag]
    # if (sg.initial_twist != 0.0) or (sg.initial_curvature[0] != 0.0) or (sg.initial_curvature[1] != 0.0):
    #     line[0] = 1
    # if (sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0):
    #     line[1] = 1
    sutl.writeFormatIntegers(file, line, sfi, newline=False)
    file.write('  ! curve_flag, oblique_flag, trapeze_flag, vlasov_flag\n\n')

    # k1  k2  k3
    if line[0] == 1:
        sutl.writeFormatFloats(
            file, initial_curvatures, sff, newline=False
        )
        file.write('  ! k11, k12, k13 (initial curvatures)\n\n')
    
    # oblique1  oblique2
    if line[1] == 1:
        sutl.writeFormatFloats(file, obliqueness, sff, newline=False)
        file.write('  ! cos11, cos21 (obliqueness)\n\n')
    
    # nnode  nelem  nmate
    sutl.writeFormatIntegers(
        file, [nnode, nelem, nmate], sfi, newline=False)
    file.write('  ! nnode, nelem, nmate\n\n')

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









def _writeDisplacementRotation(
    # macro_response:smdl.SectionResponse,
    file,
    displacement:list[float]=[0, 0, 0],
    rotation:list[list[float]]=[[1,0,0],[0,1,0],[0,0,1]],
    sff:str='20.12e'):

    # sutl.writeFormatFloats(file, macro_response.getDisplacement(), sff)
    # sutl.writeFormatFloatsMatrix(file, macro_response.getDirectionCosine(), sff)
    sutl.writeFormatFloats(file, displacement, sff)
    file.write('\n')
    sutl.writeFormatFloatsMatrix(file, rotation, sff)









def _writeLoad(
    file, macro_response:smdl.StateCase, model, sff:str='20.12e'):

    # _load = macro_response.getLoad()
    _load = macro_response.load.data

    if model == 0 or model == 'BM1':
        # sutl.writeFormatFloats(file, macro_response.getLoad())
        sutl.writeFormatFloats(file, _load, fmt=sff)

    elif model == 1 or model == 'BM2':
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




def _writeGlobalResponses(
    file, macro_responses:list[smdl.StateCase], model, sff:str='20.12e'):

    for _i, _response in enumerate(macro_responses):
        if _i == 0:
            # _writeDisplacementRotation(_response, file, sff)
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

            file.write('\n')

        _writeLoad(file, _response, model, sff)

    return




