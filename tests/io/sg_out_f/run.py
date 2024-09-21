import sgio

fn_base = 'uh60a'
fn_sg = f'{fn_base}.sg'
fn_sg_fi = f'{fn_sg}.fi'
fn_msh = f'{fn_base}.msh'

name_sr = 'strength ratio'

sg = sgio.read(fn_sg, 'vabs', sgdim=2, smdim=1)
print(sg)

state_case = sgio.readOutputState(fn_sg, 'v', 'fi')
print(state_case)
_sr = state_case.getState('fi').data
# print(_sr)
sgio.addCellDictDataToMesh(name_sr, _sr, sg.mesh)

sgio.write(sg, fn_msh, 'gmsh', mesh_only=True)

