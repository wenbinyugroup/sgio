import sgio

input_file = 'sg31t_hex20_sc21.sg'
output_file = 'sg31t_hex20_sc21.sg.sn'

# Read the SwiftComp input file
sg = sgio.read(
    filename=input_file,
    file_format='sc',
    sgdim=3,
    model_type='BM1',
)

# Read the SwiftComp output file
state_cases = sgio.read_output_state(
    filename=input_file,
    file_format='sc',
    analysis='d',
    tool_version='2.1',
    sg=sg,
    extension=['sn', 'snm'],
)

# Get the first and only one state case
state_case = state_cases[0]

# Add data to the mesh
sgio.add_cell_dict_data_to_mesh(
    dict_data=state_case.getState('s').data,
    name=['S11', 'S12', 'S13', 'S22', 'S23', 'S33'],
    mesh=sg.mesh
)

# Write the mesh to a gmsh file for visualization
sgio.write(
    sg=sg,
    filename=input_file.replace('.sg', '.msh'),
    file_format='gmsh',
)
