import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

# The Abaqus input holds the mesh, materials and composite sections. The SG
# manifest adds what the .inp cannot state: SG dimension, beam model and the
# plane the cross-section is drawn in.
sg = sgio.read(str(cwd / 'sg2_box.sg.json'), 'sg_manifest')
print(sg)

# Write a SwiftComp input together with its own manifest. SwiftComp owns the
# materials, sections and model space, so the new manifest only records the
# model file, sgdim and model type.
sgio.write(
    sg,
    str(cwd / 'sg2_box_sc.sg.json'),
    'sg_manifest',
    model_file='sg2_box.sc',
    model_file_format='swiftcomp',
)

# The SwiftComp manifest reads back as the same structure gene.
sg_sc = sgio.read(str(cwd / 'sg2_box_sc.sg.json'), 'sg_manifest')
print(sg_sc.sgdim, sg_sc.model_space, sg_sc.nnodes, sg_sc.nelems)
