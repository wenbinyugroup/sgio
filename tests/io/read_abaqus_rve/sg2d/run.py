import sgio

# fn_base = 'sg2_box_composite_section'
# fn_base = 'sg2_plydrop_composite_section'
# fn_base = 'sg2_airfoil_composite_section'
fn_base = 'sg2_airfoil'
# fn_base = 'sg2_airfoil_2'
# fn_base = 'sg2_iso_airfoil'

fn_rve_abq_inp = f'../../../files/{fn_base}.inp'
sg = sgio.read(fn_rve_abq_inp, file_format='abaqus')
sg.sgdim = 2
sg.smdim = 1
sg.model = 1

print(sg)
# print(sg.mesh.get_cell_data('property_ref_csys', 'quad'))

fn_sg = f'{fn_base}.sg'
sgio.write(sg, fn_sg, 'vabs')

fn_sg = f'{fn_base}.msh'
sgio.write(sg, fn_sg, 'gmsh22', format_version='2.2')
