"""VABS dehomogenization / failure-analysis output state reader.

Internal helper used by :func:`sgio.iofunc.main.read_output_state`. Parses
VABS ``.U``, ``.ELE``, and ``.fi`` files into per-case ``StateCase``
objects.
"""
from __future__ import annotations

import logging

import sgio.iofunc.vabs as _vabs
import sgio.model as sgmodel
from sgio.core import StructureGene

from ._helpers import _resolve_num_elements, _safe_parse

logger = logging.getLogger(__name__)


def read_vabs_output_state(
    filename: str, analysis: str, extension: list[str],
    num_cases: int, num_elements: int, sg: StructureGene,
    tool_version: str, **kwargs
) -> list[sgmodel.StateCase] | None:
    """Read VABS output state data.

    Parameters
    ----------
    filename : str
        Base filename.
    analysis : str
        ``'fi'`` for failure indices; ``'d'`` or ``'l'`` for dehomogenization.
    extension : list[str]
        Subset of ``{'u', 'ele'}`` to read.
    num_cases : int
        Number of load cases.
    num_elements : int
        Number of elements; ``0`` falls back to ``sg.nelems``.
    sg : StructureGene
        Structure gene object.
    tool_version : str
        VABS tool version string (e.g. ``'4'``, ``'5'``); empty string is
        treated as pre-4 (no version header to skip).

    Returns
    -------
    list[StateCase] or None
        List of state cases, or None on parse failure.
    """
    state_cases = [sgmodel.StateCase({}, {}) for _ in range(num_cases)]
    num_elements = _resolve_num_elements(num_elements, sg)

    def _skip_v4_header(f):
        # VABS 4+ writes a version header on the first line; consume it.
        if not tool_version or float(tool_version) <= 4:
            return
        line = f.readline()
        while line.strip() == '':
            line = f.readline()
        logger.debug(f'line: {line}')

    if analysis == "fi":
        with open(f"{filename}.fi", "r") as file:
            for i_case in range(num_cases):
                _skip_v4_header(file)
                result = _safe_parse(_vabs._readOutputFailureIndexCase, file, num_elements)
                if result is None:
                    return None
                fi, sr, eids_sr_min = result
                state_case = state_cases[i_case]
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
                sr_min = {eid: sr[eid] for eid in eids_sr_min}
                state_case.addState(
                    name="sr_min", state=sgmodel.State(
                        name="sr_min", data=sr_min, label=["sr_min"], location="element"
                    )
                )

    elif analysis in ("d", "l"):
        if "u" in extension:
            with open(f"{filename}.U", "r") as file:
                for i_case in range(num_cases):
                    u = _safe_parse(
                        _vabs.read_output_buffer, file, analysis, extension="u", **kwargs,
                    )
                    if u is None:
                        return None
                    state_cases[i_case].addState(
                        name="u", state=sgmodel.State(
                            name="u", data=u, label=["u1", "u2", "u3"], location="node"
                        )
                    )

        if "ele" in extension:
            with open(f"{filename}.ELE", "r") as file:
                for i_case in range(num_cases):
                    _skip_v4_header(file)
                    result = _safe_parse(
                        _vabs._readOutputElementStrainStressCase, file, num_elements,
                    )
                    if result is None:
                        return None
                    ee, es, eem, esm = result
                    state_case = state_cases[i_case]
                    # VABS .ELE strain columns are engineering shear: e11, 2e12, 2e13, e22, 2e23, e33.
                    # See VABS docs: guide/output/dehomo.md.
                    state_case.addState(
                        name="ee", state=sgmodel.State(
                            name="ee", data=ee,
                            label=["e11", "2e12", "2e13", "e22", "2e23", "e33"],
                            location="element"
                        )
                    )
                    state_case.addState(
                        name="es", state=sgmodel.State(
                            name="es", data=es,
                            label=["s11", "s12", "s13", "s22", "s23", "s33"],
                            location="element"
                        )
                    )
                    state_case.addState(
                        name="eem", state=sgmodel.State(
                            name="eem", data=eem,
                            label=["em11", "2em12", "2em13", "em22", "2em23", "em33"],
                            location="element"
                        )
                    )
                    state_case.addState(
                        name="esm", state=sgmodel.State(
                            name="esm", data=esm,
                            label=["sm11", "sm12", "sm13", "sm22", "sm23", "sm33"],
                            location="element"
                        )
                    )

    return state_cases
