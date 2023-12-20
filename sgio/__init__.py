from .core.sg import StructureGene
from .core.builder import buildSG1D
# from .core.solid import MaterialProperty
# from .core.shell import ShellProperty
# from .core.beam import BeamProperty
from .core.merge import combineSG

from .model import *

from .io import (
    read, readOutput, readLoadCsv, write,
    addPointDictDataToMesh,
    addCellDictDataToMesh,
    )

from .execu import run

# from . import utils

# from .meshio import *


