import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent
sc_file = cwd / 'sg2_box.sc'

# The Abaqus input holds the mesh, materials and composite sections, but not
# the SG dimension, beam model or the plane the cross-section is drawn in.

# Method 1: pass the SG parameters as arguments.
sg = sgio.read(
    str(cwd / 'sg2_box_composite_section.inp'), 'abaqus',
    sgdim=2, model_type='BM1', model_space='xy',
)
sgio.write(sg, str(sc_file), 'sc')
api_output = sc_file.read_text()

# SwiftComp input defines sgdim and model space, but not the model type.
sg_sc = sgio.read(str(sc_file), 'sc', model_type='BM1')
print(sg_sc.sgdim, sg_sc.model_space, sg_sc.nnodes, sg_sc.nelems)

# Method 2: keep the SG parameters in SG manifests.
# sg2_box.sg.json references the Abaqus input and adds the SG parameters.
sg = sgio.read(str(cwd / 'sg2_box.sg.json'), 'sg_manifest')
print(sg)

# Write the SwiftComp input together with its own manifest. SwiftComp owns the
# materials, sections and model space, so the new manifest only records the
# model file, sgdim and model type.
sgio.write(
    sg,
    str(cwd / 'sg2_box_sc.sg.json'),
    'sg_manifest',
    model_file='sg2_box.sc',
    model_file_format='swiftcomp',
)

# Both methods write the same SwiftComp input.
assert sc_file.read_text() == api_output

# The SwiftComp manifest reads back as the same structure gene.
sg_sc = sgio.read(str(cwd / 'sg2_box_sc.sg.json'), 'sg_manifest')
print(sg_sc.sgdim, sg_sc.model_space, sg_sc.nnodes, sg_sc.nelems)
