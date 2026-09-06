import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

main_msh = cwd / 'sg21_box_quad4_min_gmsh41.msh'
sections_json = cwd / 'sections.json'
config_json = cwd / 'config.json'
output_file = cwd / 'sg21_box_quad4_min_gmsh41.sg'

sg = sgio.read_sg_from_gmsh_bundle(
    main_msh=main_msh,
    sections_json=sections_json,
    config_json=config_json,
    model_type='BM1',
)

print(sg)

sgio.write(
    sg=sg,
    filename=str(output_file),
    file_format='vabs',
    model_type='BM1',
    model_space='yz',
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()
