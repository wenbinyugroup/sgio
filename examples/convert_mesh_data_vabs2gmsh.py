"""Example: Convert VABS Mesh to Gmsh Format for Visualization

This example demonstrates how to convert a VABS cross-section file to
Gmsh format for visualization purposes.

The conversion extracts only the mesh data (nodes and elements) without
material properties, making it suitable for quick visualization.
"""
import sgio
from pathlib import Path

# Define file paths
files_dir = Path(__file__).parent / 'files'
input_file = files_dir / 'cs_box_t_vabs41.sg'
output_file = files_dir / 'cs_box_t_vabs41.msh'

# Check if input file exists
if not input_file.exists():
    print(f"Error: Input file not found: {input_file}")
    print("Please ensure the file exists in the examples/files/ directory")
    exit(1)

print("=" * 60)
print("Converting VABS Mesh to Gmsh Format")
print("=" * 60)
print(f"Input:  {input_file.name}")
print(f"Output: {output_file.name}")
print("=" * 60)

# Convert VABS file to Gmsh format
# - mesh_only=True: Only convert mesh data (no materials)
# - model_type='BM2': Timoshenko beam model (required for VABS reading)
sg = sgio.convert(
    str(input_file),
    str(output_file),
    file_format_in='vabs',
    file_format_out='gmsh',
    model_type='BM2',
    mesh_only=True
)

print("\n✓ Conversion complete!")
print(f"  Nodes: {len(sg.mesh.points)}")
print(f"  Elements: {len(sg.mesh.cells)}")
print("=" * 60)
print(f"\nYou can now visualize the mesh in Gmsh:")
print(f"  gmsh {output_file}")
print("\nOr use ParaView to view the geometry.")
print("=" * 60)

