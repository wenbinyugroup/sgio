from __future__ import annotations

import logging

# import sgio._global as GLOBAL
import sgio.utils as sutl
import sgio.model as smdl
# import sgio.iofunc._meshio as smsh
from ._mesh import (
    read_buffer,
    write_buffer,
)
from ..common import (
    read_material_rotation_combinations,
    read_materials as common_read_materials,
    read_material as common_read_material,
    read_elastic_property as common_read_elastic_property,
    write_material_combos,
    write_material as common_write_material,
    write_materials as common_write_materials,
    write_displacement_rotation,
    write_load,
)

logger = logging.getLogger(__name__)



def _readHeader(file):
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


def _readMesh(file, sgdim:int, nnode:int, nelem:int, format_flag):
    """
    """

    logger.debug('reading mesh...')

    mesh = read_buffer(
        file,
        sgdim=sgdim, nnode=nnode, nelem=nelem,
        format_flag=format_flag
    )

    return mesh



def _readMaterialRotationCombinations(file, ncomb):
    """Read material rotation combinations (VABS format).
    
    Wrapper for common function with VABS-specific comment character.
    """
    return read_material_rotation_combinations(file, ncomb, comment_char='!')









def _readMaterials(file, nmate:int):
    """Read materials from VABS input file.
    
    Wrapper for common function with VABS-specific parameters.
    """
    return common_read_materials(
        file, nmate, comment_char='!', has_ntemp=False, physics=0
    )




def _readMaterial(file, isotropy:int, ntemp:int=1):
    """Read a single material from VABS input file.
    
    Wrapper for common function with VABS-specific parameters.
    """
    return common_read_material(
        file, isotropy, ntemp, comment_char='!', physics=0
    )









def _readElasticProperty(file, isotropy:int):
    """Read elastic properties from VABS input file.
    
    Wrapper for common function with VABS-specific parameters.
    """
    return common_read_elastic_property(file, isotropy, comment_char='!')






# Write input





def _writeMesh(
    mesh, file, model_space='', prop_ref_y='x',
    int_fmt='8d', float_fmt='20.12e'
    ):
    """Write mesh data to VABS format."""
    logger.debug('writing mesh...')

    write_buffer(
        file, mesh,
        sgdim=2, model_space=model_space, prop_ref_y=prop_ref_y,
        int_fmt=int_fmt, float_fmt=float_fmt
    )

    return




def _writeMOCombos(sg, file, sfi:str='8d', sff:str='20.12e'):
    """Write material-orientation combinations (VABS format).
    
    Wrapper for common function with VABS-specific comment character.
    """
    write_material_combos(sg, file, sfi, sff, comment_char='!')
    return




def _writeMaterial(
    mid:int, material:smdl.CauchyContinuumModel, file,
    analysis, thermal_flag,
    sfi:str='8d', sff:str='20.12e'):
    """Write a single material (VABS format).
    
    Wrapper for common function with VABS-specific parameters.
    """
    common_write_material(
        mid, material, file, analysis,
        physics=thermal_flag,
        sfi=sfi, sff=sff,
        comment_char='!',
        has_ntemp=False
    )
    return




def _writeMaterials(
    dict_materials, file, analysis, thermal_flag=0,
    sfi:str='8d', sff:str='20.12e', mat_id_map=None):
    """Write materials (VABS format).
    
    Wrapper for common function with VABS-specific parameters.
    """
    common_write_materials(
        dict_materials, file, analysis,
        physics=thermal_flag,
        sfi=sfi, sff=sff,
        comment_char='!',
        has_ntemp=False,
        mat_id_map=mat_id_map
    )
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
    file,
    displacement:list[float]=None,
    rotation:list[list[float]]=None,
    sff:str='20.12e'):
    """Write displacement and rotation (VABS format).
    
    Wrapper for common function.
    """
    write_displacement_rotation(file, displacement, rotation, sff)









def _writeLoad(
    file, macro_response:smdl.StateCase, model, sff:str='20.12e'):
    """Write load data (VABS format).
    
    Wrapper for common function.
    """
    write_load(file, macro_response, model, sff)
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




