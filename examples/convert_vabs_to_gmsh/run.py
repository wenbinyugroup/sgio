"""Example: Convert VABS Mesh to Gmsh Format for Visualization

This example demonstrates how to convert a VABS cross-section file to
Gmsh format for visualization purposes.

The conversion extracts only the mesh data (nodes and elements) without
material properties, making it suitable for quick visualization.
"""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

input_file = str(cwd / 'cs_box_t_vabs41.sg')
output_file = str(cwd / 'cs_box_t_vabs41.msh')

# Convert VABS file to Gmsh format
# - mesh_only=True: Only convert mesh data (no materials)
# - model_type='BM2': Timoshenko beam model (required for VABS reading)
sg = sgio.convert(
    input_file,
    output_file,
    file_format_in='vabs',
    file_format_out='gmsh',
    model_type='BM2',
    mesh_only=True
)

print(sg)
