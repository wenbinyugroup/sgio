"""VABS output reader orchestration."""

from __future__ import annotations

import logging

from sgio.core.sg import StructureGene

from ._output import (
    _readOutputElementStrainStressCase,
    _readOutputFailureIndexCase,
    _readOutputH,
    _readOutputNodeDisplacement,
)


logger = logging.getLogger(__name__)


def read_output_buffer(
    file,
    analysis: str = "h",
    sg: StructureGene | None = None,
    extension: str = "",
    model_type: str = "BM1",
    tool_version: str = "",
    ncase: int = 1,
    nelem: int = 0,
    **kwargs,
):
    """Read a VABS output file buffer."""
    logger.debug("reading vabs output...")
    logger.debug(locals())

    if analysis in (0, "h", ""):
        if sg is not None:
            if sg.analysis_config.model == 0:
                return _readOutputH(file, model_type="bm1", **kwargs)
            if sg.analysis_config.model == 1:
                return _readOutputH(file, model_type="bm2", **kwargs)
            return None
        return _readOutputH(file, model_type=model_type, **kwargs)

    if analysis in (1, 2, "dl", "d", "l"):
        if extension == "u":
            return _readOutputNodeDisplacement(file)
        if extension == "ele":
            if nelem == 0 and sg is not None:
                nelem = sg.nelems
            if ncase == 1:
                if tool_version and float(tool_version) > 4:
                    file.readline()
                return _readOutputElementStrainStressCase(file, nelem)
        return None

    if analysis in ("f", 3, "fe", 4):
        return None

    if analysis in ("fi", 5):
        if nelem == 0 and sg is not None:
            nelem = sg.nelems
        if ncase == 1:
            if tool_version and float(tool_version) > 4:
                file.readline()
            return _readOutputFailureIndexCase(file, nelem)
        return None

    return None
