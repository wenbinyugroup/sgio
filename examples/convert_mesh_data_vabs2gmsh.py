import sgio

fn_in = 'files/box.sg'
fn_out = 'files/box.msh'

sg = sgio.convert(
    fn_in, fn_out, 'vabs', 'gmsh',
    sgdim=2, model_type='BM2', mesh_only=True
)

print(sg)

