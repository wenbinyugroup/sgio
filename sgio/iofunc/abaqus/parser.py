"""Abaqus input parser."""

from __future__ import annotations

import io
import logging
from contextlib import redirect_stdout
from typing import Any

from sgio._vendors.inprw.inpRW import inpRW

logger = logging.getLogger(__name__)

# Abaqus structural keywords that the SG mapper does not consume. They are
# captured here as plain, serializable dicts and routed to ``FEModel.extras``
# by the mapper as a non-lossy fallback (see architecture/io.md boundary table).
STRUCTURAL_KEYWORDS = ("boundary", "cload", "dload", "step")


def _scalar(value: Any) -> Any:
    """Coerce an inpRW parameter/data cell to a plain, deep-copyable value.

    inpRW wraps entries in ``int``/``str`` subclasses (``inpInt``, ``inpString``)
    and Decimal-like objects; force them to their plain base type so the
    ``extras`` fallback stays JSON/deep-copy safe.
    """
    value = getattr(value, "_value", value)
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return float(value)
    if isinstance(value, str):
        return str(value).strip()
    return str(value).strip()


def _serialize_block(block: Any) -> dict[str, Any]:
    """Serialize one inpRW keyword block into a plain dict.

    The result contains only primitives/strings so it survives the deep copy
    performed by :meth:`StructureGene.from_fe` / :meth:`StructuralModel.from_fe`.
    """
    parameters: dict[str, Any] = {}
    try:
        for key in block.parameter:
            parameters[str(key).strip()] = _scalar(block.parameter[key])
    except Exception:  # pragma: no cover - defensive against odd blocks
        parameters = {}

    data: list[list[Any]] = []
    try:
        for row in block.data:
            data.append([_scalar(cell) for cell in row])
    except Exception:  # pragma: no cover - *Step data may be non-tabular
        data = []

    return {
        "keyword": str(getattr(block, "name", "")),
        "parameters": parameters,
        "data": data,
    }


def _extract_structural_blocks(parser: inpRW) -> dict[str, list[dict[str, Any]]]:
    """Capture unmapped structural keyword blocks as serializable payloads."""
    blocks: dict[str, list[dict[str, Any]]] = {}
    for keyword in STRUCTURAL_KEYWORDS:
        found = parser.findKeyword(keyword, printOutput=False)
        if found:
            blocks[keyword] = [_serialize_block(block) for block in found]
    return blocks


def parse_input_file(
    filename: str,
    sgdim: int = 2,
    model: int | str = 1,
    **kwargs: Any,
) -> dict[str, Any]:
    """Parse an Abaqus input file into a raw intermediate payload.

    Parameters
    ----------
    filename : str
        Abaqus ``.inp`` filename.
    sgdim : int, optional
        Structure-gene geometry dimension.
    model : int or str, optional
        Macro model selector.
    **kwargs : dict[str, Any]
        Extra adapter options retained in the payload for mapper use.

    Returns
    -------
    dict[str, Any]
        Raw parser payload containing the native ``inpRW`` object plus caller
        context needed by the mapper.
    """
    parser = inpRW(filename)
    stdout_capture = io.StringIO()
    with redirect_stdout(stdout_capture):
        parser.parse()

    parser_output = stdout_capture.getvalue().strip()
    if parser_output:
        logger.debug(parser_output)

    return {
        "filename": filename,
        "sgdim": sgdim,
        "model": model,
        "kwargs": dict(kwargs),
        "inprw": parser,
        "structural_blocks": _extract_structural_blocks(parser),
    }
