"""SwiftComp dehomogenization output state reader.

Internal helper used by :func:`sgio.iofunc.main.read_output_state`. Splits
the SwiftComp-specific parsing of `.u` / `.sn` / `.snm` files out of the
main module so the public entry point stays a thin dispatcher.
"""
from __future__ import annotations

import logging

import sgio.iofunc.swiftcomp as _swiftcomp
import sgio.model as sgmodel
from sgio.core import StructureGene

from ._helpers import _resolve_num_elements, _safe_parse

logger = logging.getLogger(__name__)


def read_swiftcomp_output_state(
    filename: str, analysis: str, model_type: str, extension: list[str],
    num_cases: int, num_elements: int, sg: StructureGene, **kwargs
) -> list[sgmodel.StateCase] | None:
    """Read SwiftComp output state data.

    Parameters
    ----------
    filename : str
        Base filename.
    analysis : str
        Analysis type. ``'fi'`` for failure indices; ``'d'`` or ``'l'`` for
        dehomogenization.
    model_type : str
        Macro structural model type (only consulted by the underlying
        SwiftComp ``read_output_buffer`` for ``'fi'``).
    extension : list[str]
        Subset of ``{'u', 'sn', 'snm'}`` to read.
    num_cases : int
        Number of load cases.
    num_elements : int
        Number of elements; ``0`` falls back to ``sg.nelems``.
    sg : StructureGene
        Structure gene object.

    Returns
    -------
    list[StateCase] or None
        List of state cases, or None on parse failure.
    """
    state_cases = [sgmodel.StateCase({}, {}) for _ in range(num_cases)]

    if analysis == "fi":
        with open(f"{filename}.fi", "r") as file:
            return _swiftcomp.read_output_buffer(
                file, analysis=analysis, model_type=model_type, **kwargs
            )

    if analysis in ("d", "l"):
        num_elements = _resolve_num_elements(num_elements, sg)

        if 'u' in extension:
            logger.info(f'reading displacement... {filename}.u')
            with open(f"{filename}.u", "r") as file:
                for i_case in range(num_cases):
                    u = _safe_parse(_swiftcomp._read_output_node_disp_case, file, sg.nnodes)
                    if u is None:
                        return None
                    state_cases[i_case].addState(
                        name="u", state=sgmodel.State(
                            name="u", data=u, label=["u1", "u2", "u3"], location="node"
                        )
                    )

        if 'sn' in extension:
            logger.info(f'reading element node strain and stress... {filename}.sn')
            with open(f"{filename}.sn", "r") as file:
                for i_case in range(num_cases):
                    result = _safe_parse(
                        _swiftcomp._read_output_node_strain_stress_case_global_gmsh,
                        file, num_elements, sg,
                    )
                    if result is None:
                        return None
                    strains, stresses = result
                    state_cases[i_case].addState(
                        name='e', state=sgmodel.State(
                            name='e', data=strains,
                            label=['e11', 'e22', 'e33', '2e23', '2e13', '2e12'],
                            location='element_node'
                        )
                    )
                    state_cases[i_case].addState(
                        name='s', state=sgmodel.State(
                            name='s', data=stresses,
                            label=['s11', 's22', 's33', 's23', 's13', 's12'],
                            location='element_node'
                        )
                    )

        if 'snm' in extension:
            logger.info(f'reading element node strain and stress in material c/s... {filename}.snm')
            with open(f"{filename}.snm", "r") as file:
                for i_case in range(num_cases):
                    result = _safe_parse(
                        _swiftcomp._read_output_node_strain_stress_case_global_gmsh,
                        file, num_elements, sg,
                    )
                    if result is None:
                        return None
                    strains, stresses = result
                    state_cases[i_case].addState(
                        name='em', state=sgmodel.State(
                            name='em', data=strains,
                            label=['e11m', 'e22m', 'e33m', '2e23m', '2e13m', '2e12m'],
                            location='element_node'
                        )
                    )
                    state_cases[i_case].addState(
                        name='sm', state=sgmodel.State(
                            name='sm', data=stresses,
                            label=['s11m', 's22m', 's33m', 's23m', 's13m', 's12m'],
                            location='element_node'
                        )
                    )

    return state_cases
