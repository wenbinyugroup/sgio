import logging
logger = logging.getLogger(__name__)

from sgio.core.sg import StructureGene
import sgio.meshio as smsh


# ====================================================================
# Readers
# ====================================================================


# Read input
# ----------

def readInputBuffer(file, smdim:int):
    """
    """
    sg = StructureGene()
    sg.smdim = smdim

    # Read mesh
    sg.mesh = _readMesh()

    # Read materials and sections

    return sg




def _readMesh(file, sgdim:int, nnode:int, nelem:int, read_local_frame):
    """
    """

    logger.debug('reading mesh...')

    mesh = smsh.read(
        file, 'abaqus',
        sgdim=sgdim, nnode=nnode, nelem=nelem, read_local_frame=read_local_frame
    )

    return mesh
