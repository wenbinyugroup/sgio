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


def configure_logging(
    cout_level='INFO',
    fout_level='INFO',
    filename='sgio.log',
    file_mode='a',
    propagate=True,
    clear_handlers=True
):
    """Configure SGIO logging.

    This function configures the 'sgio' logger with console and file handlers.
    By default, logs propagate to parent loggers (e.g., root logger) for
    integration with centralized logging setups.

    Parameters
    ----------
    cout_level : {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, optional
        Console output level, by default 'INFO'
    fout_level : {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, optional
        File output level, by default 'INFO'
    filename : str, optional
        Path to log file, by default 'sgio.log'
    file_mode : {'a', 'w'}, optional
        File mode: 'a' for append (accumulate logs across runs),
        'w' for overwrite (fresh log file each time), by default 'a'
    propagate : bool, optional
        If True, logs propagate to parent loggers (e.g., root logger),
        allowing centralized logging. If False, logs are isolated to SGIO
        handlers only. By default True.
    clear_handlers : bool, optional
        If True, clear existing handlers before adding new ones to prevent
        duplicate log messages. By default True.

    Examples
    --------
    Basic usage with default settings (append mode, propagation enabled):

    >>> import sgio
    >>> sgio.configure_logging(cout_level='INFO', filename='run.log')

    Overwrite log file each run:

    >>> sgio.configure_logging(file_mode='w', filename='run.log')

    Isolate SGIO logs (don't send to root logger):

    >>> sgio.configure_logging(propagate=False)

    Multi-package application with centralized logging:

    >>> import logging
    >>> # Configure root logger first
    >>> logging.basicConfig(
    ...     level=logging.DEBUG,
    ...     handlers=[logging.FileHandler('app.log')]
    ... )
    >>> # Now configure SGIO - logs will reach both SGIO and root handlers
    >>> import sgio
    >>> sgio.configure_logging(cout_level='INFO')

    Notes
    -----
    - The 'sgio' logger level is always set to DEBUG internally. Use handler
      levels (cout_level, fout_level) to control what gets logged.
    - Child module loggers (e.g., sgio.core.builder) automatically propagate
      to the 'sgio' logger when propagate=True.
    - For multi-package applications, consider configuring the root logger
      instead of calling this function. See the logging guide for details.
    """
    # Clear existing handlers if requested
    if clear_handlers and logger.handlers:
        # Close handlers properly before removing
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    # Set logger level to DEBUG (handlers control actual output)
    logger.setLevel('DEBUG')

    # Console handler with Rich formatting
    ch = RichHandler()
    ch.setLevel(cout_level.upper())
    cf = logging.Formatter(
        fmt='{message:s}',
        style='{',
        datefmt='[%X]'
    )
    ch.setFormatter(cf)
    logger.addHandler(ch)

    # File handler with Rich formatting
    # Use specified file_mode ('a' for append, 'w' for overwrite)
    file_console = Console(file=open(filename, file_mode), width=120)
    fh = RichHandler(console=file_console)
    fh.setLevel(fout_level.upper())
    ff = logging.Formatter(
        fmt='{message:s}',
        style='{',
        datefmt='[%X]'
    )
    fh.setFormatter(ff)
    logger.addHandler(fh)

    # Control propagation to parent loggers
    logger.propagate = propagate



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


