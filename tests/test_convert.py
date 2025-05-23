# import logging
import os
import yaml

from sgio import convert, run, configure_logging, logger

configure_logging(cout_level='info')


test_case_files = [
    'test_convert_vabs_abaqus.yml',
    'test_convert_vabs_gmsh.yml',
    'test_convert_sc_abaqus.yml',
]


def test_convert(fn_test_cases, input_dir, output_dir):

    with open(f'{input_dir}/{fn_test_cases}', 'r') as file:
        test_cases = yaml.safe_load(file)

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for _i, _case in enumerate(test_cases):
        print()

        ff_in = _case['ff_in']
        ff_out = _case['ff_out']

        fn_in = f'{input_dir}/{_case["fn_in"]}'
        fn_out = f'{output_dir}/{_case["fn_out"]}'

        logger.info(f'Converting {fn_in} to {fn_out}...')

        convert(
            fn_in, fn_out,
            ff_in, ff_out,
            file_version_in=_case.get('version_in', None),
            file_version_out=_case.get('version_out', None),
            model_type=_case.get('model', None),
        )

        _solver = _case.get('solver', None)
        if _solver:
            run(_solver, fn_out, analysis='h', smdim=_case.get('model', None))



if __name__ == '__main__':
    input_dir = 'files'
    output_dir = '_temp'

    for fn_test_cases in test_case_files:
        test_convert(fn_test_cases, input_dir, output_dir)

