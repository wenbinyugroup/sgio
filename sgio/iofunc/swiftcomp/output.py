"""SwiftComp output reader orchestration."""

from __future__ import annotations

from sgio.core.sg import StructureGene

from ._output import (
    _readOutputFailureIndex,
    _readOutputH,
    _read_output_node_strain_stress_case_global_gmsh,
)


def read_output_buffer(
    file,
    analysis: int | str,
    model_type: str,
    sg: StructureGene | None = None,
    extension: str = "",
    nelem: int = 0,
    lfmt: int = 0,
    **kwargs,
):
    """Read a SwiftComp output file buffer."""
    if analysis in (0, "h", ""):
        return _readOutputH(file, model_type=model_type, **kwargs)

    if analysis in (1, 2, "dl", "d", "l"):
        if extension == "u":
            return None

        if nelem == 0 and sg is not None:
            nelem = sg.nelems

        if extension == "sn" and lfmt == 1:
            return _read_output_node_strain_stress_case_global_gmsh(file, nelem, sg)
        return None

    if analysis in ("f", 3, "fe", 4):
        return None

    if analysis in ("fi", 5):
        return _readOutputFailureIndex(file)

    return None
