import sys
import yaml
# import msgd.builder.presg as mbp
# import msgd.analysis.sg as mas

import sgio

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Wrap in main to prevent execution during test collection
if __name__ == '__main__':
    fn = sys.argv[1]

    with open(fn, 'r') as fobj:
        raw_input = yaml.safe_load(fobj)

    sg_input = raw_input['layup']
    # print(sg_input)

    sg_name = sg_input.get('name', 'laminate')
    sg_dim = 1

    # params = sg_input['parameters']
    sg_design_input = sg_input['design']

    sg_model_input = sg_input['model']
    model_type = sg_model_input['type']
    # smdim = 2
    mesh_size = sg_model_input.get('mesh_size', 0)
    elem_type = sg_model_input.get('element_type', 2)
    version = sg_model_input.get('version', '2.2')

    mdb = {}
    for _m in raw_input['material']:
        # if sg['type'] == 'material':
        mdb[_m['name']] = {'property': _m['property']}


    # mas.substituteParams(layup, params)
    # print(layup)
    # mas.substituteParams(model, params)
    # print(model)


    # layer_list = sgio.core.builder.generateLayerList(layup_design)
    # print(layer_list)

    sg = sgio.buildSG1D(
        name=sg_name,
        layup=sg_design_input,
        sgdb=mdb,
        model=model_type,
        mesh_size=mesh_size,
        elem_type=elem_type,
    )


    # sg.summary()
    print(sg)
    print(sg.mesh.points)
    print(sg.mesh.cells[0].data)

    fn_sg = '{}.sg'.format(sg_name)
    sgio.write(sg, fn_sg, 'sc', format_version=version, model_space='z')


