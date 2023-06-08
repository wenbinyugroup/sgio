import sys
import sgio

fn_sg1 = sys.argv[1]
fn_sg2 = sys.argv[2]
fn_out = sys.argv[3]

sg1 = sgio.read(fn_sg1, 'vabs', '4', 1)
sg2 = sgio.read(fn_sg2, 'vabs', '4', 1)

sg = sgio.mergeSG(sg1, sg2)

sg.write(fn_out, 'gmsh22')
