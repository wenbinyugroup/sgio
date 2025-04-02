from ._version import __version__

from .core.sg import StructureGene
from .core.builder import buildSG1D
# from .core.solid import MaterialProperty
# from .core.shell import ShellProperty
# from .core.beam import BeamProperty
from .core.merge import combineSG

from .model import *

from .iofunc import (
    read, readOutput, readOutputModel, readOutputState,
    readLoadCsv, write, convert,
    addPointDictDataToMesh,
    addCellDictDataToMesh,
    )

from .execu import run

# from . import utils

# from .meshio import *

__all__ = [
    'read',
    'readOutput',
    'readOutputModel',
    'readOutputState',
    'readLoadCsv',
    'write',
    'convert',
    'addPointDictDataToMesh',
    'addCellDictDataToMesh',
    'run',
    'StructureGene',
    'buildSG1D',
    'combineSG'
]
