import sgio

import yaml

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



def convert(
    fn_base, sgdim, model_type,
    file_format_in, file_ext_in, format_version_in,
    file_format_out, file_ext_out, format_version_out, dir_out
    ):

    logger.critical("converting sg input from {}.{} ({} v{}) to {}.{} ({} v{})...".format(
        fn_base, file_ext_in, file_format_in, format_version_in,
        fn_base, file_ext_out, file_format_out, format_version_out
    ))

    # fn_base = 'sg21eb_tri6_sc21'
    fn_in = f'../../../files/{fn_base}.{file_ext_in}'
    fn_out = f'{dir_out}/{fn_base}.{file_ext_out}'
    # file_format_in = 'sc'
    # format_version_in = '2.1'
    # file_format_out = 'gmsh22'
    # format_version_out = '2.2'
    # smdim = 1

    sg = sgio.read(fn_in, file_format_in, format_version=format_version_in, model_type=model_type, sgdim=sgdim)
    print(sg)
    # print(sg.mesh.cell_data['property_id'])
    sgio.write(sg, fn_out, file_format_out, format_version=format_version_out, model_type=model_type)



if __name__ == '__main__':
    # fn_dir = 'sg_to_gmsh'
    fn_dir = 'abq_to_sg'

    fn_test_cases = f'{fn_dir}/test_cases.yml'

    with open(fn_test_cases, 'r') as file:
        test_cases = yaml.safe_load(file)

    for _i, _case in enumerate(test_cases):
        convert(
            _case['fn_base'], _case['sgdim'], _case['model_type'],
            _case['file_format_in'], _case['file_ext_in'], _case['format_version_in'],
            _case['file_format_out'], _case['file_ext_out'], _case['format_version_out'], fn_dir
            # 'gmsh22', 'msh', '2.2'
        )
        print()
