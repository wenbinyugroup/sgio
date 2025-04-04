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
    filename: str,
    file_format: str,
    model_type: str = 'SD1',
    format_version: str = '',
    sgdim: int = 3,
    sg: StructureGene = None,
    **kwargs
) -> StructureGene:
    """Read SG data file.

    Parameters
    ----------
    filename : str
        Name of the SG data file
    file_format : str
        Format of the SG data file.
        Choose one from 'abaqus', 'vabs', 'sc', 'swiftcomp'.
    model_type : str
        Type of the macro structural model.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    format_version : str
        Version of the format
    sgdim : int
        Dimension of the geometry. Default is 3.
        Choose one from 1, 2, 3.
    sg : :obj:`sgio.core.sg.StructureGene`, optional
        Structure gene object

    Returns
    -------
    :obj:`sgio.core.sg.StructureGene`
        Structure gene object
    """
    # sutils.check_file_exists(filename)
    file_format = file_format.lower()
    if file_format == 'sc' or file_format == 'swiftcomp':
        with open(filename, 'r') as file:
            sg = _swiftcomp.read_input_buffer(
                file, format_version, model_type
            )
    elif file_format == 'vabs':
        with open(filename, 'r') as file:
            sg = _vabs.read_buffer(
                file, file_format, format_version, model_type
            )
    elif file_format == 'abaqus':
        with open(filename, 'r') as file:
            sg = _abaqus.read_input_buffer(
                file, sgdim=sgdim, model=model_type
            )
    else:
        raise ValueError(f"Unknown file format: {file_format}")

    if not sg:
        sg = StructureGene(sgdim=sgdim, smdim=model_type)
    if not sg.mesh:
        sg.mesh, _, _ = meshio.read(filename, file_format)

    return sg




def readOutputModel(
    filename: str, file_format: str, model_type: str = "", sg: StructureGene = None,
    **kwargs
):
    """Read SG homogenization output file.

    Parameters
    ----------
    filename : str
        Name of the SG analysis output file
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    model_type : str
        Type of the macro structural model.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    sg : StructureGene, optional
        SG object.

    Returns
    -------
    Model
        If `analysis` is 'h', return the consitutive model.
    """

    model = None
    try:
        with open(filename, "r") as file:
            if file_format.lower().startswith("s"):
                model = _swiftcomp.read_output_buffer(
                    file, analysis="h", model_type=model_type, **kwargs
                )
            elif file_format.lower().startswith("v"):
                model = _vabs.read_output_buffer(
                    file, analysis="h", sg=sg, model_type=model_type, **kwargs
                )
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
    except Exception as e:
        logger.error(f"Error: {e}")

    return model




def readOutputState(
    filename: str, file_format: str, analysis: str, model_type: str = "",
    extension: str = "ele", sg: StructureGene = None, tool_version: str = "",
    num_cases: int = 1, num_elements: int = 0, **kwargs
) -> sgmodel.StateCase:
    """Read SG dehomogenization or failure analysis output.

    Parameters
    ----------
    filename : str
        Name of the SG analysis output file
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    analysis : str
        Indicator of SG analysis.
        Choose one from

        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    model_type : str
        Type of the macro structural model.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    extension : str or list of str
        Extension of the output data.
        Default is 'ele'.
        Include one or more of the following keywords:

        * 'u': Displacement
        * 'ele': Element strain and stress
    sg : StructureGene
        Structure gene object
    tool_version : str
        Version of the tool
    num_cases : int
        Number of load cases

    Returns
    -------
    StateCase
        State case object
    """

    state_case = sgmodel.StateCase()

    if analysis == "fi":
        # Read failure index
        if file_format.lower().startswith("s"):
            with open(f"{filename}.fi", "r") as file:
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type, **kwargs
                )

        elif file_format.lower().startswith("v"):
            with open(f"{filename}.fi", "r") as file:
                try:
                    fi, sr, eids_sr_min = _vabs.read_output_buffer(
                        file, analysis, sg, tool_version=tool_version,
                        num_cases=num_cases, num_elements=num_elements, **kwargs
                    )
                except Exception as e:
                    logger.error(f"Error: {e}")
                    return None
            if fi is None or sr is None:
                logger.error("Error: No data read")
                return None
            state_case.addState(
                name="fi", state=sgmodel.State(
                    name="fi", data=fi, label=["fi"], location="element"
                )
            )
            state_case.addState(
                name="sr", state=sgmodel.State(
                    name="sr", data=sr, label=["sr"], location="element"
                )
            )
            sr_min = {}
            for eid in eids_sr_min:
                sr_min[eid] = sr[eid]
            state_case.addState(
                name="sr_min", state=sgmodel.State(
                    name="sr_min", data=sr_min, label=["sr_min"], location="element"
                )
            )

    elif analysis == "d" or analysis == "l":
        # Read dehomogenization output
        if file_format.lower().startswith("s"):
            pass

        elif file_format.lower().startswith("v"):
            if not isinstance(extension, list):
                extension = [extension,]
            extension = [e.lower() for e in extension]

            # Displacement
            if "u" in extension:
                u = None
                with open(f"{filename}.U", "r") as file:
                    try:
                        u = _vabs.read_output_buffer(file, analysis, extension="u", **kwargs)
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        return None
                if u is None:
                    logger.error("Error: No data read")
                    return None
                state_case.addState(
                    name="u", state=sgmodel.State(
                        name="u", data=u, label=["u1", "u2", "u3"], location="node"
                    )
                )

            # Element strain and stress
            if "ele" in extension:
                ee, es, eem, esm = None, None, None, None
                with open(f"{filename}.ELE", "r") as file:
                    try:
                        ee, es, eem, esm = _vabs.read_output_buffer(
                            file, analysis, sg=sg, extension="ele", tool_version=tool_version,
                            num_cases=num_cases, num_elements=num_elements, **kwargs
                        )
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        return None
                if ee is None or es is None or eem is None or esm is None:
                    logger.error("Error: No data read")
                    return None
                state_case.addState(
                    name="ee", state=sgmodel.State(
                        name="ee", data=ee, label=["e11", "2e12", "2e13", "e22", "2e23", "e33"], location="element"
                    )
                )
                state_case.addState(
                    name="es", state=sgmodel.State(
                        name="es", data=es, label=["s11", "s12", "s13", "s22", "s23", "s33"], location="element"
                    )
                )
                state_case.addState(
                    name="eem", state=sgmodel.State(
                        name="eem", data=eem, label=["em11", "2em12", "2em13", "em22", "2em23", "em33"], location="element"
                    )
                )
                state_case.addState(
                    name="esm", state=sgmodel.State(
                        name="esm", data=esm, label=["sm11", "sm12", "sm13", "sm22", "sm23", "sm33"], location="element"
                    )
                )

    return state_case




def readOutput(
    fn, file_format, analysis='h', model_type='',
    sg=None, **kwargs
    ):
    """Read SG analysis output file.

    Parameters
    ----------
    fn : str
        Name of the SG analysis output file.
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    analysis : str, optional
        Indicator of SG analysis.
        Default is 'h'.
        Choose one from
        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    model_type : str
        Type of the macro structural model.
        Choose one from
        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    sg : :obj:`StructureGene`
        Structure gene object

    Returns
    -------
    Model
        If `analysis` is 'h', return the consitutive model.
        * :obj:`EulerBernoulliBeamModel` if `model_type` is 'BM1'
        * :obj:`TimoshenkoBeamModel` if `model_type` is 'BM2'
        * :obj:`KirchhoffLovePlateModel` if `model_type` is 'PL1' and `file_format` is 'sc' or 'swiftcomp'
        * :obj:`ReissnerMindlinPlateModel` if `model_type` is 'PL2' and `file_format` is 'sc' or 'swiftcomp'
        * :obj:`CauchyContinuumModel` if `model_type` is 'SD1' and `file_format` is 'sc' or 'swiftcomp'
    StateCase
        If `analysis` is 'd' or 'l', return the state case.
    """

    # print(f'reading {file_format} output file {fn}...')
    # print(f'file_format: {file_format}, analysis: {analysis}, smdim: {smdim}...')

    if analysis == 'h':
        with open(fn, 'r') as file:
            if file_format.lower().startswith('s'):
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)
            elif file_format.lower().startswith('v'):
                return _vabs.read_output_buffer(
                    file, analysis, sg, model_type=model_type,
                    **kwargs)

    elif analysis == 'fi':
        if file_format.lower().startswith('s'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)
        elif file_format.lower().startswith('v'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                return _vabs.read_output_buffer(file, analysis, sg, **kwargs)

    elif analysis == 'd' or analysis == 'l':
        if file_format.lower().startswith('s'):
            pass

        elif file_format.lower().startswith('v'):
            state_case = sgmodel.StateCase()

            # Displacement
            _u = None
            _fn = f'{fn}.U'
            with open(_fn, 'r') as file:
                _u = _vabs.read_output_buffer(file, analysis, ext='u', **kwargs)
            _state = sgmodel.State(
                name='u', data=_u, label=['u1', 'u2', 'u3'], location='node')
            state_case.addState(name='u', state=_state)

            # Element strain and stress
            _ee, _es, _eem, _esm = None, None, None, None
            _fn = f'{fn}.ELE'
            with open(_fn, 'r') as file:
                _ee, _es, _eem, _esm = _vabs.read_output_buffer(file, analysis, ext='ele', **kwargs)
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
    sg: StructureGene, fn: str, file_format: str,
    format_version: str = '', analysis: str = 'h', sg_format: int = 1,
    macro_responses: list[sgmodel.StateCase] = [], model_type: str = 'SD1',
    load_type: int = 0, sfi: str = '8d', sff: str = '20.12e', mesh_only: bool = False
) -> str:
    """Write analysis input

    Parameters
    ----------
    sg : StructureGene
        Structure gene object
    fn : str
        Name of the input file
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    format_version : str, optional
        Version of the format. Default is ''
    analysis : str, optional
        Indicator of SG analysis.
        Default is 'h'.
        Choose one from

        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    sg_format : {0, 1}, optional
        Format for the VABS input. Default is 1
    macro_responses : list[StateCase], optional
        Macroscopic responses. Default is `[]`.
    model_type : str
        Type of the macro structural model.
        Default is 'SD1'.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    load_type : int, optional
        Type of the load. Default is 0
    sfi
        String formating integers. Default is '8d'
    sff
        String formating floats. Default is '20.12e'
    mesh_only
        If write meshing data only. Default is False
    """

    # Check if file_format is valid
    if file_format not in ['sc', 'swiftcomp', 'vabs']:
        mesh_only = True

    # Check if structure_gene is valid
    if sg is None:
        raise ValueError('structure_gene is None')

    # Check if structure_gene.mesh is valid
    if sg.mesh is None:
        raise ValueError('structure_gene.mesh is None')

    # Open the file and write the data
    with open(fn, 'w', encoding='utf-8') as file:
        if mesh_only:
            sg.mesh.write(
                file,
                file_format,
                int_fmt=sfi,
                float_fmt=sff
            )

        else:
            if file_format.startswith('s'):
                if format_version == '':
                    format_version = GLOBAL.SC_VERSION_DEFAULT

                _swiftcomp.write_buffer(
                    sg, file,
                    analysis=analysis, model=model_type,
                    macro_responses=macro_responses,
                    load_type=load_type,
                    sfi=sfi, sff=sff, version=format_version
                )

            elif file_format.startswith('v'):
                if format_version == '':
                    format_version = GLOBAL.VABS_VERSION_DEFAULT

                _vabs.write_buffer(
                    sg, file,
                    analysis=analysis, sg_format=sg_format,
                    macro_responses=macro_responses, model=model_type,
                    sfi=sfi, sff=sff, version=format_version,
                    mesh_only=mesh_only
                )

    return fn




def convert(
    file_name_in: str,
    file_name_out: str,
    file_format_in: str,
    file_format_out: str,
    file_version_in: str = '',
    file_version_out: str = '',
    analysis: str = 'h',
    sgdim: int = 3,
    model_type: str = 'SD1',
    vabs_format_version: int = 1,
    str_format_int: str = '8d',
    str_format_float: str = '20.12e',
    mesh_only: bool = False
) -> StructureGene:
    """Convert the Structure Gene data file format.

    Parameters
    ----------
    file_name_in : str
        File name before conversion
    file_name_out : str
        File name after conversion
    file_format_in : str
        Format of the input file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    file_format_out : str
        Format of the output file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    file_version_in : str, optional
        Version of the input file, by default ''
    file_version_out : str, optional
        Version of the output file, by default ''
    analysis : str, optional
        Indicator of Structure Gene analysis.
        Default is 'h'.
        Choose one from

        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    sgdim : int
        Dimension of the geometry. Default is 3.
        Choose one from 1, 2, 3.
    model_type : str
        Type of the macro structural model.
        Default is 'SD1'.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    vabs_format_version : int, optional
        Format for the VABS input, by default 1
    str_format_int : str, optional
        String formating integers, by default '8d'
    str_format_float : str, optional
        String formating floats, by default '20.12e'
    mesh_only : bool, optional
        If write meshing data only, by default False
    """

    if file_name_in is None:
        raise ValueError("Input file name should not be None.")

    if file_name_out is None:
        raise ValueError("Output file name should not be None.")

    sg = read(
        filename=file_name_in,
        file_format=file_format_in,
        model_type=model_type,
        format_version=file_version_in,
        sgdim=sgdim,
        mesh_only=mesh_only)

    if sg is None:
        raise ValueError("Input file is not a valid SG file.")

    write(
        sg=sg,
        fn=file_name_out,
        file_format=file_format_out,
        format_version=file_version_out,
        analysis=analysis,
        sg_format=vabs_format_version,
        model_type=model_type,
        sfi=str_format_int,
        sff=str_format_float,
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
    """
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
    fn: str, smdim: int, model: int, load_tags: list = [],
    load_type: int = 0, disp_tags: list = ['u1', 'u2', 'u3'],
    rot_tags: list = ['c11', 'c12', 'c13', 'c21', 'c22', 'c23', 'c31', 'c32', 'c33'],
    loc_tags: list = ['loc',], cond_tags: list = [],
    loc_vtypes: list = [], cond_vtypes: list = [],
    delimiter: str = ',', nhead: int = 1, encoding: str = 'utf-8-sig'
) -> sgmodel.StructureResponseCases:
    """
    Reads a CSV file containing load data for a given structure.
    The file should have the following format:

    loc, cond, u1, u2, u3, c11, c12, c13, c21, c22, c23, c31, c32, c33, f1, f2, ...
    1, 1, 1, 2, 3, 0, 0, 1, 0, 1, 0, 0, 0, 1, 4, 5, ...

    Parameters
    ----------
    fn : str
        The filename of the CSV file to read.
    smdim : int
        The dimension of the structure model.
    model : int
        The model type of the structure.
    load_tags : list, optional
        The tags of the loads to be read. Defaults to an empty list.
    load_type : int, optional
        The type of the loads. Defaults to 0.
    disp_tags : list, optional
        The tags of the displacements to be read. Defaults to ['u1', 'u2', 'u3'].
    rot_tags : list, optional
        The tags of the rotations to be read. Defaults to ['c11', 'c12', 'c13', 'c21', 'c22', 'c23', 'c31', 'c32', 'c33'].
    loc_tags : list, optional
        The tags of the locations to be read. Defaults to ['loc',].
    cond_tags : list, optional
        The tags of the conditions to be read. Defaults to an empty list.
    loc_vtypes : list, optional
        The value types of the locations to be read. Defaults to an empty list.
    cond_vtypes : list, optional
        The value types of the conditions to be read. Defaults to an empty list.
    delimiter : str, optional
        The delimiter of the CSV file. Defaults to ','.
    nhead : int, optional
        The number of header lines to skip. Defaults to 1.
    encoding : str, optional
        The encoding of the CSV file. Defaults to 'utf-8-sig'.

    Returns
    -------
    struct_resp_cases : StructureResponseCases
        The structure response cases.
    """

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

    with open(fn, 'r', encoding=encoding) as file:
        cr = csv.reader(file, delimiter=delimiter)

        tags_idx = {}

        hi = 0
        for i, row in enumerate(cr):
            row = [s.strip() for s in row]
            if row[0] == '':
                continue

            if i < nhead:
                if hi == 0:
                    for tag in loc_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in cond_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in disp_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in rot_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in load_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                hi += 1
                continue

            else:
                resp_case = {}

                sect_resp = sgmodel.SectionResponse()

                sect_resp.load_type = load_type
                sect_resp.load_tags = load_tags

                for tag, vtype in zip(loc_tags, loc_vtypes):
                    sect_resp.loc[tag] = eval(vtype)(row[tags_idx[tag]])

                for tag, vtype in zip(cond_tags, cond_vtypes):
                    sect_resp.cond[tag] = eval(vtype)(row[tags_idx[tag]])

                sect_resp.load = [float(row[tags_idx[tag]]) for tag in load_tags]
                sect_resp.displacement = [float(row[tags_idx[tag]]) for tag in disp_tags]
                sect_resp.directional_cosine = [
                    [float(row[tags_idx[tag]]) for tag in rot_tags[0:3]],
                    [float(row[tags_idx[tag]]) for tag in rot_tags[3:6]],
                    [float(row[tags_idx[tag]]) for tag in rot_tags[6:9]]
                ]

                resp_case['response'] = sect_resp
                struct_resp_cases.responses.append(resp_case)

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
