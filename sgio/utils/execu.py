# import os
# import platform
# import signal
import logging
import subprocess as sbp


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


# class SwiftCompIOError(Exception):
#     pass




def run(cmd, timeout, max_try=3, **kwargs):

    # Handle batch scripts on Windows
    if isinstance(cmd, (list, tuple)) and len(cmd) > 0:
        cmd_name = cmd[0].lower()
        if cmd_name.endswith(('.bat', '.cmd')):
            # Wrap batch script with cmd.exe /c
            cmd = ['cmd.exe', '/c'] + list(cmd)

    logger.info(' '.join(cmd))

    _try = 0

    while _try < max_try:

        try:
            out = sbp.run(
                cmd,
                capture_output=True, timeout=timeout, encoding='UTF-8'
            )

            # print(out.stdout)

            logger.debug(f'return code: {out.returncode}')
            logger.debug(f'stdout:\n{out.stdout}')
            logger.debug(f'stderr:{out.stderr}')

            cmd_name = cmd[0].lower()

            if cmd_name.lower().startswith(MSG_COMMANDS):
                message = getScVabsMessage(cmd[0], out.stdout)

                # Success
                if ('finished successfully' in message[-2]) or ('finished successfully' in message[-1]):
                    if cmd[0].lower().startswith('s'):
                        logger.debug(message[-1])
                    elif cmd[0].lower().startswith('v'):
                        logger.debug(message[-2])
                    # return

                # Errors
                elif 'license' in message[-1]:
                    err_message = message[-1]
                    if cmd[0].lower().startswith('s'):
                        raise SwiftCompLicenseError(err_message)
                    elif cmd[0].lower().startswith('v'):
                        raise VABSLicenseError(err_message)

                elif 'I/O error' in message[-1]:
                    err_message = message[-1]
                    if cmd[0].lower().startswith('s'):
                        raise SwiftCompIOError(err_message)
                    elif cmd[0].lower().startswith('v'):
                        raise VABSIOError(err_message)

                else:
                    scmd = ' '.join(cmd)
                    err_message = f'Something wrong with <{scmd}>...'
                    if cmd[0].lower().startswith('s'):
                        raise SwiftCompError(err_message)
                    elif cmd[0].lower().startswith('v'):
                        raise VABSError(err_message)

        except sbp.TimeoutExpired as e:

            logger.error('Timeout expired', exc_info=e)
            # os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            # logger.critical('Process killed')

            if cmd_name.lower().startswith(MSG_COMMANDS):
                # Try again if the command is SwiftComp or VABS
                # Sometimes SwiftComp/VABS may not finish for no reason
                _try += 1
                continue

            else:
                break


        except SwiftCompLicenseError as e:
            logger.error('Something wrong in the SwiftComp license...', exc_info=e)
            break

        except VABSLicenseError as e:
            logger.error('Something wrong in the VABS license...', exc_info=e)
            break

        except SwiftCompIOError as e:
            logger.error('Something wrong in the SwiftComp input...', exc_info=e)
            break

        except VABSIOError as e:
            logger.error('Something wrong in the VABS input...', exc_info=e)
            break

        except SwiftCompError as e:
            logger.error('', exc_info=e)
            break

        except VABSError as e:
            logger.error('', exc_info=e)
            break

        else:
            break




def getScVabsMessage(code, stdout):
    r"""
    """
    message = []
    stdout = stdout.split('\n')
    for line in stdout:
        line = line.strip()
        if line == '':
            continue
        message.append(line)

    return message





# def importFunction(module_name, func_name):
#     r"""
#     """

#     try:
#         import_str = 'import {}'.format(module_name)
#         logger.info(import_str)
#         exec(import_str)
#         func_str = '{}.{}'.format(module_name, func_name)
#         logger.info('evaluating user function: {}'.format(func_str))
#         func_obj = eval(func_str)
#     except ImportError:
#         try:
#             import_str = 'from {} import {}'.format(module_name, func_name)
#             logger.info(import_str)
#             exec(import_str)
#             logger.info('evaluating user function: {}'.format(func_name))
#             func_obj = eval(func_str)
#         except ImportError:
#             print('something wrong when importing module:', module_name)


#     return func_obj
