"""Example: Export one VABS section as a SG-on-Gmsh bundle."""
import logging
import sys
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent
sys.path.insert(0, str(cwd.parent))

from _bundle_helpers import write_gmsh_bundle_sidecars

input_file = str(cwd / 'cs_box_t_vabs41.sg')
main_msh = cwd / 'main.msh'

sg = sgio.read(
    input_file,
    file_format='vabs',
    format_version='4.1',
    model_type='BM2',
)
sgio.write(
    sg=sg,
    filename=str(main_msh),
    file_format='gmsh',
    format_version='4.1',
    model_type='BM2',
    binary=False,
)
write_gmsh_bundle_sidecars(sg, cwd)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()

print(sg)
