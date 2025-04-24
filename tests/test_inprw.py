import logging
# import inpRW
# from repr2 import repr2

import sgio

logger = logging.getLogger(__name__)

sgio.configure_logging(cout_level='DEBUG')

fn = 'files/abaqus/sg2_box_solid_section.inp'

# inp = inpRW.inpRW(fn)
# inp.parse()

# print(repr2(inp))

sg = sgio.read(fn, 'abaqus')
print(sg)
