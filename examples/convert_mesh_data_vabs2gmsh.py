import sgio

fn_in = 'files/cs_box_t_vabs41.sg'
fn_out = 'files/cs_box_t_vabs41.msh'

sg = sgio.convert(
    fn_in, fn_out, 'vabs', 'gmsh',
    model_type='BM2', mesh_only=True
)

print(sg)

