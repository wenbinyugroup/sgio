"""Example: Read VABS Dehomogenization Output (Local Stress/Strain)

This example demonstrates how to:
1. Read VABS input file (mesh)
2. Read VABS dehomogenization output (local stress/strain fields)
3. Add the stress/strain data to the mesh
4. Export to Gmsh format for visualization

The example uses VABS 4.1 output files for a box cross-section.
"""
import sgio

# Define file paths
input_file = 'cs_box_t_vabs41.sg'
output_file = 'cs_box_t_vabs41_local.msh'

# [step1]
# Read the mesh from VABS input file
sg = sgio.read(
    filename=input_file,
    file_format='vabs',
)

state_cases = sgio.read_output_state(
    filename=input_file,
    file_format='vabs',
    analysis='d',          # 'd' for dehomogenization
    extension='ele',       # Element-level data
    sg=sg,
    tool_version='4.1'
)

# [step2]
# Extract stress data and add to mesh
state_case = state_cases[0]  # Use first load case

# Get the stress tensor in material coordinates (esm)
# esm = element stress in material coordinates
stress_data = state_case.getState('esm').data

# Add the stress components to the mesh as cell data
sgio.add_cell_dict_data_to_mesh(
    dict_data=stress_data,
    name=[
        'S11 (M)',  # Normal stress in direction 1
        'S12 (M)',  # Shear stress in 1-2 plane
        'S13 (M)',  # Shear stress in 1-3 plane
        'S22 (M)',  # Normal stress in direction 2
        'S23 (M)',  # Shear stress in 2-3 plane
        'S33 (M)'   # Normal stress in direction 3
    ],
    mesh=sg.mesh
)

# [step3]
# Write the mesh with stress data to Gmsh format
sgio.write(
    sg=sg,
    filename=str(output_file),
    file_format='gmsh',
)
