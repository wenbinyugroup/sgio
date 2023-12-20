import sgio

fn_base = 'uh60a'
fn_sg = f'{fn_base}.sg'
fn_sg_fi = f'{fn_sg}.fi'
fn_msh = f'{fn_base}.msh'

name_sr = 'strength ratio'

sg = sgio.read(fn_sg, 'vabs', sgdim=2, smdim=1)
print(sg)

output = sgio.readOutput(fn_sg, 'v', 'fi')
_sr = output['strength_ratio']
sgio.addCellDictDataToMesh(name_sr, _sr, sg.mesh)

sgio.write(sg, fn_msh, 'gmsh22', mesh_only=True)

