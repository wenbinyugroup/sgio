"""Module for executing external solvers (VABS and SwiftComp)."""

from __future__ import annotations

import logging
from typing import Union, Literal

import sgio.utils.execu as sue
import sgio.utils as sutl
from .model.general import getModelDim

logger = logging.getLogger(__name__)


# Type alias for analysis parameter
AnalysisType = Union[int, Literal['', 'h', 'dn', 'dl', 'd', 'l', 'fi', 'f', 'fe']]

# Analysis type constants for VABS
VABS_HOMOGENIZATION = (0, 'h', '')
VABS_DEHOM_NONLINEAR = (1, 'dn')
VABS_DEHOM_LINEAR = (2, 'dl', 'd', 'l')
VABS_FAILURE_INDICES = (3, 'fi')

# Analysis type constants for SwiftComp
SC_HOMOGENIZATION = (0, 'h', '')
SC_DEHOM_LINEAR = (2, 'dl', 'd', 'l')
SC_FAILURE_INDICES = (3, 'fi')
SC_FAILURE_STRENGTH = (4, 'f')
SC_FAILURE_ENVELOPE = (5, 'fe')

# Valid dimensions for structural models
VALID_SMDIM = (1, 2, 3)


def run(
    solver: str,
    input_name: str,
    analysis: AnalysisType,
    smdim: Union[int, str] = 2,
    aperiodic: bool = False,
    output_gmsh_format: bool = True,
    reduced_integration: bool = False,
    scrnout: bool = True,
    timeout: float = 3600
) -> None:
    """Run external solvers (VABS or SwiftComp).

    Parameters
    ----------
    solver : str
        Solver name of VABS or SwiftComp
    input_name : str
        Name of the input file.
    analysis : {0, 1, 2, 3, 4, 5, '', 'h', 'dn', 'dl', 'd', 'l', 'fi', 'f', 'fe'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 1 or 'dn' - (VABS) dehomogenization (nonlinear)
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
        * 4 or 'f' - (SwiftComp) initial failure strength
        * 5 or 'fe' - (SwiftComp) initial failure envelope
    smdim : int or str, default 2
        (SwiftComp) Dimension of the macroscopic structural model.
    aperiodic : bool, default False
        (SwiftComp) If the structure gene is periodic.
    output_gmsh_format : bool, default True
        (SwiftComp) If output dehomogenization results in Gmsh format
    reduced_integration : bool, default False
        (SwiftComp) If reduced integration is used for certain elements.
    scrnout : bool, default True
        Switch of printing solver messages (currently unused).
    timeout : float, default 3600
        Timeout in seconds for solver execution.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If solver type is not recognized or parameters are invalid.
    VABSError, SwiftCompError
        If solver execution fails.
    """
    logger.debug(f'local variables:\n{sutl.convertToPrettyString(locals())}')

    # Validate timeout
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")

    solver_lower = solver.lower()
    
    if solver_lower.startswith('v'):
        runVABS(solver, input_name, analysis, scrnout, timeout)
    elif solver_lower.startswith('s'):
        if isinstance(smdim, str):
            smdim = getModelDim(smdim)
        runSwiftComp(
            solver, input_name, analysis, smdim,
            aperiodic, output_gmsh_format, reduced_integration,
            scrnout, timeout
        )
    else:
        raise ValueError(f"Unknown solver type: {solver}. Must start with 'v' (VABS) or 's' (SwiftComp).")






def runVABS(
    command: str,
    input_name: str,
    analysis: AnalysisType,
    scrnout: bool = True,
    timeout: float = 3600
) -> None:
    """Run VABS solver.

    Parameters
    ----------
    command : str
        Command name of VABS
    input_name : str
        Name of the input file.
    analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 1 or 'dn' - dehomogenization (nonlinear)
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
    scrnout : bool, default True
        Switch of printing solver messages (currently unused).
    timeout : float, default 3600
        Timeout in seconds for solver execution.

    Returns
    -------
    None

    Raises
    ------
    VABSError
        If VABS execution fails.
    ValueError
        If timeout is invalid.
    """
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")

    cmd = [command, input_name]

    if analysis in VABS_HOMOGENIZATION:
        pass
    elif analysis in VABS_DEHOM_NONLINEAR:
        cmd.append('1')
    elif analysis in VABS_DEHOM_LINEAR:
        cmd.append('2')
    elif analysis in VABS_FAILURE_INDICES:
        cmd.append('3')
    else:
        valid = f"homogenization {VABS_HOMOGENIZATION}, " \
                f"dehomogenization-nonlinear {VABS_DEHOM_NONLINEAR}, " \
                f"dehomogenization-linear {VABS_DEHOM_LINEAR}, " \
                f"failure-indices {VABS_FAILURE_INDICES}"
        raise ValueError(f"Invalid analysis type for VABS: {analysis}. Valid options: {valid}")

    sue.run(cmd, int(timeout))


def runSwiftComp(
    command: str,
    input_name: str,
    analysis: AnalysisType,
    smdim: int,
    aperiodic: bool = False,
    output_gmsh_format: bool = True,
    reduced_integration: bool = False,
    scrnout: bool = True,
    timeout: float = 3600
) -> None:
    """Run SwiftComp solver.

    Parameters
    ----------
    command : str
        Command name of SwiftComp
    input_name : str
        Name of the input file.
    analysis : {0, 2, 3, 4, 5, '', 'h', 'dl', 'd', 'l', 'fi', 'f', 'fe'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
        * 4 or 'f' - initial failure strength
        * 5 or 'fe' - initial failure envelope
    smdim : int
        Dimension of the macroscopic structural model (1, 2, or 3).
    aperiodic : bool, default False
        If the structure gene is periodic.
    output_gmsh_format : bool, default True
        If output dehomogenization results in Gmsh format
    reduced_integration : bool, default False
        If reduced integration is used for certain elements.
    scrnout : bool, default True
        Switch of printing solver messages (currently unused).
    timeout : float, default 3600
        Timeout in seconds for solver execution.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If invalid analysis type or smdim is provided.
    SwiftCompError
        If SwiftComp execution fails.
    """
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")
        
    if smdim not in VALID_SMDIM:
        raise ValueError(f"smdim must be in {VALID_SMDIM}, got {smdim}")

    cmd = [command, input_name]
    cmd.append(f'{smdim}D')

    arg = ''

    if analysis in SC_HOMOGENIZATION:
        arg = 'H'
        if aperiodic:
            arg += 'A'
    elif analysis in SC_DEHOM_LINEAR:
        arg = 'L'
        if aperiodic:
            arg += 'A'
        if output_gmsh_format:
            arg += 'G'
    elif analysis in SC_FAILURE_INDICES:
        arg = 'FI'
    elif analysis in SC_FAILURE_STRENGTH:
        arg = 'F'
    elif analysis in SC_FAILURE_ENVELOPE:
        arg = 'FE'
    else:
        valid = f"homogenization {SC_HOMOGENIZATION}, " \
                f"dehomogenization-linear {SC_DEHOM_LINEAR}, " \
                f"failure-indices {SC_FAILURE_INDICES}, " \
                f"failure-strength {SC_FAILURE_STRENGTH}, " \
                f"failure-envelope {SC_FAILURE_ENVELOPE}"
        raise ValueError(f"Invalid analysis type for SwiftComp: {analysis}. Valid options: {valid}")

    cmd.append(arg)

    if reduced_integration:
        cmd.append('R')

    sue.run(cmd, int(timeout))

