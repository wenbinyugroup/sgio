import sgio

# fn_base = 'sg2_box_composite_section'
# fn_base = 'sg2_plydrop_composite_section'
# fn_base = 'sg2_airfoil_composite_section'
# fn_base = 'sg2_airfoil'
# fn_base = 'sg2_airfoil_2'
# fn_base = 'sg2_iso_airfoil'

# fn_in = f'../../../files/{fn_base}.inp'
# fn_out = f'{fn_base}.sg'
# ff_in = 'abaqus'
# ff_out = 'vabs'
# sgdim = 2
# model = 'BM2'  # Timoshenko model

exts = {
    'abaqus': 'inp',
    'vabs': 'sg',
    'swiftcomp': 'sg',
    'gmsh22': 'msh',
}

cases = [
    {
        'fn_base': 'sg2_airfoil',
        'ff_in': 'abaqus',
        'ff_out': 'vabs',
        'sgdim': 2,
        'model': 'BM2'
    },
    {
        'fn_base': 'sg2_airfoil',
        'ff_in': 'abaqus',
        'ff_out': 'gmsh22',
        'sgdim': 2,
        'model': 'BM2'
    },
    {
        'fn_base': 'sg2_airfoil_2',
        'ff_in': 'abaqus',
        'ff_out': 'vabs',
        'sgdim': 2,
        'model': 'BM2'
    },
    {
        'fn_base': 'sg2_airfoil_2',
        'ff_in': 'abaqus',
        'ff_out': 'gmsh22',
        'sgdim': 2,
        'model': 'BM2'
    },
]

_case = cases[3]
fn_in = f'../../../files/{_case["fn_base"]}.{exts[_case["ff_in"]]}'
fn_out = f'{_case["fn_base"]}.{exts[_case["ff_out"]]}'
sg = sgio.convert(
    file_name_in=fn_in,
    file_name_out=fn_out,
    file_format_in=_case['ff_in'],
    file_format_out=_case['ff_out'],
    sgdim=_case['sgdim'],
    model=_case['model']
)

print(sg)

# sg = sgio.read(fn_rve_abq_inp, file_format='abaqus')
# sg.sgdim = 2
# sg.smdim = 1
# sg.model = 1

# print(sg)
# # print(sg.mesh.get_cell_data('property_ref_csys', 'quad'))

# fn_sg = f'{fn_base}.sg'
# sgio.write(sg, fn_sg, 'vabs')

# fn_sg = f'{fn_base}.msh'
# sgio.write(sg, fn_sg, 'gmsh22', format_version='2.2')
