import os
import sys
# import pprint
import sgio

# import meshio
# import msgd.pkg.meshio as mpm

fn = sys.argv[1]
file_format = sys.argv[2]
smdim = int(sys.argv[3])

fn_base, fn_ext = os.path.splitext(fn)

sg = sgio.read(fn, file_format, smdim)
print(sg)

# mesh = mpm.read(fn)

# mesh._inspect(outstream=print)
# mesh._inspect(outstream=pprint.pprint)

# with open('debug.dat', 'w') as file:
#     mesh._inspect(outstream=file.write, append_newline=True)


# print(mesh)
# print('-'*40)
# print(dir(mesh))
# print('-'*40)
# pprint.pprint(mesh.__dict__)
# print('-'*40)
# print('mesh.cells')
# pprint.pprint(mesh.cells)
# print('-'*40)
# print('mesh.cells[0].data')
# pprint.pprint(mesh.cells[0].data)
# print('-'*40)
# print('mesh.cell_sets')
# pprint.pprint(mesh.cell_sets)

# fn = '.'.join([fn_base, 'msh'])
# mesh.write(fn, file_format='gmsh22', binary=False)
