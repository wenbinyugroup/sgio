"""Method 1: pass the SG parameters as arguments of ``sgio.read``."""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

sc_file = cwd / 'sg2_box.sc'

# The Abaqus input holds the mesh, materials and composite sections, but not
# the SG dimension, beam model or the plane the cross-section is drawn in.
sg = sgio.read(
    str(cwd / 'sg2_box_composite_section.inp'), 'abaqus',
    sgdim=2, model_type='BM1', model_space='xy',
)
print(sg)

sgio.write(sg, str(sc_file), 'sc')

# SwiftComp input defines sgdim and model space, but not the model type.
sg_sc = sgio.read(str(sc_file), 'sc', model_type='BM1')
print(sg_sc.sgdim, sg_sc.model_space, sg_sc.nnodes, sg_sc.nelems)
