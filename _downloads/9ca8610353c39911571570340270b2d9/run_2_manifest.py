"""Method 2: read the SG parameters from the SG manifest."""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

# sg2_airfoil.sg.json references sg2_airfoil.inp and holds the SG parameters,
# so the conversion takes no SG arguments. It writes the same VABS input as
# run_1_api.py.
sg = sgio.convert(
    str(cwd / 'sg2_airfoil.sg.json'),
    str(cwd / 'sg2_airfoil.sg'),
    'sg_manifest',
    'vabs',
)

# Export the converted section as a Gmsh mesh with its SG manifest, for
# visualization or downstream Gmsh-based workflows. A .msh file carries no
# materials or SG parameters, so a Gmsh export is always written this way.
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
)
plotter.off_screen = True
plotter.show(screenshot=str(cwd / "pyvista.png"), auto_close=False)
plotter.close()
