from __future__ import annotations

import logging

import sgio._global as GLOBAL

logger = logging.getLogger(GLOBAL.LOGGER_NAME)

import csv

import sgio._global as GLOBAL
import sgio.iofunc._abaqus as _abaqus
import sgio.iofunc._swiftcomp as _swiftcomp
import sgio.iofunc._vabs as _vabs
import sgio.meshio as meshio
import sgio.model as sgmodel
import sgio.utils as sutils
from sgio.core.sg import StructureGene


def read(
    fn, file_format, format_version='',
    sgdim=3, model=3, sg=None,
    mesh_only=False, **kwargs):
    """Read SG data file.

    Parameters
    ----------
    fn : str
        Name of the SG data file
    file_format : str
        Format of the SG data file
    format_version : str
        Version of the format
    sgdim : int
        Dimension of the geometry
    smdim : int
        Dimension of the macro structural model
    sg : StructureGene
        Structure gene object
    mesh_only : bool
        If read meshing data only

    Returns
    -------
    :obj:`Structure gene`
    """

    file_format = file_format.lower()

    # if file_format.lower() in ['vabs', 'sc', 'swiftcomp']:
    if file_format in ['sc', 'swiftcomp']:
        with open(fn, 'r') as file:
            sg = _swiftcomp.readInputBuffer(file, format_version, model)
    elif file_format == 'vabs':
        with open(fn, 'r') as file:
            sg = _vabs.readBuffer(file, file_format, format_version, model)
    elif file_format == 'abaqus':
        with open(fn, 'r') as file:
            sg = _abaqus.readInputBuffer(file, sgdim=sgdim, model=model)

    else:
        if not sg:
            sg = StructureGene(sgdim=sgdim, smdim=model)
        sg.mesh, _, _ = meshio.read(fn, file_format)

    return sg




def readOutputModel(
    fn, file_format, model_type='', sg=None, **kwargs
    ):
    """Read SG homogenization output file.

    Parameters
    ----------
    fn : str
        Name of the SG analysis output file
    file_format : str
        Format of the SG data file
    model_type : str
        Type of the macro structural model.
        Choose one from 'SD1', 'PL1', 'PL2', 'BM1', 'BM2'.
    sg : :obj:`StructureGene`
        Structure gene object

    Returns
    -------
    :obj:`sgmodel.Model`
        Consitutive model
    """

    model = None

    with open(fn, 'r') as file:
        if file_format.lower().startswith('s'):
            model = _swiftcomp.readOutputBuffer(
                file, analysis='h', model_type=model_type,
                **kwargs)

        elif file_format.lower().startswith('v'):
            model = _vabs.readOutputBuffer(
                file, analysis='h', sg=sg, model_type=model_type,
                **kwargs)

    return model




def readOutputState(
    fn, file_format, analysis, model_type='',
    sg=None, **kwargs
    ):
    """Read SG dehomogenization or failure analysis output.

    Parameters
    ----------
    fn : str
        Name of the SG analysis output file
    file_format : str
        Format of the SG data file
    analysis : str
        Indicator of SG analysis.
        Choose one from 'd', 'l', 'fi'.
    model_type : str
        Type of the macro structural model.
        Choose one from 'SD1', 'PL1', 'PL2', 'BM1', 'BM2'.
    sg : :obj:`StructureGene`
        Structure gene object
    """

    state_case = sgmodel.StateCase()

    if analysis == 'fi':
        if file_format.lower().startswith('s'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                return _swiftcomp.readOutputBuffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)

        elif file_format.lower().startswith('v'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                _fi, _sr, _eids_sr_min = _vabs.readOutputBuffer(file, analysis, sg, **kwargs)
            _state = sgmodel.State(
                name='fi', data=_fi, label=['fi'], location='element')
            state_case.addState(name='fi', state=_state)
            _state = sgmodel.State(
                name='sr', data=_sr, label=['sr'], location='element')
            state_case.addState(name='sr', state=_state)
            _sr_min = {}
            for _eid in _eids_sr_min:
                _sr_min[_eid] = _sr[_eid]
            _state = sgmodel.State(
                name='sr_min', data=_sr_min, label=['sr_min'], location='element')
            state_case.addState(name='sr_min', state=_state)

    elif analysis == 'd' or analysis == 'l':
        if file_format.lower().startswith('s'):
            pass

        elif file_format.lower().startswith('v'):
            # state_case = sgmodel.StateCase()

            # Displacement
            _u = None
            _fn = f'{fn}.U'
            with open(_fn, 'r') as file:
                _u = _vabs.readOutputBuffer(file, analysis, ext='u', **kwargs)
            _state = sgmodel.State(
                name='u', data=_u, label=['u1', 'u2', 'u3'], location='node')
            state_case.addState(name='u', state=_state)

            # Element strain and stress
            _ee, _es, _eem, _esm = None, None, None, None
            _fn = f'{fn}.ELE'
            with open(_fn, 'r') as file:
                _ee, _es, _eem, _esm = _vabs.readOutputBuffer(file, analysis, ext='ele', **kwargs)
            _state = sgmodel.State(
                name='ee', data=_ee, label=['e11', 'e12', 'e13', 'e22', 'e23', 'e33'], location='element')
            state_case.addState(name='ee', state=_state)
            _state = sgmodel.State(
                name='es', data=_es, label=['s11', 's12', 's13', 's22', 's23', 's33'], location='element')
            state_case.addState(name='es', state=_state)
            _state = sgmodel.State(
                name='eem', data=_eem, label=['em11', 'em12', 'em13', 'em22', 'em23', 'em33'], location='element')
            state_case.addState(name='eem', state=_state)
            _state = sgmodel.State(
                name='esm', data=_esm, label=['sm11', 'sm12', 'sm13', 'sm22', 'sm23', 'sm33'], location='element')
            state_case.addState(name='esm', state=_state)

            # state_field = sgmodel.StateField(
            #     node_displ=_u,
            #     elem_strain=_ee, elem_stress=_es, elem_strain_m=_eem, elem_stress_m=_esm
            # )

    return state_case




def readOutput(
    fn, file_format, analysis='h', model_type='',
    sg=None, **kwargs
    ):
    """Read SG analysis output file.

    Parameters
    ----------
    fn : str
        Name of the SG analysis output file
    file_format : str
        Format of the SG data file
    analysis : str
        Indicator of SG analysis.
        Choose one from 'h', 'd', 'l', 'fi'.
    model_type : str
        Type of the macro structural model.
        Choose one from 'SD1', 'PL1', 'PL2', 'BM1', 'BM2'.
    sg : :obj:`StructureGene`
        Structure gene object


    Returns
    -------
    Model
    """

    # print(f'reading {file_format} output file {fn}...')
    # print(f'file_format: {file_format}, analysis: {analysis}, smdim: {smdim}...')

    if analysis == 'h':
        with open(fn, 'r') as file:
            if file_format.lower().startswith('s'):
                return _swiftcomp.readOutputBuffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)
            elif file_format.lower().startswith('v'):
                return _vabs.readOutputBuffer(
                    file, analysis, sg, model_type=model_type,
                    **kwargs)

    elif analysis == 'fi':
        if file_format.lower().startswith('s'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                return _swiftcomp.readOutputBuffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)
        elif file_format.lower().startswith('v'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                return _vabs.readOutputBuffer(file, analysis, sg, **kwargs)

    elif analysis == 'd' or analysis == 'l':
        if file_format.lower().startswith('s'):
            pass

        elif file_format.lower().startswith('v'):
            state_case = sgmodel.StateCase()

            # Displacement
            _u = None
            _fn = f'{fn}.U'
            with open(_fn, 'r') as file:
                _u = _vabs.readOutputBuffer(file, analysis, ext='u', **kwargs)
            _state = sgmodel.State(
                name='u', data=_u, label=['u1', 'u2', 'u3'], location='node')
            state_case.addState(name='u', state=_state)

            # Element strain and stress
            _ee, _es, _eem, _esm = None, None, None, None
            _fn = f'{fn}.ELE'
            with open(_fn, 'r') as file:
                _ee, _es, _eem, _esm = _vabs.readOutputBuffer(file, analysis, ext='ele', **kwargs)
            _state = sgmodel.State(
                name='ee', data=_ee, label=['e11', 'e12', 'e13', 'e22', 'e23', 'e33'], location='element')
            state_case.addState(name='ee', state=_state)
            _state = sgmodel.State(
                name='es', data=_es, label=['s11', 's12', 's13', 's22', 's23', 's33'], location='element')
            state_case.addState(name='es', state=_state)
            _state = sgmodel.State(
                name='eem', data=_eem, label=['em11', 'em12', 'em13', 'em22', 'em23', 'em33'], location='element')
            state_case.addState(name='eem', state=_state)
            _state = sgmodel.State(
                name='esm', data=_esm, label=['sm11', 'sm12', 'sm13', 'sm22', 'sm23', 'sm33'], location='element')
            state_case.addState(name='esm', state=_state)

            # state_field = sgmodel.StateField(
            #     node_displ=_u,
            #     elem_strain=_ee, elem_stress=_es, elem_strain_m=_eem, elem_stress_m=_esm
            # )

            return state_case


    return




def write(
    sg:StructureGene, fn:str, file_format:str,
    format_version:str='', analysis='h', sg_fmt:int=1,
    macro_responses:list[sgmodel.StateCase]=[], model=0, load_type=0,
    sfi:str='8d', sff:str='20.12e', mesh_only=False
    ):
    """Write analysis input

    Parameters
    ----------
    sg
        Structure gene object
    fn
        Name of the input file
    file_format
        file_format of the analysis
    analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}, optional
        Analysis type, by default 'h'
    sg_fmt : {0, 1}, optional
        Format for the VABS input, by default 1
    sfi
        String formating integers
    sff
        String formating floats
    version
        Version of the format
    mesh_only
        If write meshing data only
    """

    logger.debug(f'writting sg data to {fn} (format: {file_format})...')

    # logger.debug(f'local variables:\n{sutils.convertToPrettyString(locals())}')

    _file_format = file_format.lower()

    _format_full_data = ['sc', 'swiftcomp', 'vabs']

    # Write meshing data only for partially supported formats
    if not _file_format in _format_full_data:
        mesh_only = True

    with open(fn, 'w', encoding='utf-8') as file:
        if mesh_only:
            sg.mesh.write(
                file,
                file_format,
                # sgdim=sg.sgdim,
                int_fmt=sfi,
                float_fmt=sff
                )

        else:
            if _file_format.startswith('s'):
                if format_version == '':
                    format_version = GLOBAL.SC_VERSION_DEFAULT

                _swiftcomp.writeBuffer(
                    sg, file,
                    analysis=analysis, model=model,
                    macro_responses=macro_responses,
                    load_type=load_type,
                    sfi=sfi, sff=sff, version=format_version,
                    )

            elif _file_format.startswith('v'):
                if format_version == '':
                    format_version = GLOBAL.VABS_VERSION_DEFAULT

                _vabs.writeBuffer(
                    sg, file,
                    analysis=analysis, sg_fmt=sg_fmt,
                    macro_responses=macro_responses, model=model,
                    sfi=sfi, sff=sff, version=format_version,
                    mesh_only=mesh_only)

    return fn




def convert(
    file_name_in:str, file_name_out:str,
    file_format_in:str='', file_format_out:str='',
    format_version_in:str='', format_version_out:str='',
    analysis:str|int='h', sgdim:int=3, model:int|str='SD1', sg_fmt:int=1,
    sfi:str='8d', sff:str='20.12e', mesh_only:bool=False
    ):
    """Convert the SG data file format.

    Parameters
    ----------
    file_name_in
        File name before conversion
    file_name_out
        File name after conversion
    """

    sg = read(
        fn=file_name_in,
        file_format=file_format_in,
        format_version=format_version_in,
        sgdim=sgdim,
        model=model,
        mesh_only=mesh_only)

    write(
        sg=sg,
        fn=file_name_out,
        file_format=file_format_out,
        format_version=format_version_out,
        analysis=analysis,
        sg_fmt=sg_fmt,
        sfi=sfi,
        sff=sff,
        mesh_only=mesh_only)

    return sg




# def readVABSOut(fn_in, analysis=0, scrnout=True):
#     """Read VABS outputs.

#     Parameters
#     ----------
#     fn_in : str
#         VABS input file name.
#     analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}
#         Analysis to be carried out.

#         * 0 or 'h' or '' - homogenization
#         * 1 or 'dn' - dehomogenization (nonlinear)
#         * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
#         * 3 or 'fi' - initial failure indices and strength ratios
#     scrnout : bool, optional
#         Switch of printing solver messages, by default True.

#     Returns
#     -------
#     various
#         Different analyses return different types of results.
#     """
#     if analysis == 0 or analysis == 'h' or analysis == '':
#         # Read homogenization results
#         if not fn_in.lower()[-2:] == '.k':
#             fn_in = fn_in + '.K'
#         return readVABSOutHomo(fn_in, scrnout)
#     elif analysis == 1 or analysis == 2 or ('d' in analysis) or analysis == 'l':
#         pass
#     elif analysis == 3 or analysis == 'fi':
#         # return readVABSOutStrengthRatio(fn_in+'.fi')
#         return readSGOutFailureIndex(fn_in+'.fi', 'vabs')









# def readSCOut(fn_in, smdim, analysis=0, scrnout=True):
#     r"""Read SwiftComp outputs.

#     Parameters
#     ----------
#     fn_in : str
#         SwiftComp input file name.
#     smdim : int
#         Dimension of the macroscopic structural model.
#     analysis : {0, 2, 3, 4, 5, '', 'h', 'dl', 'd', 'l', 'fi', 'f', 'fe'}
#         Analysis to be carried out.

#         * 0 or 'h' or '' - homogenization
#         * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
#         * 3 or 'fi' - initial failure indices and strength ratios
#         * 4 or 'f' - initial failure strength
#         * 5 or 'fe' - initial failure envelope
#     scrnout : bool, optional
#         Switch of printing solver messages., by default True

#     Returns
#     -------
#     various
#         Different analyses return different types of results.
#     """
#     # if not logger:
#     #     logger = mul.initLogger(__name__)

#     logger.info('reading sc output file (smdim={}, analysis={})...'.format(smdim, analysis))

#     if analysis == 0 or analysis == 'h' or analysis == '':
#         # Read homogenization results
#         if not fn_in.lower()[-2:] == '.k':
#             fn_in = fn_in + '.k'
#         return readSCOutHomo(fn_in, smdim, scrnout)

#     elif analysis == 1 or analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
#         pass

#     elif (analysis.startswith('f')) or (analysis >= 3):
#         return readSCOutFailure(fn_in+'.fi', analysis)



















# ====================================================================

def readSGInterfacePairs(fn):
    r"""
    """

    # if logger is None:
    #     logger = mul.initLogger(__name__)

    logger.debug('reading sg interface paris: {0}...'.format(fn))

    itf_pairs = []

    with open(fn, 'r') as fobj:
        for li, line in enumerate(fobj):
            line = line.strip()
            if line == '\n' or line == '':
                continue

            line = line.split()

            _pair = [
                int(line[1]), int(line[2]),
                float(line[3]), float(line[4]),
                float(line[5]), float(line[6])
            ]

            itf_pairs.append(_pair)

    return itf_pairs









def readSGInterfaceNodes(fn):
    """
    """

    # if logger is None:
    #     logger = mul.initLogger(__name__)

    logger.debug('reading sg interface nodes: {0}...'.format(fn))

    itf_nodes = []

    with open(fn, 'r') as fobj:
        for li, line in enumerate(fobj):
            line = line.strip()
            if line == '\n' or line == '':
                continue

            line = line.split()

            _nodes = []
            for nid in line[1:]:
                _nodes.append(int(nid))

            itf_nodes.append(_nodes)

    return itf_nodes









# ====================================================================

def readLoadCsv(
    fn:str, smdim:int, model:int, load_tags=[], load_type=0,
    disp_tags=['u1', 'u2', 'u3'],
    rot_tags = ['c11', 'c12', 'c13', 'c21', 'c22', 'c23', 'c31', 'c32', 'c33'],
    loc_tags=['loc',], cond_tags=[],
    loc_vtypes=[], cond_vtypes=[],
    delimiter=',', nhead=1, encoding='utf-8-sig'
    ):
    """
    """

    logger.debug('reading structural response file {}...'.format(fn))

    if len(load_tags) == 0:
        if smdim == 1:
            if model == 'b1':
                load_tags = ['f1', 'm1', 'm2', 'm3']
            elif model == 'b2':
                load_tags = ['f1', 'f2', 'f3', 'm1', 'm2', 'm3']

    if isinstance(loc_tags, str):
        loc_tags = [loc_tags,]
    if isinstance(cond_tags, str):
        cond_tags = [cond_tags,]

    if isinstance(loc_vtypes, str):
        loc_vtypes = [loc_vtypes,]
    if isinstance(cond_vtypes, str):
        cond_vtypes = [cond_vtypes,]

    if len(loc_vtypes) < len(loc_tags):
        if len(loc_vtypes) == 0:
            loc_vtypes = ['int',] * len(loc_tags)
        elif len(loc_vtypes) == 1:
            loc_vtypes = loc_vtypes * len(loc_tags)
    if len(cond_vtypes) < len(cond_tags):
        if len(cond_vtypes) == 0:
            cond_vtypes = ['int',] * len(cond_tags)
        elif len(cond_vtypes) == 1:
            cond_vtypes = cond_vtypes * len(cond_tags)

    struct_resp_cases = sgmodel.StructureResponseCases()
    struct_resp_cases.loc_tags = loc_tags
    struct_resp_cases.cond_tags = cond_tags

    # load = {}

    with open(fn, 'r', encoding=encoding) as file:
        cr = csv.reader(file, delimiter=delimiter)

        tags_idx = {}
        # loc_tags_idx = {}
        # case_tags_idx = {}
        # disp_tags_idx = {}
        # rot_tags_idx = {}
        # load_tags_idx = {}

        hi = 0
        for i, row in enumerate(cr):
            row = [s.strip() for s in row]
            if row[0] == '':
                continue

            if i < nhead:
                if hi == 0:
                    # Get index of each tag
                    for _tag in loc_tags:
                        tags_idx[_tag] = row.index(_tag)
                    for _tag in cond_tags:
                        tags_idx[_tag] = row.index(_tag)
                    for _tag in disp_tags:
                        tags_idx[_tag] = row.index(_tag)
                    for _tag in rot_tags:
                        tags_idx[_tag] = row.index(_tag)
                    for _tag in load_tags:
                        tags_idx[_tag] = row.index(_tag)
                    # print(tags_idx)
                hi += 1
                continue
                # # Read head
                # for label in row:
                #     if label.lower().startswith('rotor'):
                #         nid = int(label.split('NODE')[1])
                #         load['node_id'].append(nid)

            else:
                resp_case = {}

                sect_resp = sgmodel.SectionResponse()

                sect_resp.load_type = load_type
                sect_resp.load_tags = load_tags

                # Read location ids
                for _tag, _type in zip(loc_tags, loc_vtypes):
                    _i = tags_idx[_tag]
                    resp_case[_tag] = eval(_type)(row[_i])

                # Read case ids
                for _tag, _type in zip(cond_tags, cond_vtypes):
                    _i = tags_idx[_tag]
                    resp_case[_tag] = eval(_type)(row[_i])

                # Read loads
                _load = []
                for _tag in load_tags:
                    _i = tags_idx[_tag]
                    _load.append(float(row[_i]))
                sect_resp.load = _load

                # Read displacements
                _disp = []
                for _tag in disp_tags:
                    _i = tags_idx[_tag]
                    _disp.append(float(row[_i]))
                sect_resp.displacement = _disp

                # Read rotations
                _rot = []
                for _tag in rot_tags:
                    _i = tags_idx[_tag]
                    _rot.append(float(row[_i]))
                sect_resp.directional_cosine = [
                    _rot[:3], _rot[3:6], _rot[6:]
                ]

                resp_case['response'] = sect_resp

                # condition = str(row[0])
                # if not condition in load.keys():
                #     load[condition] = {
                #         'fx': {'a': [], 'r': [], 'v': []},
                #         'fy': {'a': [], 'r': [], 'v': []},
                #         'fz': {'a': [], 'r': [], 'v': []},
                #         'mx': {'a': [], 'r': [], 'v': []},
                #         'my': {'a': [], 'r': [], 'v': []},
                #         'mz': {'a': [], 'r': [], 'v': []}
                #     }

                # a, r, fx, fy, fz, mx, my, mz = list(map(float, row[1:]))
                # v = {
                #     'fx': fx, 'fy': fy, 'fz': fz,
                #     'mx': mx, 'my': my, 'mz': mz
                # }

                # azimuth.append(a)

                # for component in ['fx', 'fy', 'fz', 'mx', 'my', 'mz']:
                #     load[condition][component]['a'].append(a)
                #     load[condition][component]['r'].append(r)
                #     load[condition][component]['v'].append(v[component])

                struct_resp_cases.responses.append(resp_case)

    # azimuth = list(set(azimuth))

    return struct_resp_cases









# def readLoadCsv(fn, delimiter=',', nhead=1, encoding='utf-8-sig'):
#     r"""
#     load = {
#         'flight_condition_1': {
#             'fx': {
#                 'a': [],
#                 'r': [],
#                 'v': []
#             },
#             'fy': [],
#             'fz': [],
#             'mx', [],
#             'my', [],
#             'mz', []
#         },
#         'flight_condition_2': {},
#         ...
#     }
#     """

#     load = {}
#     azimuth = []

#     with open(fn, 'r', encoding=encoding) as file:
#         cr = csv.reader(file, delimiter=delimiter)

#         for i, row in enumerate(cr):
#             row = [s.strip() for s in row]
#             if row[0] == '':
#                 continue

#             if i < nhead:
#                 continue
#                 # # Read head
#                 # for label in row:
#                 #     if label.lower().startswith('rotor'):
#                 #         nid = int(label.split('NODE')[1])
#                 #         load['node_id'].append(nid)

#             else:
#                 condition = str(row[0])
#                 if not condition in load.keys():
#                     load[condition] = {
#                         'fx': {'a': [], 'r': [], 'v': []},
#                         'fy': {'a': [], 'r': [], 'v': []},
#                         'fz': {'a': [], 'r': [], 'v': []},
#                         'mx': {'a': [], 'r': [], 'v': []},
#                         'my': {'a': [], 'r': [], 'v': []},
#                         'mz': {'a': [], 'r': [], 'v': []}
#                     }

#                 a, r, fx, fy, fz, mx, my, mz = list(map(float, row[1:]))
#                 v = {
#                     'fx': fx, 'fy': fy, 'fz': fz,
#                     'mx': mx, 'my': my, 'mz': mz
#                 }

#                 azimuth.append(a)

#                 for component in ['fx', 'fy', 'fz', 'mx', 'my', 'mz']:
#                     load[condition][component]['a'].append(a)
#                     load[condition][component]['r'].append(r)
#                     load[condition][component]['v'].append(v[component])

#     azimuth = list(set(azimuth))

#     return load, azimuth
