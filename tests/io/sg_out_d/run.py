import sgio

fn_base = 'uh60a'
fn_sg = f'{fn_base}.sg'
fn_sg_ele = f'{fn_sg}.ele'
fn_msh = f'{fn_base}.msh'

names_e = [
    'e11', '2e12', '2e13', 'e22', '2e23', 'e33'
]

sg = sgio.read(fn_sg, 'vabs', sgdim=2, smdim=1)

_e, _s, _em, _sm = sgio.readOutput(fn_sg_ele, 'v', 'd')
sgio.addCellDictDataToMesh(names_e, _e, sg.mesh)

sgio.write(sg, fn_msh, 'gmsh22', mesh_only=True)

