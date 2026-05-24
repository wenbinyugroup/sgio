import logging
import sys
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent
sys.path.insert(0, str(cwd.parent))

from _bundle_helpers import write_gmsh_bundle_sidecars

sg = sgio.convert(
    str(cwd / 'sg2_airfoil.inp'),  # Name of the Abaqus inp file.
    str(cwd / 'sg2_airfoil.sg'),  # Name of the VABS file.
    'abaqus', # Format of the CS data converted from.
    'vabs', # Format of the CS data converted to.
    sgdim=2, # Cross-section mesh lies in a 2D plane.
    model_type='bm2', # Structural model: Timoshenko.
)

# Export the converted section to a SG-on-Gmsh bundle for visualization or
# downstream bundle-based workflows.
sgio.write(
    sg=sg,
    filename=str(cwd / 'main.msh'),
    file_format='gmsh',
    format_version='4.1',
    model_type='BM2',
    binary=False,
)
write_gmsh_bundle_sidecars(sg, cwd)


