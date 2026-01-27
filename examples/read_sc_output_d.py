import sgio
from pathlib import Path

# Define file paths
files_dir = Path(__file__).parent / 'files'
input_file = files_dir / 'sg31t_hex20_sc21.sg'
output_file = files_dir / 'sg31t_hex20_sc21.sg.sn'

# Check if input file exists
if not input_file.exists():
    print(f"Error: Input file not found: {input_file}")
    print("Please ensure the file exists in the examples/files/ directory")
    exit(1)

# Read the SwiftComp input file
sg = sgio.read(
    filename=str(input_file),
    file_format='sc',
    sgdim=3,
    model_type='BM1',
)

# Read the SwiftComp output file
state_cases = sgio.readOutputState(
    filename=str(input_file),
    file_format='sc',
    analysis='d',
    tool_version='2.1',
    sg=sg,
    extension=['sn', 'snm'],
)

# Get the first and only one state case
state_case = state_cases[0]

# Add data to the mesh
sgio.addCellDictDataToMesh(
    dict_data=state_case.getState('s').data,
    name=['S11', 'S12', 'S13', 'S22', 'S23', 'S33'],
    mesh=sg.mesh
)

# Write the mesh to a gmsh file for visualization
sgio.write(
    sg=sg,
    fn=str(input_file).replace('.sg', '.msh'),
    file_format='gmsh',
)
