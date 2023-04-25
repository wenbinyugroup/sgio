
MSG_COMMANDS = (
    'swiftcomp', 'sc', 'vabs'
)

MSG_COMMAND_TO_NAME = {
    'swiftcomp': 'SwiftComp',
    'sc': 'SwiftComp',
    'vabs': 'VABS',
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


