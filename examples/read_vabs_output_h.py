import sgio

model = sgio.readOutputModel(
    "files/cs_box_t_vabs41.sg.K",
    "vabs",
    model_type="BM2"
)

ea = model.get('ea')
gj = model.get('gj')
ei22 = model.get('ei22')
ei33 = model.get('ei33')

print(f'EA = {ea}')
print(f'GJ = {gj}')
print(f'EI22 = {ei22}')
print(f'EI33 = {ei33}')
