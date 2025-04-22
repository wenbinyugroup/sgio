import matplotlib.pyplot as plt

import sgio
from sgio.utils.plot import plot_sg_2d


# fn = 'files/vabs/version_4_0/sg21eb_tri3_vabs40.sg'
fn = 'files/vabs/version_4_0/sg21t_tri3_vabs40.sg'

cs = sgio.read(fn, 'vabs')
# print(cs)
model = sgio.readOutputModel(f'{fn}.k', 'vabs', sg=cs)
# print(model)

fig, ax = plt.subplots()
plot_sg_2d(cs, model, ax)
plt.show()
