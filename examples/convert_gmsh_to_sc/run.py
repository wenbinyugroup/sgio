import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

main_msh = cwd / 'sg33_cube_tetra4_min_gmsh41.msh'
sections_json = cwd / 'sections.json'
config_json = cwd / 'config.json'
output_file = cwd / 'sg33_cube_tetra4_min_gmsh41.sg'

sg = sgio.read_sg_from_gmsh_bundle(
    main_msh=main_msh,
    sections_json=sections_json,
    config_json=config_json,
    model_type='SD1',
)

print(sg)

sgio.write(
    sg=sg,
    filename=str(output_file),
    file_format='sc',
    format_version='2.1',
    model_type='SD1',
)
