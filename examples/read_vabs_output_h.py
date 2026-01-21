"""Example: Read VABS Homogenized Output (Beam Properties)

This example demonstrates how to read VABS homogenized output to obtain
the effective beam properties (stiffness matrix, mass matrix, etc.).

The example reads a VABS 4.1 output file (.K file) for a Timoshenko beam model.
"""
import sgio
from pathlib import Path

# Define the output file path
# Note: The .K file contains homogenized beam properties
output_file = Path(__file__).parent / 'files' / 'cs_box_t_vabs41.sg.K'

# Check if file exists
if not output_file.exists():
    print(f"Error: Output file not found: {output_file}")
    print("Please run VABS analysis first to generate the .K file")
    print("Or use a different example file from examples/files/")
    exit(1)

# Read the VABS homogenized output
# - file_format='vabs': Specifies VABS format
# - model_type='BM2': Timoshenko beam model (includes shear deformation)
model = sgio.readOutputModel(
    str(output_file),
    file_format='vabs',
    model_type='BM2'
)

# Extract beam properties using the .get() method
ea = model.get('ea')      # Axial stiffness
gj = model.get('gj')      # Torsional stiffness
ei22 = model.get('ei22')  # Bending stiffness about axis 2
ei33 = model.get('ei33')  # Bending stiffness about axis 3

# Display beam properties
print("=" * 60)
print("VABS Homogenized Beam Properties")
print("=" * 60)
print(f"File: {output_file.name}")
print(f"Model Type: {model.label}")
print(f"Model Name: {model.model_name}")
print("=" * 60)

print("\nStiffness Properties:")
print(f'  EA (Axial stiffness):      {ea:.6e}')
print(f'  GJ (Torsional stiffness):  {gj:.6e}')
print(f'  EI22 (Bending stiffness):  {ei22:.6e}')
print(f'  EI33 (Bending stiffness):  {ei33:.6e}')

# Display mass properties if available
mu = model.get('mu')
if mu is not None:
    print(f'\nMass Properties:')
    print(f'  μ (Mass per unit length):  {mu:.6e}')

print("=" * 60)
