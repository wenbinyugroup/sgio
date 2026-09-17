# Minimal 3D plain-weave TexGen fixture

This fixture was generated with TexGen 3.13.1 using the same construction as
`micro-structure-builders/weave_3d`:

- `CTextileWeave2D(2, 2, 1.0, 0.2, False)`
- `SwapPosition(0, 0)` and `SwapPosition(1, 1)`
- yarn width `0.8` and yarn height `0.1`
- `CRectangularVoxelMesh("CPeriodicBoundaries")`
- voxel grid `3 x 3 x 1`

The physical mesh has 32 nodes and 9 C3D8R elements. Its element sets contain
one matrix element and two elements for each of `Yarn0` through `Yarn3`. TexGen
also adds six periodic-constraint driver nodes, so SGIO reads 38 nodes from the
complete Abaqus deck.

`plain_weave_3d.ori` is retained because `plain_weave_3d.inp` references it via
the Abaqus `*Distribution, Input=` parameter.

Run `python generate.py` with CPython 3.9 and an installation of TexGen 3.13.1
at `C:\Program Files\TexGen` to regenerate the fixture.
