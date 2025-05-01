import sgio

ver = '4.0'
fn_base = 'files/vabs/version_4_0/uh60a'
fn_sg = f'{fn_base}.sg'
fn_sg_fi = f'{fn_sg}.fi'
fn_msh = f'{fn_base}.msh'

name_sr = 'strength ratio'

sg = sgio.read(fn_sg, 'vabs', sgdim=2, smdim=1)
print(sg)

state_case = sgio.readOutputState(fn_sg, 'v', 'fi', sg=sg, tool_version=ver)
print(state_case)
_sr = state_case.getState('fi').data
# print(_sr)
sgio.addCellDictDataToMesh(name_sr, _sr, sg.mesh)

sgio.write(sg, fn_msh, 'gmsh', format_version='4.1', mesh_only=True)

