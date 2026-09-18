from __future__ import annotations

import logging
import os
import shutil
import subprocess as sbp
from typing import List, Union


from sgio._global import MSG_COMMANDS
from sgio._exceptions import (
    SwiftCompLicenseError,
    VABSLicenseError,
    SwiftCompIOError,
    VABSIOError,
    SwiftCompError,
    VABSError,
)


logger = logging.getLogger(__name__)


def run(cmd: Union[List[str], tuple], timeout: int) -> sbp.CompletedProcess:
    """Run external solver command with error handling.
    
    Executes a command using subprocess and handles SwiftComp/VABS-specific
    error detection by parsing stdout for known error patterns. Automatically
    wraps Windows batch scripts with cmd.exe.
    
    Parameters
    ----------
    cmd : list of str or tuple
        Command and arguments to execute
    timeout : int
        Timeout in seconds for command execution
    
    Returns
    -------
    subprocess.CompletedProcess
        Process result object containing stdout, stderr, and return code
    
    Raises
    ------
    ValueError
        If cmd is empty or timeout is not positive
    SwiftCompLicenseError, VABSLicenseError
        If license issues detected in solver output
    SwiftCompIOError, VABSIOError
        If I/O errors detected in solver output
    SwiftCompError, VABSError
        If solver execution fails for other reasons
    subprocess.CalledProcessError
        If command returns non-zero exit code
    subprocess.TimeoutExpired
        If command execution exceeds timeout
    
    Examples
    --------
    >>> result = run(['swiftcomp', 'input.sc'], timeout=60)
    >>> print(result.returncode)
    0
    """

    # Input validation
    if not cmd:
        raise ValueError("cmd cannot be empty")
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")
    
    # Handle batch scripts on Windows - always work with a copy
    cmd = list(cmd)  # Convert to list (makes a copy)
    # Identify the solver by executable name before cmd[0] is replaced by
    # a cmd.exe wrapper or a resolved full path
    solver = os.path.splitext(os.path.basename(cmd[0]))[0].lower()
    if cmd[0].lower().endswith(('.bat', '.cmd')):
        # Wrap batch script with cmd.exe /c
        cmd = ['cmd.exe', '/c'] + cmd

    logger.info(' '.join(cmd))

    logger.debug("PATH used by Python:")
    for p in os.environ["PATH"].split(os.pathsep):
        logger.debug(f"  {p}")
    resolved = shutil.which(cmd[0])
    logger.debug(f"Resolved path: {resolved}")
    
    # Use resolved path if found to ensure subprocess can locate the executable
    if resolved:
        cmd[0] = resolved
        logger.debug(f"Using resolved path: {cmd[0]}")

    try:
        out = sbp.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )

        logger.info(f'return code: {out.returncode}')
        logger.debug(f'stdout:\n{out.stdout}')
        logger.debug(f'stderr: {out.stderr}')

        if solver.startswith(MSG_COMMANDS):
            _check_solver_output(solver, out.stdout, cmd)

        return out

    except sbp.CalledProcessError as e:
        logger.error(f"Command failed: {e.returncode}")
        logger.error(f"stderr: {e.stderr}")
        raise

    except sbp.TimeoutExpired as e:
        logger.error('Timeout expired', exc_info=e)
        raise

    except SwiftCompLicenseError as e:
        logger.error('Something wrong in the SwiftComp license...', exc_info=e)
        raise

    except VABSLicenseError as e:
        logger.error('Something wrong in the VABS license...', exc_info=e)
        raise

    except SwiftCompIOError as e:
        logger.error('Something wrong in the SwiftComp input...', exc_info=e)
        raise

    except VABSIOError as e:
        logger.error('Something wrong in the VABS input...', exc_info=e)
        raise

    except SwiftCompError as e:
        logger.error('SwiftComp execution error', exc_info=e)
        raise

    except VABSError as e:
        logger.error('VABS execution error', exc_info=e)
        raise


def _check_solver_output(solver: str, stdout: str, cmd: List[str]) -> None:
    """Raise if SwiftComp/VABS output does not report a successful run.

    The solvers exit with code 0 even on failure, so the last output lines
    are the only reliable success signal.

    Parameters
    ----------
    solver : str
        Lower-case executable name without extension (e.g. ``'swiftcomp'``).
    stdout : str
        Standard output of the solver run.
    cmd : list of str
        Executed command, used in the error message.

    Raises
    ------
    SwiftCompLicenseError, VABSLicenseError
        If the last output line reports a license problem.
    SwiftCompIOError, VABSIOError
        If the last output line reports an I/O error.
    SwiftCompError, VABSError
        If the output is empty or does not end with 'finished successfully'.
    """
    if solver.startswith('v'):
        license_error, io_error, solver_error = VABSLicenseError, VABSIOError, VABSError
    else:
        license_error, io_error, solver_error = (
            SwiftCompLicenseError, SwiftCompIOError, SwiftCompError)

    message = getScVabsMessage(stdout)
    logger.debug(f'message:\n{message}')

    # Success is reported on one of the last two lines
    if any('finished successfully' in line for line in message[-2:]):
        return

    scmd = ' '.join(cmd)
    if not message:
        raise solver_error(f'No output from <{scmd}>')

    last_message = message[-1]
    if 'license' in last_message:
        raise license_error(last_message)
    if 'I/O error' in last_message:
        raise io_error(last_message)
    raise solver_error(f'Something wrong with <{scmd}>: {last_message}')


def getScVabsMessage(stdout: str) -> List[str]:
    """Extract non-empty message lines from solver output.
    
    Parameters
    ----------
    stdout : str
        Standard output from SwiftComp or VABS solver
    
    Returns
    -------
    list of str
        Non-empty lines from output, with whitespace stripped
    
    Examples
    --------
    >>> output = "Line 1\\n\\nLine 2\\n  Line 3  \\n"
    >>> getScVabsMessage(output)
    ['Line 1', 'Line 2', 'Line 3']
    """
    return [line.strip() for line in stdout.splitlines() if line.strip()]

