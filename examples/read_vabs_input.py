"""Example: Read VABS Input File

This example demonstrates how to read a VABS input file and inspect
the structure gene data.

The example reads a VABS 4.0 format file for an Euler-Bernoulli beam
cross-section model.
"""
import sgio
from pathlib import Path

# Define the input file path
input_file = Path(__file__).parent / 'files' / 'sg21eb_tri3_vabs40.sg'

# Check if file exists
if not input_file.exists():
    print(f"Error: Input file not found: {input_file}")
    print("Please ensure the file exists in the examples/files/ directory")
    exit(1)

# Read the VABS input file
# - file_format='vabs': Specifies VABS format
# - model_type='BM1': Euler-Bernoulli beam model (classical beam theory)
sg = sgio.read(
    str(input_file),
    file_format='vabs',
    model_type='BM1'
)

# Display basic information about the structure gene
print("=" * 60)
print("VABS Input File Information")
print("=" * 60)
print(f"File: {input_file.name}")
print(f"Model Type: {sg.model.label if sg.model else 'Not specified'}")
print(f"Number of nodes: {len(sg.mesh.points)}")
print(f"Number of elements: {len(sg.mesh.cells)}")
print(f"Number of materials: {len(sg.materials) if sg.materials else 0}")
print("=" * 60)

# Display the full structure gene object
print("\nFull Structure Gene Object:")
print(sg)

