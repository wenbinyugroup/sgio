from pathlib import Path
import logging
# from icecream import ic
# import inpRW
# from repr2 import repr2

import sgio

logger = logging.getLogger(__name__)

# Wrap in main to prevent execution during test collection
if __name__ == '__main__':
    sgio.configure_logging(cout_level='DEBUG')

    # Resolve path relative to this test file
    test_dir = Path(__file__).parent.parent
    fn = test_dir / 'files' / 'abaqus' / 'sg2_airfoil.inp'

    # ----------

    # inp = inpRW.inpRW(fn)
    # inp.parse()

    # print(inp.keywords)

    # for _set in inp.findKeyword('elset'):
    #     # print(_set)
    #     ic(_set.parameter)
    #     ic(_set.parameter.keys())
    #     ic(_set.data)

    # for _section in inp.findKeyword('solid section'):
    #     # print(_set)
    #     ic(_section.parameter)
    #     ic(_section.parameter.keys())
    #     ic(_section.data)

    # ----------

    sg = sgio.read(str(fn), 'abaqus')
    print(sg)

    # sgio.write(sg, f'{fn}.sg', 'abaqus')
