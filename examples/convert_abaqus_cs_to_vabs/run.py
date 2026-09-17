import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

sg = sgio.convert(
    str(cwd / 'sg2_airfoil.inp'),  # Name of the Abaqus inp file.
    str(cwd / 'sg2_airfoil.sg'),  # Name of the VABS file.
    'abaqus', # Format of the CS data converted from.
    'vabs', # Format of the CS data converted to.
    sgdim=2, # Cross-section mesh lies in a 2D plane.
    model_space='xy', # The mesh plane is x-y.
    model_type='bm2', # Structural model: Timoshenko.
)

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


