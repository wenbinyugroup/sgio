import sgio

model = sgio.readOutputModel(
    "sg21eb_tri3_vabs40.sg.k",
    "vabs",
    model_type="BM1"
)

print(model)
