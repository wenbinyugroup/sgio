import sgio

fn = 'sg33_cube_tetra4_min_gmsh41.msh'

sg = sgio.read(fn, 'gmsh')

sg.materials = sgio.read_materials_from_json('materials.json')

print(sg)

sgio.write(
    sg=sg,
    filename=fn.replace('.msh', '.sg'),
    file_format='sc',
    format_version='2.1',
    model_type='sd1',
)
