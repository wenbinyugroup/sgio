---
title: sg2-BM2-TE
tags:
  - swiftcomp
  - test-fixture
---

# sg2-BM2-TE

Minimal periodic SwiftComp homogenization fixture.

- Macro model: Timoshenko beam (BM2)
- Structure-gene dimension: 2D
- Analysis: thermoelastic (`analysis=1`)

## Inputs

- `sg2-BM2-TE.sg`: isotropic baseline.
- `sg2-BM2-TE-ORTHO.sg`: orthotropic material with an elemental local coordinate system.
- `sg2-BM2-TE-ANISO.sg`: general-anisotropic material with an elemental local coordinate system.

Run each input as `SwiftComp <input> 1D H`. Its echo must report the stated submodel,
analysis, SG dimension, material isotropy, and—when non-isotropic—elemental orientation.
