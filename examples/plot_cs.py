"""Example: Plot Cross-Section with Beam Properties

This example demonstrates how to:
1. Read a VABS cross-section input file
2. Read the corresponding VABS output (beam properties)
3. Visualize the cross-section with property overlay

The plot shows the cross-section geometry with beam properties like
neutral axis, shear center, and principal axes.
"""
import matplotlib.pyplot as plt
import sgio
from sgio import plot_sg_2d
from pathlib import Path

# Define file paths
files_dir = Path(__file__).parent / 'files'
input_file = files_dir / 'sg21eb_tri3_vabs40.sg'
output_file = files_dir / 'sg21eb_tri3_vabs40.sg.K'

# Check if files exist
if not input_file.exists():
    print(f"Error: Input file not found: {input_file}")
    print("Please ensure the file exists in the examples/files/ directory")
    exit(1)

if not output_file.exists():
    print(f"Warning: Output file not found: {output_file}")
    print("Plotting mesh only without beam properties overlay")
    model = None
else:
    # Read VABS output (beam properties)
    model = sgio.readOutputModel(str(output_file), 'vabs')

# Read VABS input (cross-section mesh)
cs = sgio.read(str(input_file), 'vabs')

# Create plot
print("=" * 60)
print("Plotting Cross-Section")
print("=" * 60)
print(f"Input file: {input_file.name}")
if model:
    print(f"Output file: {output_file.name}")
    print(f"Model type: {model.label}")
print("=" * 60)

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 8))

# Plot cross-section with beam properties overlay
plot_sg_2d(cs, model, ax)

# Add title and labels
ax.set_title('Cross-Section Visualization', fontsize=14, fontweight='bold')
ax.set_xlabel('x₂ (m)', fontsize=12)
ax.set_ylabel('x₃ (m)', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

# Display the plot
plt.tight_layout()
print("\nDisplaying plot... (close window to exit)")
plt.show()

print("=" * 60)
print("Plot closed.")
print("=" * 60)
