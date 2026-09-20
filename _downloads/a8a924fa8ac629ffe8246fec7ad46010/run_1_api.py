"""Method 1: pass the SG parameters as arguments of ``sgio.convert``."""
import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

# The Abaqus file states neither the SG dimension nor the model type.
sg = sgio.convert(
    str(cwd / 'sg33_cube.inp'),
    str(cwd / 'sg33_cube_sc21.sg'),
    'abaqus',
    'sc',
    sgdim=3,
    file_version_out='2.1',
    model_type='SD1',
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
)
plotter.off_screen = True
plotter.show(screenshot=str(cwd / "pyvista.png"), auto_close=False)
plotter.close()

print(sg)
