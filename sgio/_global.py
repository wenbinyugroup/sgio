import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.pretty import Pretty

# from sgio.utils.logging import initLogger

logger = logging.getLogger('sgio')
console = Console()

def pprint(*args, **kwargs):
    console.print(Pretty(*args), **kwargs)


def pretty_string(v):
    return Pretty(v).__str__()


def configure_logging(cout_level='INFO', fout_level='INFO', filename='log.txt'):
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

    # logger = logging.getLogger(name)
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

    # fh = logging.FileHandler(filename)
    console = Console(file=open(filename, 'w'), width=120)
    fh = RichHandler(console=console)
    fh.setLevel(fout_level.upper())
    # ff = logging.Formatter(
    #     fmt='[{asctime}] {levelname:8s} {module}.{funcName} :: {message} ',
    #     datefmt='%H:%M:%S', style='{'
    # )
    ff = logging.Formatter(
        fmt='{message:s}',
        style='{',
        datefmt='[%X]'
    )
    fh.setFormatter(ff)
    logger.addHandler(fh)


    # logging.basicConfig(
    #     level=logging.INFO,
    #     # format="%(name)s: %(message)s",  # Include logger name in format
    #     # datefmt="[%X]",
    #     handlers=[ch, fh]
    # )

    logger.propagate = False


    # return logger



# Configure logging
# configure_logging()

SC_VERSION_DEFAULT = '2.1'
VABS_VERSION_DEFAULT = '4.1'

MSG_COMMANDS = (
    'swiftcomp', 'sc', 'vabs'
)

MSG_COMMAND_TO_NAME = {
    'swiftcomp': 'SwiftComp',
    'sc': 'SwiftComp',
    'vabs': 'VABS',
}

FAILURE_CRITERION_NAME_TO_ID = {
    'max_principal_stress': 1,
    'max_principal_strain': 2,
    'max_shear_stress': 3,
    'tresca': 3,
    'max_shear_strain': 4,
    'mises': 5,
    'max_stress': 1,
    'max_strain': 2,
    'tsai-hill': 3,
    'tsai-wu': 4,
    'hashin': 5
}


