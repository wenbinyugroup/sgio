# Merge Section Layout Data

## Problem Description

Given a blade cross-section layout CSV and a directory of section files, merge all
cross-sections into one visualization mesh so the full blade can be inspected in Gmsh,
ParaView, or another mesh viewer.

## Explanation of the Solution

```{literalinclude} ../../../examples/plot_css/run.py
:language: python
```

`sgio.merge_sections_from_csv(...)` reads the `location` and `cs` columns from
`blade.csv`, resolves each section file under `cs/`, translates every section along the
spanwise direction, normalizes the data to a visualization mesh, remaps Gmsh geometrical
tags when needed, and writes a merged mesh file.

The default input format is `vabs` and the default output format is `gmsh22`. For the
current example data the section inputs are already Gmsh meshes, so the call is:

```python
sgio.merge_sections_from_csv(
    csv_file="blade.csv",
    section_dir="cs",
    input_format="gmsh",
    output_file="blade_merged.msh",
)
```

It can also read section inputs directly from other SG formats and convert them internally
before merging, for example:

```python
sgio.merge_sections_from_csv(
    csv_file="blade.csv",
    section_dir="sections",
    input_format="swiftcomp",
    model_type="bm1",
    output_file="blade_merged.msh",
)
```

## Result

A merged mesh file `blade_merged.msh` is created. Open it with:

```bash
gmsh blade_merged.msh
```

or inspect it in ParaView.

## File List

- [run.py](../../../examples/plot_css/run.py): Example script that calls the library API
- [blade.csv](../../../examples/plot_css/blade.csv): Blade cross-section layout file
