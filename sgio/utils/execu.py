import os
import platform
import signal
import subprocess as sbp
import sgio.utils.logger as mul


def run(cmd, timeout, scrnout, logger=None):
    if logger is None:
        logger = mul.initLogger(__name__)

    logger.critical(' '.join(cmd))
    # proc = sbp.Popen(cmd, stdout=sbp.PIPE, stderr=sbp.PIPE)
    # print('command: ', cmd)
    if platform.system() == 'Windows':
        if scrnout:
            # sbp.call(cmd)
            proc = sbp.Popen(cmd)
        else:
            # proc = sbp.Popen(cmd, stdout=sbp.DEVNULL, stderr=sbp.STDOUT)
            proc = sbp.Popen(cmd, stdout=sbp.PIPE, stderr=sbp.STDOUT)

        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            # print('exit code:', proc.returncode)
            # print(stdout)
            if logger:
                # logger.debug(f'exit code: {proc.returncode}')
                logger.debug('exit code: {0}'.format(proc.returncode))
                logger.debug(stdout)
                # logger.debug(stdout.decode())
        except sbp.TimeoutExpired as e:
            # print('exit code:', proc.returncode)
            # print(stderr)
            if logger:
                # logger.debug(f'exit code: {proc.returncode}')
                logger.debug('exit code: {0}'.format(proc.returncode))
                # logger.debug(stdout.decode())
                # logger.debug(stderr.decode())

            logger.critical('TimeoutExpired')
            proc.kill()
            logger.critical('Process killed')


    elif platform.system() == 'Linux':
        # sbp.run(["$PATH"])

        # if scrnout:
        #     # sbp.call(cmd)
        #     proc = sbp.Popen(cmd)
        # else:
        #     # proc = sbp.Popen(cmd, stdout=sbp.DEVNULL, stderr=sbp.STDOUT, preexec_fn=os.setsid)
        #     proc = sbp.Popen(cmd, stdout=sbp.PIPE, stderr=sbp.STDOUT, preexec_fn=os.setsid)

        try:
            sbp.run(cmd, timeout=timeout)
            # stdout, stderr = proc.communicate(timeout=timeout)
            # print('exit code:', proc.returncode)
            # print(stdout)
            # if logger:
            #     # logger.debug(f'exit code: {proc.returncode}')
            #     logger.debug('exit code: {0}'.format(proc.returncode))
            #     logger.debug(stdout)
            #     # logger.debug(stdout.decode())
        except sbp.TimeoutExpired as e:
            # print('exit code:', proc.returncode)
            # print(stderr)
            # if logger:
            #     # logger.debug(f'exit code: {proc.returncode}')
            #     logger.debug('exit code: {0}'.format(proc.returncode))
            #     # logger.debug(stdout.decode())
            #     # logger.debug(stderr.decode())

            logger.critical('TimeoutExpired')
            # os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            logger.critical('Process killed')

