# Visualize SG Data

SGIO can render cross-section geometry, homogenized properties, and merged blade
meshes. Three backends are used, each suited to a different job.

| Backend | Use for | Dependency |
|---|---|---|
| matplotlib | Static figures for reports | required |
| plotly | Interactive HTML, large meshes | required |
| PyVista / VTK | 3D inspection and ParaView export | optional (`pyvista` extra) |

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

## Inspect a Mesh with PyVista

{func}`sgio.create_pyvista_plotter` is the high-level scene factory for an
{class}`sgio.SGMesh`. It converts geometry and point/cell fields to a PyVista
grid and returns a `pyvista.Plotter`; the caller chooses whether to open a
desktop window, take a screenshot, or write HTML.

```python
import sgio

sg = sgio.read('cross_section.sg', file_format='vabs', model_type='BM2')
plotter = sgio.create_pyvista_plotter(
    sg.mesh,
    scalars='property_id',
    show_edges=True,
    show_local_axes=True,
)
plotter.show()
```

The local-axis overlay resolves the canonical per-element coordinate system:
`element_local_csys`, then `property_ref_csys`, then the compatibility axis
fields. It draws `y1`, `y2`, and `y3` as red, green, and blue arrows at sampled
cell centers. The factory does not need a GUI to construct a scene.

PyVista is optional and imported lazily; install it with:

```powershell
uv sync --extra pyvista
```

For browser HTML export, install the Trame-enabled extra and call
`plotter.export_html(...)`:

```powershell
uv sync --extra pyvista-html
```

The HTML viewer provides PyVista/VTK interaction, not Plotly's modebar or a
configurable CAD/CAE trackball toolbar.

## Export a Mesh for ParaView

`sgio.write` exports an {class}`sgio.SGMesh` or {class}`sgio.StructureGene` to
legacy `.vtk` or XML `.vtu` files:

```python
sgio.write('cross_section.vtu', sg, file_format='vtu')
```

This is a mesh-only exchange contract. It preserves points, cell topology,
`point_data`, and `cell_data`, but it does not serialize SG materials,
sections, orientations, or analysis configuration. It rejects non-empty
`cell_point_data`, `point_sets`, and `cell_sets` rather than silently losing
them. VTK/VTU input is not supported by `sgio.read` in this release.

`SGMesh.to_pyvista()` remains available for lower-level work. Its bridge keeps
geometry plus point/cell data, but deliberately drops point/cell sets and
element-nodal data because PyVista has no compatible representation.

See {doc}`/examples/preview_sg_mesh`, {doc}`/examples/plot_abaqus_local_csys`,
{doc}`/examples/export_sg_mesh_to_vtu`, and
{doc}`/examples/view_css_fi_paraview`.
