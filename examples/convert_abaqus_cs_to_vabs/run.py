import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

# There are two ways to call functions to convert the data.

# Method 1: Use the `convert` function to do this in one step.

sgio.convert(
    str(cwd / 'sg2_airfoil.inp'),  # Name of the Abaqus inp file.
    str(cwd / 'sg2_airfoil.sg'),  # Name of the VABS file.
    'abaqus', # Format of the CS data converted from.
    'vabs', # Format of the CS data converted to.
    sgdim=2, # Cross-section mesh lies in a 2D plane.
    model_type='bm2', # Structural model: Timoshenko.
)

# Visualize
sgio.convert(
    str(cwd / 'sg2_airfoil.sg'),  # Name of the Abaqus inp file.
    str(cwd / 'sg2_airfoil.msh'),  # Name of the VABS file.
    'vabs', # Format of the CS data converted from.
    'gmsh', # Format of the CS data converted to.
    model_type='bm2', # Structural model: Timoshenko.
)


# Method 2: Use the `read` and `write` functions to do this in two steps.

# sg = sgio.read(
#     'sg2_airfoil.inp',  # Name of the SG file.
#     'abaqus', # Format of the SG data. See doc for more info.
#     model='bm2', # Structural model: Timoshenko.
# )

# sgio.write(
#     sg,  # SG data
#     'sg2_airfoil.sg',  # Name of the SG file.
#     'vabs', # Format of the SG data. See doc for more info.
# )


