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
    cmd_name = cmd[0].lower()
    if cmd_name.endswith(('.bat', '.cmd')):
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

        cmd_name = cmd[0].lower()

        if cmd_name.startswith(MSG_COMMANDS):
            message = getScVabsMessage(out.stdout)

            logger.debug(f'message:\n{message}')

            # Check if message has content before accessing indices
            if not message:
                logger.warning('Empty message from solver output')
                return out

            # Success - check last two lines
            success_found = False
            if len(message) >= 2 and 'finished successfully' in message[-2]:
                logger.debug(message[-2])
                success_found = True
            elif len(message) >= 1 and 'finished successfully' in message[-1]:
                logger.debug(message[-1])
                success_found = True

            if success_found:
                return out

            # Errors - check last line
            last_message = message[-1]
            
            if 'license' in last_message:
                if cmd_name.startswith('s'):
                    raise SwiftCompLicenseError(last_message)
                elif cmd_name.startswith('v'):
                    raise VABSLicenseError(last_message)

            elif 'I/O error' in last_message:
                if cmd_name.startswith('s'):
                    raise SwiftCompIOError(last_message)
                elif cmd_name.startswith('v'):
                    raise VABSIOError(last_message)

            else:
                scmd = ' '.join(cmd)
                err_message = f'Something wrong with <{scmd}>...'
                if cmd_name.startswith('s'):
                    raise SwiftCompError(err_message)
                elif cmd_name.startswith('v'):
                    raise VABSError(err_message)

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

