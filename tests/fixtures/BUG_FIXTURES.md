# Bug-reproduction fixtures

Minimal inputs that each trigger exactly one known defect. Regenerate them all
with:

```
uv run python tests/fixtures/make_bug_fixtures.py
```

(The generator needs the `gmsh` Python package for the mesh fixtures; the
Abaqus deck is emitted verbatim from constants and needs nothing.)

Every mesh here is a handful of elements on a unit cube or square. These
exercise parser/writer paths, not numerics, so the design goal is that a
failing assertion points at one line of code — not that the geometry is
interesting. Where an older, large fixture covers the same defect it is noted
below; the small one is a drop-in replacement.

Status column is against **sgio 0.8.0 as published**. Six entries differ in
this working tree, which is called out per row.

| Fixture | Defect | Status |
|---|---|---|
| `gmsh/sg33_cube_boundary_group_bug_min_gmsh41.msh` | lower-dim physical group counted as SG elements | fixed in tree |
| `gmsh/sg22_square_boundary_group_bug_min_gmsh41.msh` | same, in 2D | fixed in tree |
| `gmsh/sg33_cube_tetra4_min_gmsh40.msh` | MSH 4.0 sent to the 4.1 reader | fixed in tree |
| `gmsh/sg33_cube_tetra4_min_gmsh22.msh` | MSH 2.2 read path returns meshio `Mesh`, writer needs `SGMesh` | fixed in tree |
| `gmsh/sections_thermoelastic_cte_bug.json` + `config_thermoelastic.json` | CTE vector written at 6 components for every isotropy | fixed in tree |
| `abaqus/sg33_cube_distribution_input_bug.inp` + `.ori` | `*Distribution ... Input=<file>` never followed | fixed in tree |

---

## `sg33_cube_boundary_group_bug_min_gmsh41.msh` (3 KB)

Unit cube, 14 nodes. Two physical groups: `matrix` (dim 3, 24 tetrahedra) and
`boundary` (dim 2, 24 triangles).

```python
sg = sgio.read(fixture, "gmsh", sgdim=3, model_type="SD1")
```

| | expected | 0.8.0 |
|---|---|---|
| `sg.nelems` | 24 | **48** |
| `list(sg.materials)` | `['matrix']` | `['matrix', 'Material_2']` |

The surface elements were counted as SG elements and given a placeholder
material. Replaced `sg33_spheres_boundary_group_bug.msh` (941 KB, since
deleted), where the same defect showed as `nelem` 25211 instead of 21963.

Fixed in this working tree: `mesh_to_sg` now keeps only the cell blocks whose
physical group resolves to a declared section, so `boundary` is dropped
instead of counted. Reading a bare `.msh` with no section data now raises
`IncompleteModelDataError` rather than fabricating a placeholder material —
so the snippet above must be called via
`sgio.read_sg_from_gmsh_bundle(fixture, sections_json=..., model_type="SD1")`
to get `sg.nelems == 24`.

The companion `sg22_square_boundary_group_bug_min_gmsh41.msh` (927 bytes) is
the same situation one dimension down — `matrix` (dim 2, 4 triangles) plus
`boundary` (dim 1, 4 lines), read with `sgdim=2, model_type="PL1"`, giving
`nelem` 8 instead of 4. It is here to keep a fix from being written as a 3D
special case.

**Do not fix this by filtering on `dim == sgdim`.** Element dimension may
legitimately differ from SG dimension — 1D beam elements in a 3D strut lattice
are real SG elements. The criterion is whether the element's physical name
resolves to a section.

## `sg33_cube_tetra4_min_gmsh40.msh` / `..._gmsh22.msh` (2.8 KB / 822 B)

Both are `sg33_cube_tetra4_min_gmsh41.msh` re-emitted by Gmsh in another
format version, so all three must read back as **8 nodes, 6 tetrahedra,
material `matrix`**. Asserting that across the trio is the test: a
version-dispatch defect shows up as a mismatch, with no separately maintained
expectations to drift.

MSH 4.0 writes itself as `4` in `$MeshFormat`, and its point entities carry a
6-double bounding box where 4.1 carries 3 coordinates. Sending a 4.0 file to
the 4.1 reader desynchronises on the first point entity. Published 0.8.0 fails
here with `ReadError: parametric nodes not implemented` — the desync happens to
surface in `$Nodes` for a file this small, whereas the 3 MB
`sg33_tpms_entities_parse_bug.msh` surfaces it in `$Entities` as
`ValueError: string or file could not be read to its end`. Same cause, and the
small file is a drop-in replacement for that fixture.

The generator sets `Mesh.SaveParametric = 0`. Without it Gmsh stores parametric
coordinates for OCC-backed entities, which meshio's 4.0 reader rejects
outright — a *different* failure that would mask the one under test.

The 2.2 file additionally reproduces the write-side defect:

```python
sg = sgio.read(fixture, "gmsh", sgdim=3, model_type="SD1", format_version="2.2")
type(sg.mesh)           # meshio._mesh.Mesh  -- 4.1 gives sgio.core.mesh.SGMesh
sgio.write(sg=sg, filename="out.sg", file_format="sc",
           format_version="2.1", model_type="SD1")
# AttributeError: 'Mesh' object has no attribute 'cell_point_data'
```

The two read paths disagreed on the mesh type they return, and 0.8's SwiftComp
writer requires the `SGMesh` one. Fixed in this working tree: the 2.2 reader
now wraps meshio's parsed mesh in `SGMesh.from_meshio` and runs the same
`finalize_sg_cell_data` post-processing the 4.0/4.1 readers already did, so
all three format versions of the trio yield the same mesh IR
(`tests/unit/test_gmsh_parser.py::test_gmsh_versions_read_into_the_same_mesh_ir`).

## `sections_thermoelastic_cte_bug.json` + `config_thermoelastic.json`

Use with `sg33_cube_two_materials_min_gmsh41.msh` (23 nodes, `matrix` and
`fibre` at 24 tetrahedra each), which exists so one write covers an isotropic
and an orthotropic material at once:

```python
sg = sgio.read_sg_from_gmsh_bundle(
    main_msh=".../sg33_cube_two_materials_min_gmsh41.msh",
    sections_json=".../sections_thermoelastic_cte_bug.json",
    config_json=".../config_thermoelastic.json",
    model_type="SD1")
sgio.write(sg=sg, filename="out.sg", file_format="sc",
           format_version="2.1", model_type="SD1")
```

`config_thermoelastic.json` sets `physics: 1` so the writer emits the thermal
record at all. Both materials then get **7 numbers** on that line:

```
       1       0       1  # material id, anisotropy, ntemp
  0.000000000000e+00  1.200000000000e+03
  3.500000000000e+09  3.500000000000e-01
  5.8e-05  5.8e-05  5.8e-05  0.0  0.0  0.0  1.1e+03     <- want 2: 5.8e-05  1.1e+03

       2       1       1  # material id, anisotropy, ntemp
  ...
 -5.0e-07  1.0e-05  1.0e-05  0.0  0.0  0.0  7.5e+02     <- want 4: -5e-07 1e-05 1e-05 7.5e+02
```

SwiftComp's thermal record is isotropy-dependent — 1 CTE + specific heat for
isotropic, 3 + specific heat for orthotropic, 6 + specific heat for
anisotropic — and so is sgio's own `read_thermal_property`. The writer had no
matching branch, so the specific heat was read out of the wrong column: 1100
became 5.8e-05 and 750 became 0.

**This one was silent.** SwiftComp reports success and the stiffness and CTE
results stay correct; only the effective-specific-heat block was wrong. A test
that only checks "no exception" would not have caught it.

Fixed in this working tree: `_write_material` (in `material_writers.py`) now
truncates `cte` through `_project_cte` before appending `specific_heat`, using
the same isotropy -> length table (`CTE_LEN_BY_ISOTROPY`, now shared with
`material_readers.py` instead of duplicated) `read_thermal_property` already
used to parse it back. `_project_cte` raises rather than silently discarding
if the components being dropped are not actually redundant (nonzero shear, or
unequal normal components under isotropy=0) — truncating those would just
trade one silent wrong value for another.

Fixing the writer surfaced a second, independent bug on the read side:
`read_material` did `mp.cte = cte` with the isotropy-truncated 1/3-length
list, which `CauchyContinuumModel`'s `validate_assignment` rejects since `cte`
is a fixed 6-component field — so reading back *any* SwiftComp file with
`physics=1` and isotropy 0 or 1 raised a `ValidationError`, independent of
whether the writer was fixed. `read_thermal_property` now pads back to 6
components the same way an isotropic/orthotropic material's Voigt CTE always
looks (repeated value for isotropic, zero shear for isotropic/orthotropic),
so sgio's internal representation stays fixed-length end to end and
write -> read is lossless. The VABS thermal branch (`physics == 3`,
`has_ntemp=False`) reads/writes CTE components individually via
`get_thermal_expansion` and was not touched.

Regression tests in `tests/unit/test_material_writers.py`: `_project_cte`
truncation and its two invariant checks, the thermal line's token count for
the mixed isotropic/orthotropic fixture (2 and 4, not 7), and a full
write -> read round trip asserting `specific_heat` and `cte` survive exactly.

## `sg33_cube_distribution_input_bug.inp` + `.ori` (1.8 KB / 304 B)

Three stacked C3D8 hexahedra. Element 1 is the isotropic `Matrix`; elements 2
and 3 are the orthotropic `Yarn`, taking their orientation from a
`*Distribution` whose rows live in the external `.ori` file.

```python
sgio.read(fixture, "abaqus", sgdim=3, model_type="SD1")
# ValueError: Abaqus orientation 'Orientations' has no coordinates for element 2.
```

sgio built its distribution table only from rows physically present under the
keyword and never followed `Input=`. 0.7.0 fell back to a single default
orientation for every element, silently; 0.8.0 raised. The missing feature was
in both.

The two yarn elements are given **different** fibre directions (+X and +Y) on
purpose. After a fix, `mesh.cell_data['property_ref_csys']` must hold **2
distinct** orientations across the 3 elements — a silent fallback collapses
that to 1, which is what made the defect invisible in the first place. Counting
distinct values is the assertion; "it read without raising" is not.

Two shape constraints worth preserving if this deck is edited:

- The `*Solid Section` cards must not be the file's last block. A trailing
  newline after their bare `,` data line makes `inpRW` emit an extra empty data
  row, and `_process_section` does `float(section_block.data[-2])` guarding only
  `ValueError`/`IndexError` — so it dies with a `TypeError` before reaching the
  defect under test. (That is arguably its own small robustness bug: a valid
  deck ending in a `*Solid Section` cannot be read.)
- The `.ori` keeps Abaqus's leading blank-label default row. A fix must not
  mistake it for an element labelled 0.

**Fixed in this working tree**, entirely at the parser layer (`sgio/_vendors/inprw`)
rather than by hand-parsing `Input=` in `mapper_in.py`:

- The vendored `inpRW` library already has a generic mechanism for keywords
  whose data can live in an external `Input=` file (`config._dataKWs`): it
  reads the file and merges its rows into the block's `.data`, so callers
  never need to know whether a keyword's data came from the main `.inp` or a
  side file. `distribution` was simply missing from that set — added it.
- Exercising that path for the first time (nothing in this repo previously
  used `Input=` on any `_dataKWs` keyword) hit a second, independent bug: the
  `_data = inpKeyword()` branch in `inpKeyword.parseKWData` does a bare
  `import inpKeywordSequence`, an absolute import left over from before the
  library was vendored under the `sgio._vendors.inprw` package. It raised
  `ModuleNotFoundError` for *any* keyword using this branch, not just
  `*Distribution`. Changed to `from . import inpKeywordSequence`, matching
  every other import in the file.
- A *third* bug surfaced once the file actually loaded: `_parseSubData` reads
  the whole external file's raw text and splits it on newlines with no
  trimming, so a file ending in a normal trailing newline (i.e. essentially
  any well-formed text file) produces one spurious all-blank row after the
  real data. In `mapper_in.py`'s distribution-table loop that phantom row has
  the same blank label as the real default row and was parsed *after* it,
  silently overwriting the real default with an empty coordinate list.
  Harmless for this fixture (both Yarn elements have explicit rows), but any
  RVE that leans on the default for elements *not* listed in the table would
  get corrupted defaults. First patched as a `len(row) < 2` guard in
  `mapper_in.py`; moved down into `_parseSubData` itself (strip trailing blank
  lines from `self.lines` before `_parseData()` turns them into rows) once
  code review pointed out the guard was a cross-layer workaround for a defect
  that belongs to the shared vendor parsing every `_dataKWs` keyword's
  external file goes through -- one fix there covers all of them, not just
  `*Distribution`.

Regression tests in `tests/unit/test_abaqus_mapper_in.py`:
`test_map_input_to_structure_gene_reads_distribution_input_file` (this
fixture: 2 distinct Yarn orientations, matrix gets the global default) and
`test_map_input_to_structure_gene_applies_input_file_distribution_default`
(a synthetic `Input=` file where one element has no explicit row, so it must
fall back to the real default and not the phantom trailing blank one).
