---
title: sg1-SD1-TE
tags:
  - swiftcomp
  - test-fixture
---

# sg1-SD1-TE

Minimal periodic SwiftComp homogenization fixture.

- Macro model: Cauchy continuum solid (SD1)
- Structure-gene dimension: 1D
- Analysis: thermoelastic (`analysis=1`)

## Inputs

- `sg1-SD1-TE.sg`: isotropic baseline.
- `sg1-SD1-TE-ORTHO.sg`: orthotropic material with an elemental local coordinate system.
- `sg1-SD1-TE-ANISO.sg`: general-anisotropic material with an elemental local coordinate system.

Run each input as `SwiftComp <input> 3D H`. Its echo must report the stated model,
analysis, SG dimension, material isotropy, and—when non-isotropic—elemental orientation.
