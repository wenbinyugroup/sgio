import os
import sys
import pprint
import sgio

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# import meshio
# import msgd.pkg.meshio as mpm

fn = sys.argv[1]
file_format = sys.argv[2]
format_version = sys.argv[3]
smdim = int(sys.argv[4])

fn_base, fn_ext = os.path.splitext(fn)

sg = sgio.read(fn, file_format, format_version, smdim)
print(sg)

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


fn_out = fn.split('.')
fn_out[-2] += '_write'
fn_out = '.'.join(fn_out)
ver_out = '2.1'
sg.write(fn_out, file_format, version=ver_out)
