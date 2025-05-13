from __future__ import annotations

import logging

# import sgio._global as GLOBAL
# import sgio.meshio as smsh
# import sgio.iofunc._meshio as smsh
import sgio.model as smdl
# from sgio.model import Model
import sgio.utils as sutl
from sgio.core.sg import StructureGene
# from sgio._exceptions import OutputFileError

from ._input import (
    _readHeader,
    _readMesh,
    _readMaterialRotationCombinations,
    _readMaterials,
    writeInputBuffer,
    writeInputBufferGlobal,
    )

from ._output import (
    _readOutputH,
    _readOutputFailureIndex,
    )


logger = logging.getLogger(__name__)


# ====================================================================
# Readers
# ====================================================================


# Read input
# ----------

def read_input_buffer(file, format_version:str, model:int|str):
    """
    """
    logger.debug(f'local variables:\n{sutl.convertToPrettyString(locals())}')
    sg = StructureGene()
    sg.version = format_version

    if isinstance(model, int):
        smdim = model
    elif isinstance(model, str):
        if model.upper()[:2] == 'SD':
            smdim = 3
        elif model.upper()[:2] == 'PL':
            smdim = 2
        elif model.upper()[:2] == 'BM':
            smdim = 1

    sg.smdim = smdim

    # Read head
    configs = _readHeader(file, format_version, smdim)
    sg.sgdim = configs['sgdim']
    sg.physics = configs['physics']
    sg.do_dampling = configs.get('do_damping', 0)
    _use_elem_local_orient = configs.get('use_elem_local_orient', 0)
    sg.is_temp_nonuniform = configs.get('is_temp_nonuniform', 0)
    if smdim != 3:
        sg.model = configs['model']
        if smdim == 1:
            init_curvs = configs.get('curvature', [0.0, 0.0, 0.0])
            sg.initial_twist = init_curvs[0]
            sg.initial_curvature = init_curvs[1:]
        elif smdim == 2:
            sg.initial_curvature = configs.get('curvature', [0.0, 0.0])

    nnode = configs['num_nodes']
    nelem = configs['num_elements']

    # Read mesh
    sg.mesh = _readMesh(file, sg.sgdim, nnode, nelem, _use_elem_local_orient)

    # Read material in-plane angle combinations
    nma_comb = configs['num_mat_angle3_comb']
    sg.mocombos = _readMaterialRotationCombinations(file, nma_comb)

    # Read materials
    nmate = configs['num_materials']
    sg.materials = _readMaterials(file, nmate, sg.physics)

    return sg










# Read output
# -----------
def read_output_buffer(
    file, analysis=0, model_type=None,
    # sg:StructureGene=None,
    **kwargs
    ):
    # print('reading output buffer...')

    if analysis == 0 or analysis == 'h' or analysis == '':
        return _readOutputH(file, model_type=model_type, **kwargs)

    elif analysis == 1 or analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
        pass

    elif analysis == 'f' or analysis == 3:
        # return readSCOutFailure(file, analysis)
        pass
    elif analysis == 'fe' or analysis == 4:
        # return readSCOutFailure(file, analysis)
        pass
    elif analysis == 'fi' or analysis == 5:
        return _readOutputFailureIndex(file)

        # output = {}
        # _fi, _sr, _eids_sr_min = _readOutputFailureIndex(file)
        # output['failure_index'] = _fi
        # output['strength_ratio'] = _sr
        # output['elems_sr_min'] = _eids_sr_min

        # return output

    return










# ====================================================================
# Writers
# ====================================================================


def write_buffer(
    sg:StructureGene, file, analysis='h', model='sd1',
    model_space='xy', prop_ref_y='x',
    macro_responses:list[smdl.StateCase]=[],
    load_type=0,
    sfi:str='8d', sff:str='20.12e', version=None
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

    if analysis == 'h':
        writeInputBuffer(
            sg, file, analysis, sg.physics, model_space,
            sfi, sff, version)

    elif (analysis == 'd') or (analysis == 'l') or (analysis.startswith('f')):
        if sg is None:
            materials = {}
        else:
            materials = sg.materials

        writeInputBufferGlobal(
            file=file,
            model=model,
            analysis=analysis,
            physics=sg.physics,
            load_type=load_type,
            macro_responses=macro_responses,
            dict_materials=materials,
            sfi=sfi,
            sff=sff
            )

    return






