"""Method 2: keep the SG parameters in SG manifests."""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

# sg2_box.sg.json references sg2_box_composite_section.inp and adds what the
# .inp cannot state: SG dimension, beam model and the plane the cross-section
# is drawn in.
sg = sgio.read(str(cwd / 'sg2_box.sg.json'), 'sg_manifest')
print(sg)

# Write a SwiftComp input together with its own manifest. SwiftComp owns the
# materials, sections and model space, so the new manifest only records the
# model file, sgdim and model type. The SwiftComp input is the same one
# run_1_api.py writes.
sgio.write(
    sg,
    str(cwd / 'sg2_box_sc.sg.json'),
    'sg_manifest',
    model_file='sg2_box.sc',
    model_file_format='swiftcomp',
)

# The SwiftComp manifest reads back as the same structure gene, with no
# arguments.
sg_sc = sgio.read(str(cwd / 'sg2_box_sc.sg.json'), 'sg_manifest')
print(sg_sc.sgdim, sg_sc.model_space, sg_sc.nnodes, sg_sc.nelems)
