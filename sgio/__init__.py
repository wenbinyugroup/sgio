from ._version import __version__

from ._global import logger, configure_logging

from ._exceptions import (
    SwiftCompLicenseError,
    VABSLicenseError,
    SwiftCompIOError,
    VABSIOError,
    SwiftCompError,
    VABSError,
    OutputFileError,
)

from .core import (
    StructureGene,
    check_isolated_nodes,
    renumber_elements,
    )
from .core.builder import buildSG1D
# from .core.solid import MaterialProperty
# from .core.shell import ShellProperty
# from .core.beam import BeamProperty
from .core.merge import combineSG

from .model import *

from .iofunc import (
    read,
    readOutput,
    readOutputModel,
    readOutputState,
    write,
    convert,
    readLoadCsv,
    # write_points_cells,
    # register_format,
    # deregister_format,
    # extension_to_filetypes,
    # sg_reader_map,
    # sg_writer_map,
    # overridden_formats
)

from .execu import run

# from . import utils

# from .meshio import *

__all__ = [
    "configure_logging",
    "read",
    "readOutput",
    "readOutputModel",
    "readOutputState",
    "write",
    "convert",
    "readLoadCsv",
    'run',
    'buildSG1D',
    'combineSG'
    "SGMesh",
    'StructureGene',
    "SwiftCompLicenseError",
    "VABSLicenseError",
    "SwiftCompIOError",
    "VABSIOError",
    "SwiftCompError",
    "VABSError",
    "OutputFileError",
]
