"""Example: Read VABS Dehomogenization Output (Local Stress/Strain)

This example demonstrates how to:
1. Read VABS input file (mesh)
2. Read VABS dehomogenization output (local stress/strain fields)
3. Add the stress/strain data to the mesh
4. Export to Gmsh format for visualization

The example uses VABS 4.1 output files for a box cross-section.
"""
import sgio
from pathlib import Path

# Define file paths
files_dir = Path(__file__).parent / 'files'
input_file = files_dir / 'cs_box_t_vabs41.sg'
output_file = files_dir / 'cs_box_t_vabs41_local.msh'

# Check if input file exists
if not input_file.exists():
    print(f"Error: Input file not found: {input_file}")
    print("Please ensure the file exists in the examples/files/ directory")
    exit(1)

print("=" * 60)
print("VABS Dehomogenization Output Processing")
print("=" * 60)

# [step1]
# Step 1: Read the mesh from VABS input file
print("\n[Step 1] Reading mesh from VABS input file...")
sg = sgio.read(
    filename=str(input_file),
    file_format='vabs',
)
print(f"  ✓ Loaded mesh with {len(sg.mesh.points)} nodes and {len(sg.mesh.cells)} elements")

# Step 2: Read the dehomogenization output state
# The .ELE file contains element-level stress/strain data
print("\n[Step 2] Reading dehomogenization output...")
state_cases = sgio.readOutputState(
    filename=str(input_file),
    file_format='vabs',
    analysis='d',          # 'd' for dehomogenization
    extension='ele',       # Element-level data
    sg=sg,
    tool_version='4.1'
)
print(f"  ✓ Loaded {len(state_cases)} load case(s)")

# [step2]
# Step 3: Extract stress data and add to mesh
print("\n[Step 3] Adding stress data to mesh...")
state_case = state_cases[0]  # Use first load case

# Get the stress tensor in material coordinates (esm)
# esm = element stress in material coordinates
stress_data = state_case.getState('esm').data

# Add the stress components to the mesh as cell data
sgio.addCellDictDataToMesh(
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
print(f"  ✓ Added stress components to mesh")

# [step3]
# Step 4: Write the mesh with stress data to Gmsh format
print("\n[Step 4] Writing mesh to Gmsh format...")
sgio.write(
    sg=sg,
    fn=str(output_file),
    file_format='gmsh',
)
print(f"  ✓ Saved to: {output_file}")
