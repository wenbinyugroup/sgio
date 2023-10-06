import sys
import sgio
import numpy as np

fn_sg1 = sys.argv[1]
fn_sg2 = sys.argv[2]
fn_out = sys.argv[3]

sg1 = sgio.read(fn_sg1, 'vabs', '4', 1)
sg2 = sgio.read(fn_sg2, 'vabs', '4', 1)
print('\nsg 1')
print(sg1)
print('\nsg 2')
print(sg2)

# Transform mesh
sg2.mesh.points += np.array([10, 0, 0])


sg = sgio.combineSG(sg1, sg2)
print('\nsg combined')
print(sg)

# sg.write(fn_out, 'gmsh22')
sgio.write(sg, fn_out, 'gmsh22', mesh_only=True)
