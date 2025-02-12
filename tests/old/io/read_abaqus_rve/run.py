import sgio

# fn_base = 'rve_cube_test'
# fn_base = 'rve_udfrp'
# fn_base = 'rve_inclusion_meshsize01'
fn_base = 'rve_inclusion_cylinder_meshsize01'

fn_rve_abq_inp = f'../../files/{fn_base}.inp'
fn_sg = f'{fn_base}.sg'

sg = sgio.read(fn_rve_abq_inp, file_format='abaqus')
sg.sgdim = 3

print(sg)

sgio.write(sg, fn_sg, 'swiftcomp')
