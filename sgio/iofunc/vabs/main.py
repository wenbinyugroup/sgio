from __future__ import annotations

import logging

# from sgio.iofunc._meshio import read_sgmesh_buffer, write_sgmesh_buffer
from ._input import (
    _readHeader,
    _readMesh,
    _readMaterialRotationCombinations,
    _readMaterials,
    _writeHeader,
    _writeMesh,
    _writeMOCombos,
    _writeMaterials,
    _writeGlobalResponses,
)
# from ._mesh import *
from ._output import (
    _readOutputH,
    _readOutputNodeDisplacement,
    _readOutputElementStrainStressCase,
    _readOutputFailureIndexCase,
)

# import sgio._global as GLOBAL
# import sgio.meshio as smsh
import sgio.model as smdl
# import sgio.utils as sutl
from sgio.core.sg import StructureGene
logger = logging.getLogger(__name__)


def read_buffer(f, format_version:str):
    """
    """
    sg = StructureGene()
    sg.version = format_version

    smdim = 1

    sg.smdim = smdim
    # print(f'smdim: {smdim}')

    # Read head
    configs = _readHeader(f)
    # print(f'configs: {configs}')
    format_flag = configs['format']
    sg.sgdim = configs['sgdim']
    sg.physics = configs['physics']
    sg.do_dampling = configs.get('do_damping', 0)
    _use_elem_local_orient = configs.get('use_elem_local_orient', 0)
    sg.is_temp_nonuniform = configs.get('is_temp_nonuniform', 0)
    # if smdim != 3:
    sg.model = configs['model']
        # if smdim == 1:
    init_curvs = configs.get('curvature', [0.0, 0.0, 0.0])
    sg.initial_twist = init_curvs[0]
    sg.initial_curvature = init_curvs[1:]


    nnode = configs['num_nodes']
    nelem = configs['num_elements']

    # Read mesh
    sg.mesh = _readMesh(f, sg.sgdim, nnode, nelem, format_flag)

    # Read material in-plane angle combinations
    nma_comb = configs['num_mat_angle3_comb']
    sg.mocombos = _readMaterialRotationCombinations(f, nma_comb)

    # Read materials
    nmate = configs['num_materials']
    sg.materials = _readMaterials(f, nmate)

    # print(f'sg.model: {sg.model}')

    return sg












# ====================================================================
# Read output
# ====================================================================
def read_output_buffer(
    file, analysis='h', sg:StructureGene=None, extension:str='', model_type='BM1',
    tool_version='', ncase=1, nelem=0,
    **kwargs):
    """Read VABS output file buffer.

    Parameters
    ----------
    file: file
        File object of the output file.
    analysis: str, optional
        Analysis type. Default is homogenization.
    sg: StructureGene, optional
        StructureGene object.
    extension: str, optional
        File extension of the output file.
    model_type: str, optional
        Model type. Default is 'BM1'.
    tool_version: str, optional
        Tool version.
    ncase: int, optional
        Number of load cases. Default is 1.
    nelem: int, optional
        Number of elements.

    Returns
    -------
    Model or list of dict:
        Model object or list of dictionaries containing the output data.
    """
    logger.debug(f'reading vabs output...')
    logger.debug(locals())

    if analysis == 0 or analysis == 'h' or analysis == '':
        if not sg is None:
            # print(f'sg.model: {sg.model}')
            if sg.model == 0:
                return _readOutputH(file, model_type='bm1', **kwargs)
            elif sg.model == 1:
                return _readOutputH(file, model_type='bm2', **kwargs)
        else:
            return _readOutputH(file, model_type=model_type, **kwargs)

    elif analysis == 1 or analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
        if extension == 'u':
            return _readOutputNodeDisplacement(file)
        elif extension == 'ele':
            if nelem == 0:
                nelem = sg.nelems

            if ncase == 1:
                if float(tool_version) > 4:
                    line = file.readline()  # skip the first line
                return _readOutputElementStrainStressCase(file, nelem)
            else:
                #TODO
                pass

    elif analysis == 'f' or analysis == 3:
        # return readSCOutFailure(file, analysis)
        pass

    elif analysis == 'fe' or analysis == 4:
        # return readSCOutFailure(file, analysis)
        pass

    elif analysis == 'fi' or analysis == 5:
        if nelem == 0:
            nelem = sg.nelems

        if ncase == 1:
            if float(tool_version) > 4:
                line = file.readline()  # skip the first line
            return _readOutputFailureIndexCase(file, nelem)
        else:
            #TODO
            pass

        # output = {}
        # _fi, _sr, _eids_sr_min = _readOutputFailureIndex(file)
        # output['failure_index'] = _fi
        # output['strength_ratio'] = _sr
        # output['elems_sr_min'] = _eids_sr_min

        # return output

    return










# Writers


def write_buffer(
    sg:StructureGene, file, analysis='h', sg_fmt:int=1, model=0,
    model_space='', prop_ref_y='x',
    renumber_nodes=False, renumber_elements=False,
    macro_responses:list[smdl.StateCase]=[],
    sfi:str='8d', sff:str='20.12e', version=None,
    **kwargs
    ):
    """Write analysis input

    Parameters
    ----------
    fn : str
        Name of the input file
    file_format : {'vabs' (or 'v'), 'swfitcomp' (or 'sc', 's')}
        file_format of the analysis
    analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}, optional
        Analysis type, by default 'h'
    sg_fmt : {0, 1}, optional
        Format for the VABS input, by default 1

    Returns
    -------
    str
        Name of the input file
    """

    if sg is None:
        timoshenko_flag = model
    else:
        timoshenko_flag = 0
        trapeze_flag = 0
        vlasov_flag = 0
        if sg.model == 1:
            timoshenko_flag = 1
        elif sg.model == 2:
            timoshenko_flag = 1
            vlasov_flag = 1
        elif sg.model == 3:
            trapeze_flag = 1
        thermal_flag = 0
        if sg.physics == 1:
            thermal_flag = 3

    if analysis == 'h':
        writeInputBuffer(
            sg, file, analysis,
            timoshenko_flag, vlasov_flag, trapeze_flag, thermal_flag,
            model_space=model_space, prop_ref_y=prop_ref_y,
            renumber_nodes=renumber_nodes,
            renumber_elements=renumber_elements,
            sg_fmt=sg_fmt,
            sfi=sfi, sff=sff, version=version)

    elif (analysis == 'd') or (analysis == 'l') or (analysis.startswith('f')):
        if sg is None:
            materials = {}
        else:
            materials = sg.materials

        writeInputBufferGlobal(
            file, timoshenko_flag, analysis,
            macro_responses, materials,
            sfi=sfi, sff=sff)

    return









def writeInputBuffer(
    sg, file, analysis,
    timoshenko_flag, vlasov_flag, trapeze_flag, thermal_flag,
    model_space='', prop_ref_y='x',
    renumber_nodes=False, renumber_elements=False,
    sg_fmt:int=1,
    sfi:str='8d', sff:str='20.12e', version=None):
    """
    """

    logger.debug(f'writing sg input...')

    # ssff = '{:' + sff + '}'
    # if not version is None:
    #     sg.version = sutl.Version(version)
    sg.version = version

    logger.debug('format version: {}'.format(sg.version))

    nlayer = len(sg.mocombos)

    # timoshenko_flag = model
    # trapeze_flag = 0
    # vlasov_flag = 0
    # if sg.model == 1:
    #     timoshenko_flag = 1
    # elif sg.model == 2:
    #     timoshenko_flag = 1
    #     vlasov_flag = 1
    # elif sg.model == 3:
    #     trapeze_flag = 1
    # thermal_flag = 0
    # if sg.physics == 1:
    #     thermal_flag = 3

    curve_flag = 0
    if (sg.initial_twist != 0.0) or (sg.initial_curvature[0] != 0.0) or (sg.initial_curvature[1] != 0.0):
        curve_flag = 1
    initial_curvatures = [sg.initial_twist,]+sg.initial_curvature

    oblique_flag = 0
    if (sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0):
        oblique_flag = 1

    _writeHeader(
        sg_fmt, nlayer,
        timoshenko_flag, sg.do_damping, thermal_flag,
        curve_flag, oblique_flag, trapeze_flag, vlasov_flag,
        initial_curvatures, sg.oblique,
        sg.nnodes, sg.nelems, sg.nmates,
        file, sfi, sff)

    _writeMesh(
        sg.mesh, file,
        model_space=model_space, prop_ref_y=prop_ref_y,
        renumber_nodes=renumber_nodes,
        renumber_elements=renumber_elements,
        int_fmt=sfi, float_fmt=sff)

    # if not mesh_only:
    _writeMOCombos(sg, file, sfi, sff)

    # if not mesh_only:
    _writeMaterials(
        dict_materials=sg.materials,
        file=file,
        analysis=analysis,
        thermal_flag=thermal_flag,
        sfi=sfi,
        sff=sff)

    return




def writeInputBufferGlobal(
    file, model, analysis,
    macro_responses:list[smdl.StateCase]=[],
    dict_materials={},
    sfi:str='8d', sff:str='20.12e'):
    """Write material strength and global/macro responses to a file.

    Parameters
    ----------
    file:
        File object to which data will be written.
    model:
        Model of the global/macro structure.
    analysis:
        Identifier for the analysis. If 'f' (failure analysis), then material strengh will be written.
    """

    if analysis.startswith('f'):
        _writeMaterials(dict_materials, file, sfi=sfi, sff=sff)

    _writeGlobalResponses(file, macro_responses, model, sff)

