import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

# The SG manifest references laminate_simple.msh and adds what the mesh cannot
# carry: sgdim, model type, model space, materials and sections.
manifest = cwd / 'laminate_simple.sg.json'
output_file = cwd / 'laminate_simple.sg'

sg = sgio.read(str(manifest), 'sg_manifest')

print(sg)

# The manifest declares model_space='xy', so the writer projects:
#   gmsh x -> VABS x2
#   gmsh y -> VABS x3
# and picks ``additional_rotation_2`` from the mesh cell data as the per-layer
# VABS ``theta_3`` (fiber angle).
sgio.write(sg=sg, filename=str(output_file), file_format='vabs')

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
)
plotter.off_screen = True
plotter.show(screenshot=str(cwd / "pyvista.png"), auto_close=False)
plotter.close()
