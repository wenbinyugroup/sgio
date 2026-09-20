"""Method 2: read the SG parameters from the SG manifest."""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

# sg33_cube.sg.json references sg33_cube.inp and holds sgdim and model_type,
# so the conversion takes no SG arguments. It writes the same SwiftComp input
# as run_1_api.py.
sg = sgio.convert(
    str(cwd / 'sg33_cube.sg.json'),
    str(cwd / 'sg33_cube_sc21.sg'),
    'sg_manifest',
    'sc',
    file_version_out='2.1',
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
)
plotter.off_screen = True
plotter.show(screenshot=str(cwd / "pyvista.png"), auto_close=False)
plotter.close()

print(sg)
