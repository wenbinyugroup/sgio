from pathlib import Path
import matplotlib.pyplot as plt

import sgio
from sgio.utils.plot import plot_sg_2d


# Resolve path relative to this test file
test_dir = Path(__file__).parent
# fn = test_dir / 'files' / 'vabs' / 'version_4_0' / 'sg21eb_tri3_vabs40.sg'
fn = test_dir / 'files' / 'vabs' / 'version_4_0' / 'sg21t_tri3_vabs40.sg'

cs = sgio.read(str(fn), 'vabs')
# print(cs)
model = sgio.readOutputModel(f'{fn}.k', 'vabs', sg=cs)
# print(model)

fig, ax = plt.subplots()
plot_sg_2d(cs, model, ax)
plt.show()
