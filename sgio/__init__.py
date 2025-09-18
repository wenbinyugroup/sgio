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
    SGMesh,
    check_isolated_nodes,
    renumber_elements,
    )
from .core.builder import buildSG1D
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
    addCellDictDataToMesh,
    addPointDictDataToMesh,
    # write_points_cells,
    # register_format,
    # deregister_format,
    # extension_to_filetypes,
    # sg_reader_map,
    # sg_writer_map,
    # overridden_formats
)

from .execu import run

from .utils import (
    plot_sg_2d,
)

from ._vendors import inprw

__all__ = [
    # Version
    "__version__",
    # Configuration and logging
    "configure_logging",
    # I/O functions
    "read",
    "readOutput",
    "readOutputModel",
    "readOutputState",
    "write",
    "convert",
    "readLoadCsv",
    "addCellDictDataToMesh",
    "addPointDictDataToMesh",
    # Execution
    "run",
    # Core functions and classes
    "buildSG1D",
    "combineSG",
    "SGMesh",
    "StructureGene",
    "check_isolated_nodes",
    "renumber_elements",
    # Utility functions
    "plot_sg_2d",
    # Model classes from .model import *
    "CauchyContinuumModel",
    "KirchhoffLovePlateShellModel",
    "ReissnerMindlinPlateShellModel",
    "EulerBernoulliBeamModel",
    "TimoshenkoBeamModel",
    # Exception classes
    "SwiftCompLicenseError",
    "VABSLicenseError",
    "SwiftCompIOError",
    "VABSIOError",
    "SwiftCompError",
    "VABSError",
    "OutputFileError",
]
