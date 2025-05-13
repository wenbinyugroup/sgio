import sgio

fn = '../files/sg23_tri6_sc21.sg.k'

model = sgio.readOutput(fn, 'sc', smdim=3)
print(model)
