import logging
from rich.logging import RichHandler

# import sgio._global as GLOBAL

def initLogger(name, cout_level='INFO', fout_level='INFO', filename='log.txt'):
    """Initialization of a logger.

    Parameters
    ----------
    name : str
        Name of the logger.
    cout_level : {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, optional
        Output level of logs to the screen, by default 'INFO'
    fout_level : {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, optional
        Output level of logs to a file, by default 'INFO'
    filename : str, optional
        Name of the log file, by default 'log.txt'

    Returns
    -------
    :obj:`logging.Logger`
        A logger object.
    """
    # if name != GLOBAL.LOGGER_NAME:
    #     GLOBAL.LOGGER_NAME = name

    logger = logging.getLogger(name)
    logger.setLevel('DEBUG')

    # ch = logging.StreamHandler()
    ch = RichHandler()
    ch.setLevel(cout_level.upper())
    # ch.setFormatter(CustomFormatter())
    cf = logging.Formatter(
        fmt='{message:s}',
        style='{',
        datefmt='[%X]'
    )
    ch.setFormatter(cf)
    logger.addHandler(ch)


    fh = logging.FileHandler(filename)
    fh.setLevel(fout_level.upper())
    ff = logging.Formatter(
        fmt='[{asctime}] {levelname:8s} {module}.{funcName} :: {message} ',
        datefmt='%H:%M:%S', style='{'
    )
    fh.setFormatter(ff)
    logger.addHandler(fh)


    return logger
