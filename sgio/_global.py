# import logging
# from rich.logging import RichHandler
from rich.console import Console
from rich.pretty import Pretty

console = Console()

def pprint(*args, **kwargs):
    console.print(Pretty(*args), **kwargs)

LOGGER_NAME = 'sgio'

SC_VERSION_DEFAULT = '2.1'
VABS_VERSION_DEFAULT = '4.0'

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

class SwiftCompLicenseError(Exception):
    pass

class VABSLicenseError(Exception):
    pass

class SwiftCompIOError(Exception):
    pass

class VABSIOError(Exception):
    pass

class SwiftCompError(Exception):
    pass

class VABSError(Exception):
    pass

class OutputFileError(Exception):
    pass
