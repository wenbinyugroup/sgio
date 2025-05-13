import os
import yaml

from sgio import (
    read,
    readOutputState,
    addCellDictDataToMesh,
    write,
    configure_logging,
    logger,
    )

configure_logging(cout_level='info')

test_case_files = [
    'test_io_vabs_out_fi.yml',
]

name_sr = 'strength ratio'


def test_io_vabs_out_state_f(fn_test_cases, input_dir, output_dir):

    with open(f'{input_dir}/{fn_test_cases}', 'r') as file:
        test_cases = yaml.safe_load(file)

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for _i, _case in enumerate(test_cases):
        print()

        # ver = '4.0'
        # fn_base = 'files/vabs/version_4_0/uh60a'
        # fn_sg = f'{fn_base}.sg'
        # fn_sg_fi = f'{fn_sg}.fi'
        # fn_msh = f'{fn_base}.msh'
        fn_in = f'{input_dir}/{_case["fn_in"]}'
        ff_in = _case['ff_in']
        version_in = _case['version_in']
        num_cases = _case.get('num_cases', 1)
        logger.info(f'num_cases: {num_cases}')

        # Read the cross-section model
        sg = read(fn_in, ff_in)
        # print(sg)

        # Read the output state
        state_cases = readOutputState(
            fn_in, ff_in, 'fi', sg=sg, tool_version=version_in, num_cases=num_cases)
        logger.info(state_cases)

        # Add data to the mesh
        for j, state_case in enumerate(state_cases):
            logger.info(f'state case {j+1}')

            addCellDictDataToMesh(
                f'case{j+1}_fi', state_case.getState('fi').data, sg.mesh)
            addCellDictDataToMesh(
                f'case{j+1}_sr', state_case.getState('sr').data, sg.mesh)

        if 'fn_out' in _case.keys():
            fn_out = f'{output_dir}/{_case["fn_out"]}'
            ff_out = _case['ff_out']
            format_version = _case['format_version']

            # Write the mesh to a file
            write(sg, fn_out, ff_out, format_version=format_version)




if __name__ == '__main__':
    input_dir = 'files'
    output_dir = '_temp'

    for fn_test_cases in test_case_files:
        test_io_vabs_out_state_f(fn_test_cases, input_dir, output_dir)

