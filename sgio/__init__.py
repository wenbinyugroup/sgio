from .core.sg import StructureGene
from .core.builder import buildSG1D
# from .core.solid import MaterialProperty
# from .core.shell import ShellProperty
# from .core.beam import BeamProperty
from .core.merge import mergeSG

from .model import MaterialSection, BeamModel, SectionResponse, StructureResponseCases

from .io.main import read, readOutput, readLoadCsv, write

from .execu import run

# from . import utils


