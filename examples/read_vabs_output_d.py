# [step1]
import sgio

# Read the mesh
sg = sgio.read(
    fn="files/cs_box_t_vabs41.sg",
    file_format='vabs',
    model_type='bm2'
)

# Read the output state
state_case = sgio.readOutputState(
    fn="files/cs_box_t_vabs41.sg",
    file_format='vabs',
    analysis='d',
    model_type='bm2',
    ext='ele',
    sg=sg,
    tool_ver='4.1'
)

# [step2]
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
    mesh_only=True
)
