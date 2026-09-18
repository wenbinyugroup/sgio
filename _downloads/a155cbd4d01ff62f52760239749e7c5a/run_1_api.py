"""Method 1: pass the SG parameters as arguments of ``sgio.convert``."""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

# The Abaqus file holds the mesh, materials and sections, but not the SG
# parameters, so they are given as arguments.
sg = sgio.convert(
    str(cwd / 'sg2_airfoil.inp'),  # Name of the Abaqus inp file.
    str(cwd / 'sg2_airfoil.sg'),  # Name of the VABS file.
    'abaqus', # Format of the CS data converted from.
    'vabs', # Format of the CS data converted to.
    sgdim=2, # Cross-section mesh lies in a 2D plane.
    model_space='xy', # The mesh plane is x-y.
    model_type='BM2', # Structural model: Timoshenko.
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()
