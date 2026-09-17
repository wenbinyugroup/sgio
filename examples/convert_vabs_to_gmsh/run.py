"""Example: Export one VABS section as a Gmsh mesh with its SG manifest."""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

input_file = str(cwd / 'cs_box_t_vabs41.sg')

sg = sgio.read(
    input_file,
    file_format='vabs',
    format_version='4.1',
    model_type='BM2',
)
# Writes main.msh and the manifest main.sg.json that references it.
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

print(sg)
