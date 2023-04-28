import sys
import yaml
# import msgd.builder.presg as mbp
# import msgd.analysis.sg as mas

import sgio


fn = sys.argv[1]

with open(fn, 'r') as fobj:
    raw_input = yaml.safe_load(fobj)

sg_input = raw_input['sg'][0]
print(sg_input)

name = 'sg1'
sgdim = 1
smdim = 2
# params = sg_input['parameters']
layup = sg_input['design']
model = sg_input['model']['md2']
sgdb = {}
for sg in raw_input['sg']:
    if sg['type'] == 'material':
        sgdb[sg['name']] = sg


# mas.substituteParams(layup, params)
# print(layup)
# mas.substituteParams(model, params)
# print(model)

elem_type = model.get('element_type', 2)

# sg = mbp.buildSG(1, name, design=layup, model=model, sgdb=sgdb)
sg = sgio.buildSG1D(
    name, layup, sgdb, smdim,
    elem_type=elem_type
)

# sg.summary()
print(sg)

fn_sg = '{}.sg'.format(name)
sg.writeInput(fn_sg, 's', version='2.2')


