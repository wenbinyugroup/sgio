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

input_file = 'sg21eb_tri3_vabs40.sg'
output_file = 'sg21eb_tri3_vabs40.sg.K'

# Read VABS output (beam properties)
model = sgio.read_output_model(output_file, 'vabs', model_type='BM1')

# Read VABS input (cross-section mesh)
cs = sgio.read(input_file, 'vabs')

# Create plot

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 8))

# Plot cross-section with beam properties overlay
plot_sg_2d(cs, model, ax)

# Add labels
ax.set_xlabel(r'$x_2$ (m)', fontsize=12)
ax.set_ylabel(r'$x_3$ (m)', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

# Display the plot
plt.tight_layout()
print("\nDisplaying plot... (close window to exit)")
plt.show()
