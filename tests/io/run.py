import os
import sys
import pprint
import sgio

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# import meshio
# import msgd.pkg.meshio as mpm

fn_base = 'sg23_tri3_quad4.sc'
# fn_base = 'sg21eb_tri3_vabs40'

fn_in = f'../files/{fn_base}'
file_format_in = 'sc'
format_version_in = '2.1'
fn_out = fn_base.replace('.sc', '.msh')
file_format_out = 'gmsh22'
format_version_out = '2.2'
smdim = 1


sg = sgio.read(fn_in, file_format_in, format_version_in, smdim)
print(sg)

# fn_base, fn_ext = os.path.splitext(fn)


# mesh = mpm.read(fn)

# mesh._inspect(outstream=print)
# mesh._inspect(outstream=pprint.pprint)

# with open('debug.dat', 'w') as file:
#     mesh._inspect(outstream=file.write, append_newline=True)


# print(mesh)
# print('-'*40)
# print(dir(mesh))
print('='*40)
print('sg.mesh.points')
pprint.pprint(sg.mesh.points)
print('-'*40)
# print('mesh.cells')
# pprint.pprint(mesh.cells)
print('-'*40)
print('sg.mesh.cells')
for i, cb in enumerate(sg.mesh.cells):
    print('type:', cb.type)
    pprint.pprint(cb.data)
print('-'*40)
for dname, dvalues in sg.mesh.cell_data.items():
    print('quantity:', dname)
    pprint.pprint(dvalues)
print('='*40)
print('materials')
for i, mp in sg.materials.items():
    print('-'*40)
    print('material:', i)
    print(mp)


sgio.write(sg, fn_out, file_format_out, version=format_version_out)
