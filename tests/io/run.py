import os
import sys
import pprint
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
print('-'*40)
print('sg.mesh.points')
pprint.pprint(sg.mesh.points)
print('-'*40)
# print('mesh.cells')
# pprint.pprint(mesh.cells)
print('-'*40)
print('sg.mesh.cells[0]')
print('type:', sg.mesh.cells[0].type)
pprint.pprint(sg.mesh.cells[0].data)
print('-'*40)
print('sg.mesh.cell_data')
pprint.pprint(sg.mesh.cell_data)

# fn_out = fn.replace('.sg', '.inp')
# sg.mesh.write(fn_out, file_format='abaqus')
# fn_out = fn.replace('.sg', '.msh')
# sg.mesh.write(fn_out, file_format='gmsh22', binary=False)
