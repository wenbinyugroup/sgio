"""SG manifest: the JSON primary file of a structure gene.

An SG manifest (``*.sg.json``) carries the SG-level parameters that no model
file format can express, and references exactly one model file by a path
relative to the manifest. See ``docs/adr/0001-sg-manifest-as-primary-file.md``.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path, PurePath
from typing import Any

from sgio._exceptions import IncompleteModelDataError
from sgio.core import SGAnalysisConfig, StructureGene

from ._manifest_sections import (
    materials_to_records,
    sections_to_records,
    structure_gene_from_mesh,
)
from ._mesh_convert import parse_model_type
from .base import BaseFormatReader, get_format_registry

MANIFEST_VERSION = 1

_TOP_LEVEL_KEYS = {
    'sg_manifest_version', 'model_file', 'sgdim', 'model_type', 'model_space',
    'initial_twist', 'initial_curvature', 'oblique', 'materials', 'sections', 'config',
}
_MODEL_FILE_KEYS = {'path', 'format', 'format_version'}
_BEAM_GEOMETRY_KEYS = ('initial_twist', 'initial_curvature', 'oblique')
_SOLVER_OWNED = {'materials', 'sections', 'config', 'model_space', *_BEAM_GEOMETRY_KEYS}

# Blocks each model file format owns; a manifest must not repeat them.
_OWNED_BLOCKS: dict[str, set[str]] = {
    'abaqus': {'materials', 'sections'},
    'gmsh': set(),
    'swiftcomp': _SOLVER_OWNED,
    'vabs': _SOLVER_OWNED,
}

# Model file formats sgio can write under a manifest (no Abaqus writer exists).
WRITABLE_MODEL_FILE_FORMATS = {'gmsh', 'swiftcomp', 'vabs'}

# Formats whose files come in several versions; the manifest must name one.
_VERSIONED_FORMATS = {'swiftcomp', 'vabs'}

_MODEL_SPACES = {1: {'x', 'y', 'z'}, 2: {'xy', 'yz', 'zx'}}
_MODEL_TYPE_PREFIX = {1: 'BM', 2: 'PL', 3: 'SD'}


def model_type_of(sg: StructureGene) -> str:
    """Return the model type string (e.g. ``'BM1'``) of a structure gene.

    Parameters
    ----------
    sg : StructureGene
        Structure gene with ``smdim`` and ``analysis_config.model`` set.

    Returns
    -------
    str
        Model type string.

    Raises
    ------
    IncompleteModelDataError
        If the structure gene has no macro model dimension.
    """
    if sg.smdim not in _MODEL_TYPE_PREFIX:
        raise IncompleteModelDataError(
            f"Structure gene has no valid smdim ({sg.smdim!r}); its model type is unknown."
        )
    return f'{_MODEL_TYPE_PREFIX[sg.smdim]}{sg.analysis_config.model + 1}'


def read_sg_manifest(
    manifest_path: str | Path,
    sgdim: int | None = None,
    model_type: str | None = None,
    model_space: str | None = None,
) -> StructureGene:
    """Read a structure gene from an SG manifest and its model file.

    Parameters
    ----------
    manifest_path : str or Path
        Path to the ``*.sg.json`` manifest.
    sgdim : int, optional
        SG dimension given by the caller; must agree with the manifest.
    model_type : str, optional
        Macro model type given by the caller; must agree with the manifest.
    model_space : str, optional
        Model space given by the caller; must agree with the SG.

    Returns
    -------
    StructureGene
        The assembled structure gene.

    Raises
    ------
    IncompleteModelDataError
        If a required manifest field is missing.
    ValueError
        If the manifest is malformed, repeats a block its model file format
        owns, or disagrees with the model file or the caller's arguments.
    """
    manifest_path = Path(manifest_path)
    with manifest_path.open('r', encoding='utf-8') as file:
        data = json.load(file)

    _check_structure(data, manifest_path)
    model_file = data['model_file']
    fmt = model_file['format']
    _check_owned_blocks(data, fmt)

    # Every field has one authority; caller arguments may only confirm it.
    _check_agreement('sgdim', sgdim, data['sgdim'])
    if model_type is not None:
        _check_model_type('Argument', model_type, data['model_type'])

    read_kwargs: dict[str, Any] = {
        'sgdim': data['sgdim'], 'model': data['model_type'], 'model_type': data['model_type'],
    }
    if model_file.get('format_version'):
        read_kwargs['format_version'] = model_file['format_version']
    reader = get_format_registry().get_reader(fmt)
    sg = reader.read_input(str(manifest_path.parent / model_file['path']), **read_kwargs)
    if not isinstance(sg, StructureGene):
        # Mesh-only formats get their materials and sections from the manifest.
        sg = structure_gene_from_mesh(sg, data['sgdim'], data['model_type'], data)

    # A model file that encodes sgdim or model type must match the manifest.
    if sg.sgdim != data['sgdim']:
        _raise_disagreement(f"{fmt} model file sgdim", sg.sgdim, data['sgdim'])
    _check_model_type(f"{fmt} model file model_type", model_type_of(sg), data['model_type'])

    _apply_manifest_fields(sg, data, fmt)
    _check_agreement('model_space', model_space, sg.model_space)
    return sg


def write_sg_manifest(
    sg: StructureGene,
    manifest_path: str | Path,
    model_file: str,
    model_file_format: str,
    format_version: str = '',
) -> str:
    """Write the SG manifest for a structure gene whose model file is written.

    Blocks owned by the model file format are left out of the manifest.

    Parameters
    ----------
    sg : StructureGene
        Structure gene described by the manifest.
    manifest_path : str or Path
        Path of the ``*.sg.json`` manifest to write.
    model_file : str
        Path of the model file, relative to the manifest directory.
    model_file_format : str
        Canonical format name of the model file.
    format_version : str, optional
        Version of the model file format.

    Returns
    -------
    str
        The manifest path.
    """
    owned = owned_blocks(model_file_format, manifest_path)
    if model_file_format in _VERSIONED_FORMATS and not format_version:
        raise IncompleteModelDataError(
            f"Writing a {model_file_format!r} SG manifest requires the model file format version."
        )

    entry: dict[str, Any] = {'path': PurePath(model_file).as_posix(), 'format': model_file_format}
    if model_file_format in _VERSIONED_FORMATS:
        entry['format_version'] = format_version
    data: dict[str, Any] = {
        'sg_manifest_version': MANIFEST_VERSION,
        'model_file': entry,
        'sgdim': sg.sgdim,
        'model_type': model_type_of(sg),
    }
    if 'model_space' not in owned and sg.sgdim in _MODEL_SPACES:
        data['model_space'] = sg.model_space
    for key in _BEAM_GEOMETRY_KEYS:
        if key not in owned:
            data[key] = getattr(sg, key)
    if 'config' not in owned:
        config = asdict(sg.analysis_config)
        config.pop('model')
        data['config'] = config
    if 'materials' not in owned:
        data['materials'] = materials_to_records(sg)
    if 'sections' not in owned:
        data['sections'] = sections_to_records(sg)

    with Path(manifest_path).open('w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)
    return str(manifest_path)


def owned_blocks(fmt: str, manifest_path: str | Path) -> set[str]:
    """Return the manifest blocks a model file format owns.

    Parameters
    ----------
    fmt : str
        Canonical model file format name.
    manifest_path : str or Path
        Manifest path, used in the error message.

    Returns
    -------
    set of str
        Owned block names.

    Raises
    ------
    ValueError
        If the format cannot be referenced by an SG manifest.
    """
    if fmt not in _OWNED_BLOCKS:
        raise ValueError(
            f"{manifest_path}: model file format {fmt!r} is not supported "
            f"by SG manifest; supported: {sorted(_OWNED_BLOCKS)}."
        )
    return _OWNED_BLOCKS[fmt]


def _check_structure(data: Any, manifest_path: Path) -> None:
    """Validate keys, version and required fields of a manifest."""
    if not isinstance(data, dict):
        raise TypeError(f"{manifest_path}: an SG manifest must be a JSON object.")

    unknown = set(data) - _TOP_LEVEL_KEYS
    if unknown:
        raise ValueError(f"{manifest_path}: unknown SG manifest fields {sorted(unknown)}.")

    version = data.get('sg_manifest_version')
    if version != MANIFEST_VERSION:
        raise ValueError(
            f"{manifest_path}: unsupported sg_manifest_version {version!r}; "
            f"expected {MANIFEST_VERSION}."
        )

    _check_model_file(data.get('model_file'), manifest_path)

    for key in ('sgdim', 'model_type'):
        if data.get(key) is None:
            raise IncompleteModelDataError(f"{manifest_path}: '{key}' is required.")
    parse_model_type(data['model_type'])
    _check_model_space(data, manifest_path)


def _check_model_file(model_file: Any, manifest_path: Path) -> None:
    """Validate the model file reference and normalize its format name."""
    if not isinstance(model_file, dict):
        raise IncompleteModelDataError(f"{manifest_path}: 'model_file' object is required.")
    unknown = set(model_file) - _MODEL_FILE_KEYS
    if unknown:
        raise ValueError(f"{manifest_path}: unknown model_file fields {sorted(unknown)}.")
    for key in ('path', 'format'):
        if not model_file.get(key):
            raise IncompleteModelDataError(f"{manifest_path}: 'model_file.{key}' is required.")

    model_file['format'] = get_format_registry().normalize(model_file['format'])
    fmt = model_file['format']
    owned_blocks(fmt, manifest_path)
    if fmt in _VERSIONED_FORMATS and not model_file.get('format_version'):
        raise IncompleteModelDataError(
            f"{manifest_path}: 'model_file.format_version' is required for {fmt!r}."
        )
    if fmt not in _VERSIONED_FORMATS and 'format_version' in model_file:
        raise ValueError(
            f"{manifest_path}: 'model_file.format_version' does not apply to {fmt!r}; "
            "the version is read from the file."
        )


def _check_model_space(data: dict, manifest_path: Path) -> None:
    """Require a valid model space when the manifest owns it for a 1D/2D SG."""
    sgdim = data['sgdim']
    model_space = data.get('model_space')
    if sgdim not in (1, 2, 3):
        raise ValueError(f"{manifest_path}: sgdim must be 1, 2 or 3; got {sgdim!r}.")
    if 'model_space' in _OWNED_BLOCKS[data['model_file']['format']]:
        return
    if sgdim == 3:
        if model_space is not None:
            raise ValueError(f"{manifest_path}: 'model_space' does not apply to sgdim=3.")
        return
    if model_space is None:
        raise IncompleteModelDataError(
            f"{manifest_path}: 'model_space' is required for sgdim={sgdim}."
        )
    if model_space not in _MODEL_SPACES[sgdim]:
        raise ValueError(
            f"{manifest_path}: model_space {model_space!r} is invalid for sgdim={sgdim}; "
            f"expected one of {sorted(_MODEL_SPACES[sgdim])}."
        )


def _check_owned_blocks(data: dict, fmt: str) -> None:
    """Reject manifest blocks that the model file format owns."""
    repeated = _OWNED_BLOCKS[fmt] & set(data)
    if repeated:
        raise ValueError(
            f"SG manifest must not define {sorted(repeated)}: "
            f"the {fmt!r} model file owns that data."
        )


def _check_agreement(name: str, given: Any, manifest_value: Any) -> None:
    """Raise if a caller argument contradicts the manifest."""
    if given is not None and given != manifest_value:
        _raise_disagreement(f"Argument {name}", given, manifest_value)


def _check_model_type(source: str, value: str, manifest_value: str) -> None:
    """Raise if a model type contradicts the manifest, ignoring spelling case."""
    if parse_model_type(value) != parse_model_type(manifest_value):
        _raise_disagreement(f"{source}", value, manifest_value)


def _raise_disagreement(source: str, value: Any, manifest_value: Any) -> None:
    """Raise the standard manifest disagreement error."""
    raise ValueError(
        f"{source}={value!r} disagrees with the SG manifest value {manifest_value!r}."
    )


def _apply_manifest_fields(sg: StructureGene, data: dict, fmt: str) -> None:
    """Set manifest-owned SG fields on a structure gene read from its model file."""
    if 'model_space' not in _OWNED_BLOCKS[fmt]:
        sg.model_space = data.get('model_space', '')
    for key in _BEAM_GEOMETRY_KEYS:
        if key in data:
            setattr(sg, key, data[key])

    config = data.get('config')
    if config is not None:
        if not isinstance(config, dict):
            raise TypeError("SG manifest field 'config' must be an object.")
        # The submodel selector is part of model_type; config must not repeat it.
        if 'model' in config:
            raise ValueError(
                "SG manifest 'config' must not define 'model'; it is given by 'model_type'."
            )
        submodel = sg.analysis_config.model
        sg.analysis_config = SGAnalysisConfig(**config)
        sg.analysis_config.model = submodel


class SGManifestReader(BaseFormatReader):
    """Registry reader for SG manifests."""

    def __init__(self):
        """Initialize the SG manifest reader."""
        super().__init__('sg_manifest')

    def read_input(
        self,
        source: str | Path,
        sgdim: int | None = None,
        model_type: str | None = None,
        model_space: str | None = None,
        **kwargs: Any,
    ) -> StructureGene:
        """Read a structure gene from an SG manifest path.

        Parameters
        ----------
        source : str or Path
            Path to the manifest.
        sgdim, model_type, model_space : optional
            Caller arguments; each must agree with the manifest.
        **kwargs
            Ignored.

        Returns
        -------
        StructureGene
            The assembled structure gene.
        """
        if not isinstance(source, (str, Path)):
            raise TypeError("SG manifest reader supports file paths only.")
        return read_sg_manifest(source, sgdim, model_type, model_space)

    def read_output(self, source, analysis: str = 'h', **kwargs: Any) -> Any:
        """SG manifests have no output files."""
        raise NotImplementedError("SG manifest has no analysis output.")
