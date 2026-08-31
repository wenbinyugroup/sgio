---
title: sg3-BM1-E
tags:
  - swiftcomp
  - test-fixture
---

# sg3-BM1-E

Minimal periodic SwiftComp homogenization fixture.

- Macro model: Euler-Bernoulli beam (BM1)
- Structure-gene dimension: 3D
- Analysis: elastic (`analysis=0`)

## Inputs

- `sg3-BM1-E.sg`: isotropic baseline.
- `sg3-BM1-E-ORTHO.sg`: orthotropic material with an elemental local coordinate system.
- `sg3-BM1-E-ANISO.sg`: general-anisotropic material with an elemental local coordinate system.

Run each input as `SwiftComp <input> 1D H`. Its echo must report the stated submodel,
analysis, SG dimension, material isotropy, and—when non-isotropic—elemental orientation.
