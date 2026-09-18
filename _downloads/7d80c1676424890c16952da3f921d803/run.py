"""Preview a Structure Gene mesh with pyvista.

Reads a VABS cross-section, bridges its ``SGMesh`` to a ``pyvista`` grid
(:meth:`SGMesh.to_pyvista`), renders a preview image, and demonstrates the
reverse bridge (:meth:`SGMesh.from_pyvista`).

pyvista is an optional dependency::

    pip install sgio[pyvista]     # or: uv pip install pyvista
"""
import logging
from pathlib import Path

import sgio
from sgio.core.mesh import SGMesh

logging.basicConfig(level=logging.INFO)
cwd = Path(__file__).resolve().parent

# 1. Read a Structure Gene (2D triangular cross-section mesh).
sg = sgio.read(
    str(cwd / "sg21t_tri3.sg"),
    file_format="vabs",
    format_version="4",
    sgdim=2,
    model_type="BM2",
)

plotter = sgio.plot_sg_pyvista(
    sg,
    show_local_axes=True,
    output_html=cwd / "pyvista.html",
)
plotter.close()

# 2. Bridge the SG mesh to a pyvista UnstructuredGrid.
grid = sg.mesh.to_pyvista()
print(grid)

# 3. Preview. ``off_screen`` + ``screenshot`` make the example run headless;
#    drop both arguments for an interactive window (grid.plot(...)).
# The 2D cross-section lives in the Y-Z plane, so look down the X axis.
grid.plot(
    scalars="property_id",
    show_edges=True,
    cpos="yz",
    off_screen=True,
    screenshot=str(cwd / "preview.png"),
)
print(f"Saved preview to {cwd / 'preview.png'}")

# 4. Reverse bridge: pyvista grid back to an SGMesh.
mesh_back = SGMesh.from_pyvista(grid)
print("Round-trip cell blocks:", [(cb.type, len(cb)) for cb in mesh_back.cells])
