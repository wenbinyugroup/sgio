import logging
import os
import subprocess as sbp
import yaml


logging.basicConfig(level=logging.DEBUG)


test_case_files = [
    'test_convert_vabs_abaqus.yml',
    'test_convert_vabs_gmsh.yml',
    'test_convert_sc_abaqus.yml',
]


def test_convert(fn_test_cases, input_dir, output_dir):
    # file_dir = 'files'

    with open(f'{input_dir}/{fn_test_cases}', 'r') as file:
        test_cases = yaml.safe_load(file)

    # output_dir = '_temp'
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for _i, _case in enumerate(test_cases):
        ff_in = _case['ff_in']
        ff_out = _case['ff_out']

        fn_in = f'{input_dir}/{_case["fn_in"]}'
        fn_out = f'{output_dir}/{_case["fn_out"]}'

        logging.info(f'Converting {fn_in} to {fn_out}...')

        cmd = [
            'python', '-m', 'sgio', 'convert',
            fn_in,
            fn_out,
            '-ff', ff_in,
            '-tf', ff_out,
        ]

        if 'version_in' in _case:
            cmd.append('-ffv')
            cmd.append(_case['version_in'])

        if 'version_out' in _case:
            cmd.append('-tfv')
            cmd.append(_case['version_out'])

        if 'model' in _case:
            cmd.append('-m')
            cmd.append(_case['model'])

        sbp.run(cmd, check=True)



if __name__ == '__main__':
    input_dir = 'files'
    output_dir = '_temp'

    for fn_test_cases in test_case_files:
        test_convert(fn_test_cases, input_dir, output_dir)

