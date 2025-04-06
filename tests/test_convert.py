import logging
import os
import yaml

from sgio import convert


logging.basicConfig(level=logging.DEBUG)


def test_convert_vabs_abaqus():
    file_dir = 'files'

    fn_test_cases = f'{file_dir}/test_convert_vabs_abaqus.yml'
    with open(fn_test_cases, 'r') as file:
        test_cases = yaml.safe_load(file)

    output_dir = '_temp'
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for _i, _case in enumerate(test_cases):
        ff_in = _case['ff_in']
        ff_out = _case['ff_out']

        fn_in = f'{file_dir}/{ff_in}/{_case["fn_in"]}'
        fn_out = f'{output_dir}/{_case["fn_out"]}'

        convert(
            fn_in,
            fn_out,
            ff_in,
            ff_out,
            file_version_out=_case['version_out'],
            model_type=_case['model'],
        )



if __name__ == '__main__':
    test_convert_vabs_abaqus()
