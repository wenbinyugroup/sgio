import json
import sgio

fn = 'files/sg33_cube_tetra4_min_gmsh41.msh'
materials_file = 'files/materials.json'

sg = sgio.read(
    fn,
    'gmsh',
    # model_type='SD1',
    # sgdim=3,
)

sg.materials = sgio.read_materials_from_json(materials_file)
# print(sg.materials)

# with open(materials_file, 'r') as f:
#     materials = json.load(f)

# for m in materials_data['materials']:
#     mat = sgio.CauchyContinuumModel(**m)
#     # Use material name as key instead of numeric ID
#     mat_name = mat.name if mat.name else f"Material_{m['id']}"
#     sg.materials[mat_name] = mat


print(sg)
# print(sg.mesh.cell_data['gmsh:physical'])



# for i, a in enumerate(sg.mesh.cell_data['property_id']):
#     sg.mesh.cell_data['property_id'][i] = a.astype(int)

sgio.write(
    sg=sg,
    fn=fn.replace('.msh', '.sg'),
    file_format='sc',
    format_version='2.1',
    model_type='sd1',
)
