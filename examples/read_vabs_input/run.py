"""Example: Read VABS Input File

This example demonstrates how to read a VABS input file and inspect
the structure gene data.

The example reads a VABS 4.0 format file for an Euler-Bernoulli beam
cross-section model.
"""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

# Define the input file path
input_file = str(cwd / 'sg21eb_tri3_vabs40.sg')

# Read the VABS input file
# - file_format='vabs': Specifies VABS format
# - model_type='BM1': Euler-Bernoulli beam model (classical beam theory)
sg = sgio.read(
    input_file,
    file_format='vabs',
    model_type='BM1'
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()

print(sg)

