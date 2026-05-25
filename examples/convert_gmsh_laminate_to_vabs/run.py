import logging
from pathlib import Path

import sgio

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

main_msh = cwd / 'laminate_simple.msh'
sections_json = cwd / 'sections.json'
config_json = cwd / 'config.json'
output_file = cwd / 'laminate_simple.sg'

sg = sgio.read_sg_from_gmsh_bundle(
    main_msh=main_msh,
    sections_json=sections_json,
    config_json=config_json,
    model_type='BM1',
)

print(sg)

# Gmsh section lives in the xy plane, so the writer projects:
#   gmsh x -> VABS x2
#   gmsh y -> VABS x3
# With model_space='xy', the writer also picks ``additional_rotation_2`` from
# the mesh cell data as the per-layer VABS ``theta_3`` (fiber angle).
sgio.write(
    sg=sg,
    filename=str(output_file),
    file_format='vabs',
    model_type='BM1',
    model_space='xy',
)
