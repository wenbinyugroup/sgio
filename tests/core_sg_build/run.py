import sys
import yaml
# import msgd.builder.presg as mbp
# import msgd.analysis.sg as mas

import sgio

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


fn = sys.argv[1]

with open(fn, 'r') as fobj:
    raw_input = yaml.safe_load(fobj)

sg_input = raw_input['sg'][0]
# print(sg_input)

name = 'sg1'
sgdim = 1
smdim = 2
# params = sg_input['parameters']
layup_design = sg_input['design']
model = sg_input['model']['md2']
version = model.get('version', '2.2')
sgdb = {}
for sg in raw_input['sg']:
    if sg['type'] == 'material':
        sgdb[sg['name']] = [
            {'property': sg['property']},
        ]


# mas.substituteParams(layup, params)
# print(layup)
# mas.substituteParams(model, params)
# print(model)

elem_type = model.get('element_type', 2)

# layer_list = sgio.core.builder.generateLayerList(layup_design)
# print(layer_list)

sg = sgio.buildSG1D(
    name, layup_design, sgdb, smdim,
    elem_type=elem_type
)


# sg.summary()
print(sg)

fn_sg = '{}.sg'.format(name)
sgio.write(sg, fn_sg, 'sc', version=version)


