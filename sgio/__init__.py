from ._version import __version__

from .core.sg import StructureGene
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
]
