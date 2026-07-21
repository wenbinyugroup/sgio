# Visualize SG Data

SGIO can render cross-section geometry, homogenized properties, and merged blade
meshes. Three backends are used, each suited to a different job.

| Backend | Use for | Dependency |
|---|---|---|
| matplotlib | Static figures for reports | required |
| plotly | Interactive HTML, large meshes | required |
| PyVista / VTK | 3D inspection, ParaView export | optional (`sgio[pyvista]`) |

## Plot a Single Cross-Section

{func}`sgio.plot_sg_2d` draws the mesh of a {class}`sgio.StructureGene`, and
{func}`sgio.plot_model_2d` draws the quantities carried by a homogenized model —
the mass center, shear center, and principal bending axes. They are separate
functions that compose by sharing one matplotlib axes:

```python
import matplotlib.pyplot as plt
import sgio

cs = sgio.read('cross_section.sg', 'vabs')
model = sgio.read_output_model('cross_section.sg.K', 'vabs', model_type='BM2')

fig, ax = plt.subplots(figsize=(10, 8))
sgio.plot_sg_2d(cs, ax)      # geometry
sgio.plot_model_2d(model, ax)  # property overlay
ax.set_aspect('equal')
fig.savefig('cross_section.png', dpi=300)
```

{func}`sgio.plot_sg_2d_plotly` and {func}`sgio.plot_model_2d_plotly` are the
interactive equivalents.

See {doc}`/examples/plot_cs`.

## Plot Multiple Cross-Sections Along a Span

Given a layout CSV of `(location, section)` pairs,
{func}`sgio.plot_sg_3d_beam` and {func}`sgio.plot_sg_3d_beam_plotly` place every
section at its spanwise station in one 3D view.

```python
import sgio

sgio.plot_sg_3d_beam_plotly(
    csv_file='blade.csv',
    section_dir='cs',
    input_format='vabs',
    model_type='BM2',
    aspect_mode='data',
    output_html='blade_3d.html',
)
```

See {doc}`/examples/plot_css_3d`.

## Plot Stiffness and Compliance Matrices

{func}`sgio.plot_matrix` renders a matrix as an annotated heatmap and
{func}`sgio.plot_matrix_bar3d` as a 3D bar chart, which makes the coupling
structure easier to read. Both take a raw matrix; `symlog=True` (the default)
applies symmetric-log scaling so entries of very different magnitude stay
legible.

```python
import matplotlib.pyplot as plt
import sgio

model = sgio.read_output_model('cross_section.sg.K', 'vabs', model_type='BM1')

fig, ax = plt.subplots(figsize=(8, 6))
sgio.plot_matrix(model.stff, fig=fig, ax=ax, annotate=True, symlog=True)
```

{func}`sgio.plot_model_matrix` is the convenience wrapper: it takes the model
object and selects the matrix by `kind` (`'stiffness'` or `'compliance'`),
labelling the rows and columns from the model's theory schema.

```python
sgio.plot_model_matrix(model, kind='stiffness')
```

## Merge Sections into One Mesh

To inspect a whole blade in an external viewer,
{func}`sgio.merge_sections_from_csv` translates each section to its spanwise
station and writes a single merged mesh.

```python
import sgio

sgio.merge_sections_from_csv(
    csv_file='blade.csv',
    section_dir='cs',
    input_format='vabs',
    output_file='blade_merged.msh',
    output_format='gmsh22',
)
```

See {doc}`/examples/merge_section_meshes`.

## Bridge to PyVista and ParaView

{class}`sgio.SGMesh` converts to and from PyVista, so any SG mesh — with its
`point_data` and `cell_data` — can be rendered by VTK or written to ParaView's
native formats.

```python
import sgio

sg = sgio.read('cross_section.sg', file_format='vabs', model_type='BM2')
grid = sg.mesh.to_pyvista()
grid.plot(scalars='property_id', show_edges=True, cpos='yz')
```

PyVista is optional and imported lazily; install it with
`pip install sgio[pyvista]`.

See {doc}`/examples/preview_sg_mesh` and {doc}`/examples/view_css_fi_paraview`.
