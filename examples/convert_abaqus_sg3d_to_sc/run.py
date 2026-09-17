import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent
output_file = cwd / 'sg33_cube_sc21.sg'

# Method 1: pass the SG parameters as arguments.
sg = sgio.convert(
    str(cwd / 'sg33_cube.inp'),
    str(output_file),
    'abaqus',
    'sc',
    sgdim=3,
    file_version_out='2.1',
    model_type='SD1',
)
api_output = output_file.read_text()

# Method 2: read the same SG parameters from the SG manifest, which references
# sg33_cube.inp.
sg = sgio.convert(
    str(cwd / 'sg33_cube.sg.json'),
    str(output_file),
    'sg_manifest',
    'sc',
    file_version_out='2.1',
)

# Both methods write the same SwiftComp input.
assert output_file.read_text() == api_output

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()

print(sg)
