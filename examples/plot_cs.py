import matplotlib.pyplot as plt
import sgio
from sgio import plot_sg_2d

fn = 'files/sg21eb_tri3_vabs40.sg'  # Your VABS input file name, relative path to this script or absolute path

cs = sgio.read(fn, 'vabs')  # Read VABS input
model = sgio.readOutputModel(f'{fn}.k', 'vabs', sg=cs)  # Read VABS output

fig, ax = plt.subplots()
plot_sg_2d(cs, model, ax)
plt.show()
