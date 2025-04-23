# import inpRW
# from repr2 import repr2

import sgio

fn = 'files/abaqus/sg2_box_solid_section.inp'

# inp = inpRW.inpRW(fn)
# inp.parse()

# print(repr2(inp))

sg = sgio.read(fn, 'abaqus')
print(sg)
