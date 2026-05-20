"""Abaqus input parser."""

from __future__ import annotations

import io
import logging
from contextlib import redirect_stdout
from typing import Any

from sgio._vendors.inprw.inpRW import inpRW

logger = logging.getLogger(__name__)


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
    }
