from __future__ import annotations

import logging

import meshio

import sgio._global as GLOBAL
import sgio.iofunc._meshio as _meshio
import sgio.iofunc.abaqus as _abaqus
import sgio.iofunc.gmsh as _gmsh
import sgio.iofunc.swiftcomp as _swiftcomp
import sgio.iofunc.vabs as _vabs
import sgio.model as sgmodel
from sgio.core import StructureGene

from ._mesh_convert import (
    mesh_to_sg as _mesh_to_sg,
    parse_model_type as _parse_model_type,
    restore_sg_from_mesh_extras as _restore_sg_from_mesh_extras,
)
from ._read_output_swiftcomp import read_swiftcomp_output_state as _read_swiftcomp_output_state
from ._read_output_vabs import read_vabs_output_state as _read_vabs_output_state
from .utils import (
    infer_section_dimension,
    read_load_csv,
    read_sg_interface_pairs,
    read_sg_interface_nodes,
)

logger = logging.getLogger(__name__)


def read_output_state(
    filename: str, file_format: str, analysis: str, model_type: str = "",
    extension: str | list[str] = "ele", sg: StructureGene | None = None,
    tool_version: str = "", num_cases: int = 1, num_elements: int = 0,
    **kwargs
) -> list[sgmodel.StateCase] | None:
    """Read SG dehomogenization or failure analysis output.

    Parameters
    ----------
    filename : str
        Name of the SG analysis output file.
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
    extension : str or list of str, optional
        Extension(s) of the output data to read. Default is ``'ele'``.
        One or more of:

        * ``'u'``: Displacement
        * ``'ele'``: Element strain and stress (VABS)
        * ``'sn'`` / ``'snm'``: Element-node strain/stress in beam/material
          coordinate system (SwiftComp)
    sg : StructureGene, optional
        Structure gene object.
    tool_version : str, optional
        Solver tool version (e.g. ``'4'``, ``'5'`` for VABS).
    num_cases : int, optional
        Number of load cases. Default is 1.
    num_elements : int, optional
        Number of elements; ``0`` falls back to ``sg.nelems``.

    Returns
    -------
    list[StateCase] or None
        List of state cases per load case, or ``None`` on parse failure.
    """
    logger.debug('reading output state...')
    logger.debug(locals())

    if not isinstance(extension, list):
        extension = [extension]
    extension = [e.lower() for e in extension]

    if file_format.lower().startswith("s"):
        return _read_swiftcomp_output_state(
            filename, analysis, model_type, extension,
            num_cases, num_elements, sg, **kwargs
        )
    if file_format.lower().startswith("v"):
        return _read_vabs_output_state(
            filename, analysis, extension, num_cases,
            num_elements, sg, tool_version, **kwargs
        )
    raise ValueError(f"Unsupported file format: {file_format}")


def read(
    filename: str,
    file_format: str,
    model_type: str = 'SD1',
    format_version: str = '',
    sgdim: int = 3,
    sg: StructureGene | None = None,
    **kwargs
) -> StructureGene:
    """Read SG data file.

    Parameters
    ----------
    filename : str
        Name of the SG data file.
    file_format : str
        Format of the SG data file.
        Choose one from 'abaqus', 'vabs', 'sc', 'swiftcomp', 'gmsh'.
    model_type : str
        Type of the macro structural model.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    format_version : str, optional
        Version of the format.
    sgdim : int, optional
        Dimension of the geometry. Default is 3.
        Choose one from 1, 2, 3.
    sg : StructureGene, optional
        Pre-built structure gene object (if not given, one is constructed).

    Returns
    -------
    StructureGene
        The parsed structure gene object.
    """
    logger.info('Reading file...')
    logger.debug(locals())

    file_format = file_format.lower()
    if file_format == 'sc' or file_format == 'swiftcomp':
        with open(filename, 'r') as file:
            sg = _swiftcomp.read_input_buffer(
                file, format_version, model_type
            )
    elif file_format == 'vabs':
        with open(filename, 'r') as file:
            sg = _vabs.read_buffer(
                file, format_version
            )
    elif file_format == 'abaqus':
        sg = _abaqus.read(
            filename, sgdim=sgdim, model=model_type
        )
    elif file_format == 'gmsh':
        with open(filename, 'rb') as file:
            mesh = _gmsh.read_buffer(file, format_version=format_version)
        sg = _mesh_to_sg(mesh, sgdim=sgdim, model_type=model_type)
        _restore_sg_from_mesh_extras(sg, mesh)
    else:
        raise ValueError(f"Unknown file format: {file_format}")

    if not sg:
        # smdim must be int; model_type is a string like 'SD1' — parse it.
        smdim, submodel = _parse_model_type(model_type)
        sg = StructureGene(sgdim=sgdim, smdim=smdim)
        sg.model = submodel
    if not sg.mesh:
        sg.mesh, _, _ = _meshio.read(filename, file_format)

    return sg


def read_output_model(
    filename: str, file_format: str, model_type: str = "",
    sg: StructureGene | None = None, **kwargs
) -> sgmodel.Model | None:
    """Read SG homogenization output file.

    Parameters
    ----------
    filename : str
        Name of the SG analysis output file.
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    model_type : str
        Type of the macro structural model.
    sg : StructureGene, optional
        SG object.

    Returns
    -------
    Model or None
        Constitutive model parsed from the homogenization output, or None
        if the file cannot be opened.
    """
    try:
        file_obj = open(filename, "r")
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return None

    with file_obj as file:
        if file_format.lower().startswith("s"):
            return _swiftcomp.read_output_buffer(
                file, analysis="h", model_type=model_type, sg=sg, **kwargs
            )
        if file_format.lower().startswith("v"):
            return _vabs.read_output_buffer(
                file, analysis="h", sg=sg, model_type=model_type, **kwargs
            )
        raise ValueError(f"Unsupported file format: {file_format}")


def read_output(
    filename: str, file_format: str, analysis: str = 'h', model_type: str = '',
    sg: StructureGene | None = None, **kwargs
) -> sgmodel.Model | sgmodel.StateCase | None:
    """Read SG analysis output file.

    Thin dispatcher that delegates to :func:`read_output_model` (for
    ``analysis='h'``) or :func:`read_output_state` (for ``analysis='d'``,
    ``'l'``, ``'fi'``). Prefer those canonical APIs in new code; this entry
    point is kept for backward compatibility.

    Parameters
    ----------
    filename : str
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
    sg : StructureGene, optional
        Structure gene object.

    Returns
    -------
    Model
        If `analysis` is 'h', the constitutive model.
    StateCase
        If `analysis` is 'd' or 'l', the (single) state case.
    object
        If `analysis` is 'fi', the failure-index payload returned by the
        underlying solver-specific reader.
    None
        If the file cannot be opened or the format is unsupported.
    """
    if analysis == 'h':
        return read_output_model(
            filename, file_format, model_type=model_type, sg=sg, **kwargs
        )

    if analysis == 'fi':
        fi_filename = f'{filename}.fi'
        if file_format.lower().startswith('s'):
            with open(fi_filename, 'r') as file:
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type, **kwargs
                )
        if file_format.lower().startswith('v'):
            with open(fi_filename, 'r') as file:
                return _vabs.read_output_buffer(file, analysis, sg, **kwargs)
        return None

    if analysis in ('d', 'l'):
        state_cases = read_output_state(
            filename, file_format, analysis,
            model_type=model_type, extension=['u', 'ele'],
            sg=sg, num_cases=1, **kwargs,
        )
        if not state_cases:
            return None
        return state_cases[0]

    return None


def write(
    sg: StructureGene, filename: str, file_format: str,
    format_version: str = '', analysis: str = 'h', sg_format: int = 1,
    model_space: str = '', prop_ref_y: str = 'x',
    macro_responses: list[sgmodel.StateCase] | None = None, model_type: str = 'SD1',
    load_type: int = 0, sfi: str = '8d', sff: str = '20.12e', mesh_only: bool = False,
    binary: bool = False
) -> str:
    """Write analysis input.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object.
    filename : str
        Name of the input file.
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp', 'gmsh'.
    format_version : str, optional
        Version of the format. Default is ``''``.
    analysis : str, optional
        Indicator of SG analysis.
        Default is ``'h'``.
        Choose one from

        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    sg_format : {0, 1}, optional
        Format for the VABS input. Default is 1.
    model_space : str, optional
        Macro model space orientation; passed through to solver writer.
    prop_ref_y : str, optional
        Reference axis selector for material orientation. Default is ``'x'``.
    macro_responses : list[StateCase], optional
        Macroscopic responses. Default is ``None`` (treated as empty).
    model_type : str, optional
        Type of the macro structural model. Default is ``'SD1'``.
    load_type : int, optional
        Type of the load. Default is 0.
    sfi : str, optional
        String formatting for integers. Default is ``'8d'``.
    sff : str, optional
        String formatting for floats. Default is ``'20.12e'``.
    mesh_only : bool, optional
        If True, write meshing data only. Default is False.
    binary : bool, optional
        For Gmsh output, write binary instead of ASCII. Default is False.

    Returns
    -------
    str
        The output filename.
    """
    logger.info('Writing file...')
    logger.debug(locals())

    if macro_responses is None:
        macro_responses = []
    if file_format not in ['sc', 'swiftcomp', 'vabs']:
        mesh_only = True

    if sg is None:
        raise ValueError('structure_gene is None')
    if sg.mesh is None:
        raise ValueError('structure_gene.mesh is None')

    with open(filename, 'w', encoding='utf-8') as file:
        if file_format.startswith('s'):
            if format_version == '':
                format_version = GLOBAL.SC_VERSION_DEFAULT

            _swiftcomp.write_buffer(
                sg, file,
                analysis=analysis, model=model_type,
                macro_responses=macro_responses,
                model_space=model_space, prop_ref_y=prop_ref_y,
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
                model_space=model_space, prop_ref_y=prop_ref_y,
                sfi=sfi, sff=sff, version=format_version,
                mesh_only=mesh_only
            )

        elif file_format.startswith('gmsh'):
            material_id_map = sg.get_export_material_ids() if sg.mocombos else {}
            sg_configs = {'sgdim': infer_section_dimension(sg)}
            if sg.smdim is not None:
                sg_configs['model'] = sg.model
            sg_configs['do_damping'] = sg.do_damping
            sg_configs['thermal'] = sg.physics

            _gmsh.write_buffer(
                file,
                sg.mesh,
                format_version=format_version,
                float_fmt=sff,
                sgdim=sg_configs['sgdim'],
                mesh_only=mesh_only,
                binary=binary,
                mocombos=sg.mocombos if sg.mocombos else None,
                material_id_map=material_id_map,
                sg_configs=sg_configs,
            )

        else:
            meshio.write(
                file, sg.mesh, file_format=file_format,
                int_fmt=sfi, float_fmt=sff)

    return filename


def convert_file_format(
    file_name_in: str,
    file_name_out: str,
    file_format_in: str,
    file_format_out: str,
    file_version_in: str = '',
    file_version_out: str = '',
    analysis: str = 'h',
    sgdim: int = 3,
    model_space: str = 'xy',
    prop_ref_y: str = 'x',
    model_type: str = 'SD1',
    vabs_format_version: int = 1,
    str_format_int: str = '8d',
    str_format_float: str = '20.12e',
    mesh_only: bool = False,
    renum_node: bool = False,
    renum_elem: bool = False
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
    renum_elem : bool, optional
        If renumber elements, by default False
    """

    logger.info('Converting file format...')
    logger.debug(locals())

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

    if renum_node or renum_elem:
        logger.warning(
            "Parameters renum_node/renum_elem are deprecated and ignored. "
            "Numbering is now handled automatically based on format requirements."
        )

    write(
        sg=sg,
        filename=file_name_out,
        file_format=file_format_out,
        format_version=file_version_out,
        analysis=analysis,
        sg_format=vabs_format_version,
        model_space=model_space,
        prop_ref_y=prop_ref_y,
        model_type=model_type,
        sfi=str_format_int,
        sff=str_format_float,
        mesh_only=mesh_only)

    logger.info('File format converted.')

    return sg


# Backward compatibility alias.
convert = convert_file_format


__all__ = [
    'read',
    'read_output',
    'read_output_model',
    'read_output_state',
    'read_load_csv',
    'write',
    'convert',
    'convert_file_format',
]
