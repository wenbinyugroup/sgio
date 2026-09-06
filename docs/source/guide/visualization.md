# Visualize SG Data

Three backends, each suited to a different job.

| Backend | Use for | Dependency |
|---|---|---|
| matplotlib | static figures for reports | required |
| plotly | interactive HTML, large meshes | required |
| PyVista / VTK | 3D inspection and ParaView export | optional (`pyvista` extra) |

## One Cross-Section

The single-SG entry points all take a {class}`sgio.StructureGene` and return
their backend's native object:

```python
import sgio

sg = sgio.read('cross_section.sg', file_format='vabs', model_type='BM2')

axes = sgio.plot_sg_matplotlib(sg)                    # matplotlib axes
figure = sgio.plot_sg_plotly(sg, output_html='cs.html')  # plotly figure
plotter = sgio.plot_sg_pyvista(sg)                    # pyvista plotter
```

matplotlib and Plotly render the section's `(x2, x3)` plane; PyVista renders
the mesh in its stored 3D coordinates.

Geometry and homogenized properties are drawn by separate functions that
compose on one axes — {func}`sgio.plot_sg_2d` for the mesh,
{func}`sgio.plot_model_2d` for the mass center, shear center, and principal
bending axes:

```python
fig, ax = plt.subplots(figsize=(10, 8))
sgio.plot_sg_2d(cs, ax)
sgio.plot_model_2d(model, ax)
ax.set_aspect('equal')
```

{func}`sgio.plot_sg_2d_plotly` and {func}`sgio.plot_model_2d_plotly` are the
interactive equivalents. See {doc}`/examples/plot_cs`.

## Many Sections Along a Span

Given a layout CSV of `(location, section)` pairs,
{func}`sgio.plot_sg_3d_beam` and {func}`sgio.plot_sg_3d_beam_plotly` place
every section at its spanwise station in one 3D view.
{func}`sgio.merge_sections_from_csv` instead writes a single merged mesh for an
external viewer.

See {doc}`/examples/plot_css_3d` and {doc}`/examples/merge_section_meshes`.

## Stiffness and Compliance Matrices

{func}`sgio.plot_matrix` renders a matrix as an annotated heatmap,
{func}`sgio.plot_matrix_bar3d` as a 3D bar chart. Both take a raw matrix;
`symlog=True` (default) keeps entries of very different magnitude legible.

{func}`sgio.plot_model_matrix` is the convenience wrapper — it takes the model
and selects the matrix by `kind`, labelling rows and columns from the model's
theory schema:

```python
sgio.plot_model_matrix(model, kind='stiffness')
```

## PyVista Inspection

{func}`sgio.plot_sg_pyvista` converts an SG's mesh and point/cell fields to a
PyVista grid and returns a `pyvista.Plotter`; the caller decides whether to
open a window, screenshot, or export HTML. Cells are colored by
`property_id` by default, with a discrete property legend.

```python
plotter = sgio.plot_sg_pyvista(
    sg, scalars='property_id', show_edges=True, show_local_axes=True,
)
plotter.show()
```

`widgets=True` adds desktop checkboxes for local axes, faces, edges, and nodes.
They use Python callbacks and are therefore unavailable with `output_html`.

The local-axis overlay resolves the per-element coordinate system in the order
given in {doc}`/ref/sg_on_gmsh`, drawing `y1`, `y2`, `y3` as red, green, and
blue arrows at sampled cell centers.

For a persisted local-axis scene, write a VTM with
{func}`sgio.create_pyvista_local_axis_multiblock`, then render it with
{func}`sgio.plot_pyvista_local_axes`. The VTM keeps glyphs for all cells;
`max_local_axes` limits only what is rendered.

Install the optional dependency with `uv sync --extra pyvista`, or
`uv sync --extra pyvista-html` for browser export via
`plotter.export_html(...)`.

## ParaView Export

{func}`sgio.write` exports an SG to legacy `.vtk` or XML `.vtu`:

```python
sgio.write(sg, 'cross_section.vtu', file_format='vtu')
```

This is a mesh-only exchange contract: points, cell topology, `point_data`, and
`cell_data` are preserved; materials, sections, orientations, and analysis
configuration are not. Non-empty `cell_point_data`, `point_sets`, and
`cell_sets` are rejected rather than silently dropped. VTK/VTU input is not
supported by {func}`sgio.read`.

`SGMesh.to_pyvista()` remains available for lower-level work; it keeps geometry
plus point/cell data but drops point/cell sets and element-nodal data, which
PyVista cannot represent.

See {doc}`/examples/preview_sg_mesh`,
{doc}`/examples/plot_abaqus_local_csys`,
{doc}`/examples/export_sg_mesh_to_vtu`, and
{doc}`/examples/view_css_fi_paraview`.
