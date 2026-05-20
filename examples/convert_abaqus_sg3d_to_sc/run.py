import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

# sgio.convert(
#     'sg33_cube.inp',
#     'sg33_cube_sc21.sg',
#     'abaqus',
#     'sc',
#     model_type='sd1',
#     sgdim=3,
#     file_version_out='2.1',
#     use_sequential_node_ids=True,
#     use_sequential_element_ids=True,
# )

sg = sgio.read(
    str(cwd / 'sg33_cube.inp'),
    'abaqus',
    sgdim=3,
)

print(sg)
print(sg.mesh.point_data)

sgio.write(
    sg=sg,
    filename=str(cwd / 'sg33_cube_sc21.sg'),
    file_format='sc',
    format_version='2.1',
    model_type='sd1',
    # use_sequential_node_ids=True,
    # use_sequential_element_ids=True,
)
