"""Example: Read VABS Homogenized Output (Beam Properties)

This example demonstrates how to read VABS homogenized output to obtain
the effective beam properties (stiffness matrix, mass matrix, etc.).

The example reads a VABS 4.1 output file (.K file) for a Timoshenko beam model.
"""
import sgio

# Define the output file path
# Note: The .K file contains homogenized beam properties
output_file = 'cs_box_t_vabs41.sg.K'

# Read the VABS homogenized output
# - file_format='vabs': Specifies VABS format
# - model_type='BM2': Timoshenko beam model (includes shear deformation)
model = sgio.read_output_model(
    str(output_file),
    file_format='vabs',
    model_type='BM2'
)

# Extract beam properties using the .get() method
ea = model.get('ea')      # Axial stiffness
gj = model.get('gj')      # Torsional stiffness
ei22 = model.get('ei22')  # Bending stiffness about axis 2
ei33 = model.get('ei33')  # Bending stiffness about axis 3
