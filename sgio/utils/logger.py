import logging


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
    logger = logging.getLogger(name)
    logger.setLevel('DEBUG')

    ch = logging.StreamHandler()
    ch.setLevel(cout_level.upper())

    fh = logging.FileHandler(filename)
    fh.setLevel(fout_level.upper())

    # c_format = logging.Formatter(
    #     '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s'
    # )
    cf = logging.Formatter(
        fmt='[{levelname}] {message}', style='{'
    )
    ch.setFormatter(cf)

    ff = logging.Formatter(
        fmt='{levelname:8s} [{asctime}] {module}.{funcName} :: {message} ',
        datefmt='%Y-%m-%d %H:%M:%S', style='{'
    )
    fh.setFormatter(ff)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

