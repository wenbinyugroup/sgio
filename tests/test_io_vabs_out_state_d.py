import logging
import sgio

logger = logging.getLogger('sgio')
sgio.configure_logging(cout_level='debug')


# Base name of the VABS files
fn_base = 'files/vabs/version_4_1/uh60a'
model_type = 'bm2'  # bm1: Euler-Bernoulli beam, bm2: Timoshenko beam



ver = '4.1'  # VABS version
fn_sg = f'{fn_base}.sg'
fn_sg_ele = f'{fn_sg}.ele'
fn_msh = f'{fn_base}.msh'

# Component labels in visualization
# name_u = ['u1', 'u2', 'u3']
name_e = ['e11', '2e12', '2e13', 'e22', '2e23', 'e33']  # Strain in global coordinate
name_em = ['e11m', '2e12m', '2e13m', 'e22m', '2e23m', 'e33m']  # Strain in material coordinate
name_s = ['s11', '2s12', '2s13', 's22', '2s23', 's33']  # Stress in global coordinate
name_sm = ['s11m', 's12m', 's13m', 's22m', 's23m', 's33m']  # Stress in material coordinate

# Read the cross-section model
sg = sgio.read(fn_sg, 'vabs', sgdim=2, model_type=model_type)
# print(sg)

# Read the output state
state_case = sgio.readOutputState(fn_sg, 'v', 'd', sg=sg, tool_version=ver)
# print(state_case)


# Add data to the mesh
# sgio.addPointDictDataToMesh(name_u, state_case.getState('u').data, sg.mesh)
# Element strain in global coordinate
sgio.addCellDictDataToMesh(name_e, state_case.getState('ee').data, sg.mesh)
# Element strain in material coordinate
sgio.addCellDictDataToMesh(name_em, state_case.getState('eem').data, sg.mesh)
# Element stress in global coordinate
sgio.addCellDictDataToMesh(name_s, state_case.getState('es').data, sg.mesh)
# Element stress in material coordinate
sgio.addCellDictDataToMesh(name_sm, state_case.getState('esm').data, sg.mesh)


# Write the mesh to a file
sgio.write(sg, fn_msh, 'gmsh', format_version='4.1', mesh_only=True)

