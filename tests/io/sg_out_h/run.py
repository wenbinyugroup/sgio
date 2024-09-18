import sgio

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

test_cases = [
    {
        'fn_base': 'sg21eb_tri6_sc21',
        'file_format': 'sc',
        'model': 'BM1',
        # 'smdim': 1,
        # 'submodel': 1
    },
    {
        'fn_base': 'sg21eb_tri3_vabs40',
        'file_format': 'vabs',
        'model': 'BM1',
        # 'smdim': 1,
        # 'submodel': 1
    },
    {
        'fn_base': 'sg21t_tri6_sc21',
        'file_format': 'sc',
        'model': 'BM2',
        # 'smdim': 1,
        # 'submodel': 2
    },
    {
        'fn_base': 'sg21t_tri3_vabs40',
        'file_format': 'vabs',
        'model': 'BM2',
        # 'smdim': 1,
        # 'submodel': 2
    },
]

analysis = 'h'

for _case in test_cases:

    fn = f"../../files/{_case['fn_base']}.sg.k"

    model = sgio.readOutput(
        fn, _case['file_format'],
        analysis=analysis, model_type=_case['model'],
        # smdim=_case['smdim'], submodel=_case['submodel']
    )

    print('\n')
    print('='*32)
    print(model.dim)
    print(model)
