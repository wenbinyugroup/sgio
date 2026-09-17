import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

manifest = cwd / 'sg21_box_quad4_min_gmsh41.sg.json'
output_file = cwd / 'sg21_box_quad4_min_gmsh41.sg'

# The SG manifest references sg21_box_quad4_min_gmsh41.msh and carries the SG parameters,
# materials and sections the mesh cannot hold.
sg = sgio.read(str(manifest), 'sg_manifest')

print(sg)

sgio.write(
    sg=sg,
    filename=str(output_file),
    file_format='vabs',
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()
