from __future__ import annotations

import logging
from pathlib import Path

import sgio.iofunc.swiftcomp as _swiftcomp
import sgio.iofunc.vabs as _vabs
import sgio.model as sgmodel
from sgio._exceptions import IncompleteModelDataError
from sgio.core import FEModel, StructureGene

from .base import get_format_registry
from .sg_manifest import WRITABLE_MODEL_FILE_FORMATS, model_type_of, write_sg_manifest
from ._mesh_convert import (
    parse_model_type as _parse_model_type,
)
from ._read_output_swiftcomp import read_swiftcomp_output_state as _read_swiftcomp_output_state
from ._read_output_vabs import read_vabs_output_state as _read_vabs_output_state
from .utils import (
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
) -> list[sgmodel.StateCase]:
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
    list[StateCase]
        List of state cases per load case. Raises on parse failure.
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
    model_type: str | None = None,
    format_version: str = '',
    sgdim: int | None = None,
    sg: StructureGene | None = None,
    model_space: str | None = None,
    **kwargs
) -> StructureGene:
    """Read SG data file.

    Parameters
    ----------
    filename : str
        Name of the SG data file.
    file_format : str
        Format of the SG data file.
        Choose one from 'abaqus', 'vabs', 'sc', 'swiftcomp', 'gmsh',
        'sg_manifest'.
    model_type : str, optional
        Type of the macro structural model. Required for 'abaqus' and
        'swiftcomp'; for 'sg_manifest' it must agree with the manifest.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    format_version : str, optional
        Version of the format.
    sgdim : int, optional
        Dimension of the geometry. Required for 'abaqus'; for 'sg_manifest'
        it must agree with the manifest.
        Choose one from 1, 2, 3.
    sg : StructureGene, optional
        Pre-built structure gene object (if not given, one is constructed).
    model_space : str, optional
        Mapping from mesh coordinate axes to SG axes, stored on the SG.
        Required when the SG is 1D or 2D and the format does not define it
        ('vabs' and 'swiftcomp' do); for 'sg_manifest' it must agree with the
        manifest.

    Returns
    -------
    StructureGene
        The parsed structure gene object.

    Raises
    ------
    IncompleteModelDataError
        If a required SG argument is missing.
    """
    logger.info('Reading file...')
    logger.debug(locals())

    registry = get_format_registry()
    canonical_format = registry.normalize(file_format)

    # The manifest is the authority; caller arguments may only confirm it.
    if canonical_format == 'sg_manifest':
        return registry.get_reader(canonical_format).read_input(
            filename, sgdim=sgdim, model_type=model_type, model_space=model_space,
        )

    given = {'sgdim': sgdim, 'model_type': model_type}
    missing = [
        name for name in _REQUIRED_READ_ARGS.get(canonical_format, ()) if given[name] is None
    ]
    if missing:
        raise IncompleteModelDataError(
            f"Reading {filename} as {canonical_format!r} requires {missing}; "
            "pass them as arguments or read an SG manifest."
        )

    reader = registry.get_reader(canonical_format)
    if reader is None:
        if registry.get_writer(canonical_format) is not None:
            raise ValueError(
                f"File format {file_format!r} supports writing only; reading is not implemented."
            )
        raise ValueError(f"Unknown file format: {file_format}")

    adapter_kwargs = dict(kwargs)
    if format_version:
        adapter_kwargs.setdefault('format_version', format_version)
    if model_type is not None:
        adapter_kwargs.setdefault('model_type', model_type)
        adapter_kwargs.setdefault('model', model_type)
    if sgdim is not None:
        adapter_kwargs.setdefault('sgdim', sgdim)
    result = reader.read_input(filename, **adapter_kwargs)

    # SG-specific adapters return ``StructureGene``; mesh-only adapters (Gmsh)
    # return a raw mesh. A mesh alone does not define a structure gene -- it
    # carries no material data and nothing that says which physical groups are
    # sections -- so rather than inventing either, refuse and say what is
    # missing. Gmsh models are read through an SG manifest.
    if isinstance(result, StructureGene):
        sg = result
    elif result is not None:
        raise IncompleteModelDataError(
            f"{filename} carries mesh data only. Building a structure gene also needs "
            "material and section data; read an SG manifest that references the mesh "
            "(file_format='sg_manifest')."
        )
    else:
        sg = None

    if not sg:
        # smdim must be int; model_type is a string like 'SD1' — parse it.
        smdim, submodel = _parse_model_type(model_type)
        sg = StructureGene(sgdim=sgdim, smdim=smdim)
        sg.analysis_config.model = submodel

    _set_model_space(sg, model_space, filename)
    return sg


# SG arguments a model file format cannot supply by itself.
_REQUIRED_READ_ARGS = {
    'abaqus': ('sgdim', 'model_type'),
    'swiftcomp': ('model_type',),
}


def _set_model_space(sg: StructureGene, model_space: str | None, filename: str) -> None:
    """Store the caller's model space on a freshly read SG; require it when needed."""
    if model_space is not None:
        if sg.model_space:
            raise ValueError(
                f"{filename} defines model_space={sg.model_space!r}; "
                "do not pass model_space for this format."
            )
        sg.model_space = model_space
    if sg.sgdim in (1, 2) and not sg.model_space:
        raise IncompleteModelDataError(
            f"Reading {filename} as a {sg.sgdim}D SG requires model_space."
        )


def read_fe_model(
    filename: str,
    file_format: str,
    model_type: str | None = None,
    format_version: str = '',
    sgdim: int | None = None,
    **kwargs
) -> FEModel:
    """Read an input file and return the generic FE core model.

    Explicit entry point for the generic finite-element core model. The
    current implementation reuses :func:`read` and unwraps its ``fe_model``;
    for the Abaqus path, ``fe_model.extras`` carries unmapped structural
    blocks (boundary conditions, loads, steps) captured as a fallback. A
    future FE-native adapter may return :class:`FEModel` directly here without
    the ``StructureGene`` wrapping.

    Parameters
    ----------
    filename : str
        Name of the input file.
    file_format : str
        Format of the input file.
        Choose one from 'abaqus', 'vabs', 'sc', 'swiftcomp', 'gmsh'.
    model_type : str, optional
        Type of the macro structural model. See :func:`read`.
    format_version : str, optional
        Version of the format.
    sgdim : int, optional
        Dimension of the geometry. See :func:`read`.

    Returns
    -------
    FEModel
        The generic finite-element core model.
    """
    sg = read(
        filename, file_format, model_type=model_type,
        format_version=format_version, sgdim=sgdim, **kwargs
    )
    return sg.fe_model


def read_output_model(
    filename: str, file_format: str, model_type: str = "",
    sg: StructureGene | None = None, **kwargs
) -> sgmodel.Model:
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
    Model
        Constitutive model parsed from the homogenization output.

    Raises
    ------
    FileNotFoundError
        If ``filename`` does not exist.
    """
    with open(filename, "r") as file:
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
    prop_ref_y: str = 'x',
    macro_responses: list[sgmodel.StateCase] | None = None, model_type: str | None = None,
    load_type: int = 0, sfi: str = '8d', sff: str = '20.12e', mesh_only: bool = False,
    binary: bool = False, model_file: str | None = None, model_file_format: str | None = None,
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
        Choose one from 'vabs', 'sc', 'swiftcomp', 'gmsh', 'vtk', 'vtu', or
        'sg_manifest'.
    format_version : str, optional
        Version of the format; for 'sg_manifest', of the model file format.
        Default is ``''`` (the writer's default version).
    analysis : str, optional
        Indicator of SG analysis.
        Default is ``'h'``.
        Choose one from

        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    sg_format : {0, 1}, optional
        Format for the VABS input. Default is 1.
    prop_ref_y : str, optional
        Reference axis selector for material orientation. Default is ``'x'``.
    macro_responses : list[StateCase], optional
        Macroscopic responses. Default is ``None`` (treated as empty).
    model_type : str, optional
        Type of the macro structural model. Defaults to the model type of
        ``sg``; for 'sg_manifest' it must agree with it.
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
    model_file : str, optional
        For 'sg_manifest': path of the model file relative to the manifest
        directory. The model file is written too.
    model_file_format : str, optional
        For 'sg_manifest': format of the model file ('vabs' or 'swiftcomp').

    Returns
    -------
    str
        The output filename.
    """
    logger.info('Writing file...')
    logger.debug(locals())

    if macro_responses is None:
        macro_responses = []

    if sg is None:
        raise ValueError('structure_gene is None')
    if sg.mesh is None:
        raise ValueError('structure_gene.mesh is None')

    registry = get_format_registry()
    canonical_format = registry.normalize(file_format)

    if canonical_format == 'sg_manifest':
        return _write_manifest_and_model_file(
            sg, filename, model_file, model_file_format, model_type,
            format_version=format_version, analysis=analysis, sg_format=sg_format,
            prop_ref_y=prop_ref_y, macro_responses=macro_responses, load_type=load_type,
            sfi=sfi, sff=sff, mesh_only=mesh_only, binary=binary,
        )

    writer = registry.get_writer(canonical_format)

    # Formats other than SG-specific solvers (VABS / SwiftComp) get mesh-only
    # output by default — preserves prior behaviour.
    if canonical_format not in ('swiftcomp', 'vabs'):
        mesh_only = True

    if writer is None:
        raise ValueError(f"Unsupported output format: {file_format}")

    if canonical_format in ('swiftcomp', 'vabs') and model_type is None:
        model_type = model_type_of(sg)

    common_kwargs = dict(
        analysis=analysis,
        macro_responses=macro_responses,
        model=model_type,
        model_space=sg.model_space,
        prop_ref_y=prop_ref_y,
        sfi=sfi,
        sff=sff,
    )
    if format_version:
        common_kwargs['version'] = format_version

    if canonical_format == 'swiftcomp':
        common_kwargs['load_type'] = load_type
    elif canonical_format == 'vabs':
        common_kwargs['sg_fmt'] = sg_format
        common_kwargs['mesh_only'] = mesh_only
    elif canonical_format == 'gmsh':
        # Gmsh writer pulls mesh/configs out of the SG itself; tighter kwargs.
        common_kwargs = dict(
            format_version=format_version,
            float_fmt=sff,
            mesh_only=mesh_only,
            binary=binary,
        )
    elif canonical_format in ('vtk', 'vtu'):
        common_kwargs = {'binary': binary}

    writer.write_input(filename, sg, **common_kwargs)
    return filename


def _write_manifest_and_model_file(
    sg: StructureGene,
    manifest_path: str,
    model_file: str | None,
    model_file_format: str | None,
    model_type: str | None,
    **write_kwargs,
) -> str:
    """Write a model file and the SG manifest that references it."""
    if not model_file or not model_file_format:
        raise ValueError("Writing an SG manifest requires model_file and model_file_format.")
    if Path(model_file).is_absolute():
        raise ValueError(
            f"model_file must be relative to the manifest directory; got {model_file!r}."
        )
    if model_type is not None and _parse_model_type(model_type) != _parse_model_type(
        model_type_of(sg)
    ):
        raise ValueError(
            f"Argument model_type={model_type!r} disagrees with the SG model type "
            f"{model_type_of(sg)!r}."
        )

    registry = get_format_registry()
    fmt = registry.normalize(model_file_format)
    if fmt not in WRITABLE_MODEL_FILE_FORMATS:
        raise ValueError(
            f"Writing an SG manifest with a {fmt!r} model file is not supported; "
            f"supported: {sorted(WRITABLE_MODEL_FILE_FORMATS)}."
        )
    writer = registry.get_writer(fmt)
    version = write_kwargs.pop('format_version') or getattr(writer, 'default_version', None) or ''

    # The manifest records the model file exactly as written.
    write(
        sg, str(Path(manifest_path).parent / model_file), fmt,
        format_version=version, **write_kwargs,
    )
    return write_sg_manifest(sg, manifest_path, model_file, fmt, format_version=version)


def convert_file_format(
    file_name_in: str,
    file_name_out: str,
    file_format_in: str,
    file_format_out: str,
    file_version_in: str = '',
    file_version_out: str = '',
    analysis: str = 'h',
    sgdim: int | None = None,
    model_space: str | None = None,
    prop_ref_y: str = 'x',
    model_type: str | None = None,
    vabs_format_version: int = 1,
    str_format_int: str = '8d',
    str_format_float: str = '20.12e',
    mesh_only: bool = False,
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
    sgdim : int, optional
        Dimension of the geometry. See :func:`read`.
        Choose one from 1, 2, 3.
    model_space : str, optional
        Mapping from input mesh coordinate axes to SG axes. See :func:`read`.
    model_type : str, optional
        Type of the macro structural model. See :func:`read`; when omitted,
        the model type of the SG that was read is written.
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
        model_space=model_space,
        mesh_only=mesh_only)

    if sg is None:
        raise ValueError("Input file is not a valid SG file.")

    write(
        sg=sg,
        filename=file_name_out,
        file_format=file_format_out,
        format_version=file_version_out,
        analysis=analysis,
        sg_format=vabs_format_version,
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
    'read_fe_model',
    'read_output',
    'read_output_model',
    'read_output_state',
    'read_load_csv',
    'write',
    'convert',
    'convert_file_format',
]
