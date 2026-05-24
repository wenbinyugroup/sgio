import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)

cwd = Path(__file__).resolve().parent

sg = sgio.convert(
    str(cwd / 'sg33_cube.inp'),
    str(cwd / 'sg33_cube_sc21.sg'),
    'abaqus',
    'sc',
    sgdim=3,
    file_version_out='2.1',
    model_type='SD1',
)

print(sg)
