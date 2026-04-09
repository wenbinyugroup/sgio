from __future__ import annotations

import logging

import sgio.model as smdl
import sgio.utils as sutl
from sgio.core.sg import StructureGene
from ._mesh import (
    read_buffer,
    write_buffer,
)
from ..common import (
    read_material_rotation_combinations,
    read_materials as common_read_materials,
    read_material as common_read_material,
    read_elastic_property as common_read_elastic_property,
    read_thermal_property,
    write_material_combos,
    write_material as common_write_material,
    write_materials as common_write_materials,
    write_displacement_rotation,
    write_load,
)


logger = logging.getLogger(__name__)


def _readHeader(file, format_version:str, smdim:int):
    """
    """

    logger.debug('reading header...')
    logger.debug(f'local variables:\n{sutl.convertToPrettyString(locals())}')

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
    """Read material rotation combinations (SwiftComp format).
    
    Wrapper for common function with SwiftComp-specific comment character.
    """
    return read_material_rotation_combinations(file, ncomb, comment_char='#')




def _readMaterials(file, nmate:int, physics:int):
    """Read materials from SwiftComp input file.
    
    Wrapper for common function with SwiftComp-specific parameters.
    """
    return common_read_materials(
        file, nmate, comment_char='#', has_ntemp=True, physics=physics
    )




def _readMaterial(file, isotropy:int, ntemp:int=1, physics:int=0):
    """Read a single material from SwiftComp input file.
    
    Wrapper for common function with SwiftComp-specific parameters.
    """
    return common_read_material(
        file, isotropy, ntemp, comment_char='#', physics=physics
    )




def _readElasticProperty(file, isotropy:int):
    """Read elastic properties from SwiftComp input file.
    
    Wrapper for common function with SwiftComp-specific parameters.
    """
    return common_read_elastic_property(file, isotropy, comment_char='#')



def _readThermalProperty(file, isotropy:int):
    """Read thermal properties from SwiftComp input file.
    
    Wrapper for common function.
    """
    return read_thermal_property(file, isotropy)























def writeInputBuffer(
    sg, file, analysis, physics,
    model_space, prop_ref_y,
    sfi:str='8d', sff:str='20.12e', version=None):
    """
    """

    logger.debug(f'writing sg input...')

    ssff = '{:' + sff + '}'
    sg.version = version

    logger.debug('format version: {}'.format(sg.version))

    _writeHeader(sg, file, sfi, sff, version)

    _writeMesh(
        mesh=sg.mesh,
        file=file,
        sgdim=sg.sgdim,
        model_space=model_space,
        prop_ref_y=prop_ref_y,
        int_fmt=sfi, float_fmt=sff
        )

    # Get material ID mapping for export
    mat_id_map = sg.get_export_material_ids()
    
    _writeMOCombos(sg, file, sfi, sff)

    _writeMaterials(
        dict_materials=sg.materials,
        file=file,
        analysis=analysis,
        physics=physics,
        sfi=sfi,
        sff=sff,
        mat_id_map=mat_id_map
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
        # Generate ID mapping for dict_materials
        mat_id_map = {name: idx + 1 for idx, name in enumerate(dict_materials.keys())}
        _writeMaterials(
            dict_materials=dict_materials,
            file=file,
            analysis=analysis,
            physics=physics,
            sfi=sfi,
            sff=sff,
            mat_id_map=mat_id_map
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









def _writeMesh(
    mesh, file, sgdim, model_space, prop_ref_y='x',
    int_fmt='8d', float_fmt='20.12e'
    ):
    """Write mesh data to SwiftComp format."""
    logger.debug('writing mesh...')

    write_buffer(
        file, mesh, sgdim=sgdim,
        model_space=model_space, prop_ref_y=prop_ref_y,
        int_fmt=int_fmt, float_fmt=float_fmt)

    return









def _writeMOCombos(sg, file, sfi, sff):
    """Write material-orientation combinations (SwiftComp format).
    
    Wrapper for common function with SwiftComp-specific comment character.
    """
    write_material_combos(sg, file, sfi, sff, comment_char='#')
    return









def _writeMaterial(
    mid:int, material:smdl.CauchyContinuumModel, file,
    analysis, physics,
    sfi:str='8d', sff:str='20.12e'):
    """Write a single material (SwiftComp format).
    
    Wrapper for common function with SwiftComp-specific parameters.
    """
    common_write_material(
        mid, material, file, analysis,
        physics=physics,
        sfi=sfi, sff=sff,
        comment_char='#',
        has_ntemp=True
    )
    return









def _writeMaterials(
    dict_materials, file, analysis, physics=0,
    sfi:str='8d', sff:str='20.12e', mat_id_map=None):
    """Write materials (SwiftComp format).
    
    Wrapper for common function with SwiftComp-specific parameters.
    """
    common_write_materials(
        dict_materials, file, analysis,
        physics=physics,
        sfi=sfi, sff=sff,
        comment_char='#',
        has_ntemp=True,
        mat_id_map=mat_id_map
    )
    return









def _writeHeader(sg:StructureGene, file, sfi, sff, version=None):
    ssfi = '{:' + sfi + '}'

    # Extra inputs for dimensionally reducible structures
    if (sg.smdim == 1) or (sg.smdim == 2):
        # model (0: classical/kirchhoff-love, 1: shear refined/mindlin)
        _model_names = {1: {0: 'euler-bernoulli', 1: 'timoshenko'}, 2: {0: 'kirchhoff-love', 1: 'mindlin'}}
        _model_name = _model_names.get(sg.smdim, {}).get(sg.model, str(sg.model))
        file.write(ssfi.format(sg.model))
        file.write(f'  # model ({_model_name})')
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
    displacement:list[float]=None,
    rotation:list[list[float]]=None,
    sff:str='20.12e'):
    """Write displacement and rotation (SwiftComp format).
    
    Wrapper for common function.
    """
    write_displacement_rotation(file, displacement, rotation, sff)









# def _writeInputLoads(sg, file, sfi, sff):
#     for load_case in sg.global_loads:
#         sutl.writeFormatFloats(file, load_case, sff)
#     file.write('\n')
#     return

def _writeLoad(
    file, macro_response:smdl.StateCase, model, sff:str='20.12e'):
    """Write load data (SwiftComp format).
    
    Wrapper for common function.
    """
    write_load(file, macro_response, model, sff)
    return


