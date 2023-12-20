import sgio

fn_base = 'uh60a'
fn_sg = f'{fn_base}.sg'
fn_sg_ele = f'{fn_sg}.ele'
fn_msh = f'{fn_base}.msh'

name_u = 'u'
# name_u = ['u1', 'u2', 'u3']
name_e = [
    'e11', '2e12', '2e13', 'e22', '2e23', 'e33'
]

sg = sgio.read(fn_sg, 'vabs', sgdim=2, smdim=1)
# print(sg.nelems)
state_field = sgio.readOutput(fn_sg, 'v', 'd')
_u = state_field.getDisplacementField()
# print(_u)
sgio.addPointDictDataToMesh(name_u, _u, sg.mesh)
_ee = state_field.getStrainField(where='e', cs='s')
# print(_ee)
sgio.addCellDictDataToMesh(name_e, _ee, sg.mesh)

print(sg)

sgio.write(sg, fn_msh, 'gmsh22', mesh_only=True)

