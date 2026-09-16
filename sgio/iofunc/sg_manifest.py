"""SG manifest: the JSON primary file of a structure gene.

An SG manifest (``*.sg.json``) carries the SG-level parameters that no model
file format can express, and references exactly one model file by a path
relative to the manifest. See ``docs/adr/0001-sg-manifest-as-primary-file.md``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sgio._exceptions import IncompleteModelDataError
from sgio.core import SGAnalysisConfig, StructureGene

from ._mesh_convert import parse_model_type
from .base import BaseFormatReader, get_format_registry

MANIFEST_VERSION = 1

_TOP_LEVEL_KEYS = {
    'sg_manifest_version', 'model_file', 'sgdim', 'model_type', 'model_space',
    'initial_twist', 'initial_curvature', 'oblique', 'sections', 'config',
}
_MODEL_FILE_KEYS = {'path', 'format', 'format_version'}
_BEAM_GEOMETRY_KEYS = ('initial_twist', 'initial_curvature', 'oblique')

# Blocks each model file format owns; a manifest must not repeat them.
_OWNED_BLOCKS: dict[str, set[str]] = {
    'abaqus': {'sections'},
}

_MODEL_SPACES = {1: {'x', 'y', 'z'}, 2: {'xy', 'yz', 'zx'}}


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
        Model space given by the caller; must agree with the manifest.

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
        owns, or disagrees with the caller's arguments.
    """
    manifest_path = Path(manifest_path)
    with manifest_path.open('r', encoding='utf-8') as file:
        data = json.load(file)

    _check_structure(data, manifest_path)
    fmt = data['model_file']['format']
    _check_owned_blocks(data, fmt)

    # Every field has one authority; caller arguments may only confirm it.
    _check_agreement('sgdim', sgdim, data['sgdim'])
    _check_agreement('model_space', model_space, data.get('model_space'))
    if model_type is not None and (
        parse_model_type(model_type) != parse_model_type(data['model_type'])
    ):
        _raise_disagreement('model_type', model_type, data['model_type'])

    model_file = data['model_file']
    reader = get_format_registry().get_reader(fmt)
    read_kwargs: dict[str, Any] = {
        'sgdim': data['sgdim'], 'model': data['model_type'], 'model_type': data['model_type'],
    }
    if model_file.get('format_version'):
        read_kwargs['format_version'] = model_file['format_version']
    sg = reader.read_input(str(manifest_path.parent / model_file['path']), **read_kwargs)

    _apply_manifest_fields(sg, data)
    return sg


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

    model_file = data.get('model_file')
    if not isinstance(model_file, dict):
        raise IncompleteModelDataError(f"{manifest_path}: 'model_file' object is required.")
    unknown = set(model_file) - _MODEL_FILE_KEYS
    if unknown:
        raise ValueError(f"{manifest_path}: unknown model_file fields {sorted(unknown)}.")
    for key in ('path', 'format'):
        if not model_file.get(key):
            raise IncompleteModelDataError(f"{manifest_path}: 'model_file.{key}' is required.")
    if model_file['format'] not in _OWNED_BLOCKS:
        raise ValueError(
            f"{manifest_path}: model file format {model_file['format']!r} is not supported "
            f"by SG manifest; supported: {sorted(_OWNED_BLOCKS)}."
        )

    for key in ('sgdim', 'model_type'):
        if data.get(key) is None:
            raise IncompleteModelDataError(f"{manifest_path}: '{key}' is required.")
    parse_model_type(data['model_type'])
    _check_model_space(data, manifest_path)


def _check_model_space(data: dict, manifest_path: Path) -> None:
    """Require a valid model space exactly when the SG is lower-dimensional."""
    sgdim = data['sgdim']
    model_space = data.get('model_space')
    if sgdim not in (1, 2, 3):
        raise ValueError(f"{manifest_path}: sgdim must be 1, 2 or 3; got {sgdim!r}.")
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
        _raise_disagreement(name, given, manifest_value)


def _raise_disagreement(name: str, given: Any, manifest_value: Any) -> None:
    """Raise the standard caller/manifest disagreement error."""
    raise ValueError(
        f"Argument {name}={given!r} disagrees with the SG manifest value {manifest_value!r}."
    )


def _apply_manifest_fields(sg: StructureGene, data: dict) -> None:
    """Set manifest-owned SG fields on a structure gene read from its model file."""
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
