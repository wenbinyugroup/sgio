# [step1]
import sgio

# Read the mesh
sg = sgio.read(
    filename="files/cs_box_t_vabs41.sg",
    file_format='vabs',
)

# Read the output state
state_cases = sgio.readOutputState(
    filename="files/cs_box_t_vabs41.sg",
    file_format='vabs',
    analysis='d',
    extension='ele',
    sg=sg,
    tool_version='4.1'
)

# [step2]
state_case = state_cases[0]
# Add the local state to the mesh
sgio.addCellDictDataToMesh(
    dict_data=state_case.getState('esm').data,
    name=[
        'S11 (M)', 'S12 (M)', 'S13 (M)',
        'S22 (M)', 'S23 (M)', 'S33 (M)'
    ],
    mesh=sg.mesh
)

# [step3]
# Write the mesh to a gmsh file
sgio.write(
    sg=sg,
    fn="files/cs_box_t_vabs41_local.msh",
    file_format='gmsh',
)
