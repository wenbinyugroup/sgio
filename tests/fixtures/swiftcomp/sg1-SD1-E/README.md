---
title: sg1-SD1-E
tags:
  - swiftcomp
  - test-fixture
---

# sg1-SD1-E

Minimal periodic SwiftComp homogenization fixture.

- Macro model: Cauchy continuum solid (SD1)
- Structure-gene dimension: 1D
- Analysis: elastic (`analysis=0`)

## Inputs

- `sg1-SD1-E.sg`: isotropic baseline.
- `sg1-SD1-E-ORTHO.sg`: orthotropic material with an elemental local coordinate system.
- `sg1-SD1-E-ANISO.sg`: general-anisotropic material with an elemental local coordinate system.

Run each input as `SwiftComp <input> 3D H`. Its echo must report the stated model,
analysis, SG dimension, material isotropy, and—when non-isotropic—elemental orientation.
