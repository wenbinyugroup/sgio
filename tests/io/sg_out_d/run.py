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

sg = sgio.read(fn_sg, 'vabs', sgdim=2, model='bm2')
# print(sg.nelems)
state_case = sgio.readOutput(fn_sg, 'v', 'd')
# print(state_case)

# _u = state_field.getDisplacementField()
# print(_u)
sgio.addPointDictDataToMesh(name_u, state_case.getState('u').data, sg.mesh)
# _ee = state_field.getStrainField(where='e', cs='s')
# print(_ee)
sgio.addCellDictDataToMesh(name_e, state_case.getState('ee').data, sg.mesh)

# print(sg)

sgio.write(sg, fn_msh, 'gmsh', mesh_only=True)

