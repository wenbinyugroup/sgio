import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent
output_file = cwd / 'sg2_airfoil.sg'

# Method 1: pass the SG parameters as arguments.
sg = sgio.convert(
    str(cwd / 'sg2_airfoil.inp'),  # Name of the Abaqus inp file.
    str(output_file),  # Name of the VABS file.
    'abaqus', # Format of the CS data converted from.
    'vabs', # Format of the CS data converted to.
    sgdim=2, # Cross-section mesh lies in a 2D plane.
    model_space='xy', # The mesh plane is x-y.
    model_type='BM2', # Structural model: Timoshenko.
)
api_output = output_file.read_text()

# Method 2: read the same SG parameters from the SG manifest, which references
# sg2_airfoil.inp.
sg = sgio.convert(
    str(cwd / 'sg2_airfoil.sg.json'),
    str(output_file),
    'sg_manifest',
    'vabs',
)

# Both methods write the same VABS input.
assert output_file.read_text() == api_output

# Export the converted section as a Gmsh mesh with its SG manifest, for
# visualization or downstream Gmsh-based workflows.
sgio.write(
    sg=sg,
    filename=str(cwd / 'main.sg.json'),
    file_format='sg_manifest',
    format_version='4.1',
    model_file='main.msh',
    model_file_format='gmsh',
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()
