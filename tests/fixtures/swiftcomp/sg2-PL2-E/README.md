---
title: sg2-PL2-E
tags:
  - swiftcomp
  - test-fixture
---

# sg2-PL2-E

Minimal periodic SwiftComp homogenization fixture.

- Macro model: Reissner-Mindlin plate/shell (PL2)
- Structure-gene dimension: 2D
- Analysis: elastic (`analysis=0`)

## Inputs

- `sg2-PL2-E.sg`: isotropic baseline.
- `sg2-PL2-E-ORTHO.sg`: orthotropic material with an elemental local coordinate system.
- `sg2-PL2-E-ANISO.sg`: general-anisotropic material with an elemental local coordinate system.

Run each input as `SwiftComp <input> 2D H`. Its echo must report the stated submodel,
analysis, SG dimension, material isotropy, and—when non-isotropic—elemental orientation.
