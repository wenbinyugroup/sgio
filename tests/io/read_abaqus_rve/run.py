import sgio

fn_rve_abq_inp = '../../files/rve_cube_test.inp'


sg = sgio.read(fn_rve_abq_inp, file_format='abaqus')

print(sg)

fn_sg = 'rve_cube.sg'

sgio.write(sg, fn_sg, 'swiftcomp')
