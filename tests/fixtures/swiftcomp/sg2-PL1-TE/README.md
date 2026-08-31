---
title: sg2-PL1-TE
tags:
  - swiftcomp
  - test-fixture
---

# sg2-PL1-TE

Minimal periodic SwiftComp homogenization fixture.

- Macro model: Kirchhoff-Love plate/shell (PL1)
- Structure-gene dimension: 2D
- Analysis: thermoelastic (`analysis=1`)

## Inputs

- `sg2-PL1-TE.sg`: isotropic baseline.
- `sg2-PL1-TE-ORTHO.sg`: orthotropic material with an elemental local coordinate system.
- `sg2-PL1-TE-ANISO.sg`: general-anisotropic material with an elemental local coordinate system.

Run each input as `SwiftComp <input> 2D H`. Its echo must report the stated submodel,
analysis, SG dimension, material isotropy, and—when non-isotropic—elemental orientation.
