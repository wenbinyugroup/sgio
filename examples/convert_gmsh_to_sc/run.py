import logging
from pathlib import Path

import sgio
from sgio.iofunc.common.material_json import read_materials_from_json

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

fn = str(cwd / 'sg33_cube_tetra4_min_gmsh41.msh')

sg = sgio.read(fn, 'gmsh')

sg.materials = read_materials_from_json(str(cwd / 'materials.json'))

print(sg)

sgio.write(
    sg=sg,
    filename=fn.replace('.msh', '.sg'),
    file_format='sc',
    format_version='2.1',
    model_type='sd1',
)
