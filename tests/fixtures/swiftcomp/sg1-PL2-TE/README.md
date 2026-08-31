---
title: sg1-PL2-TE
tags:
  - swiftcomp
  - test-fixture
---

# sg1-PL2-TE

Minimal periodic SwiftComp homogenization fixture.

- Macro model: Reissner-Mindlin plate/shell (PL2)
- Structure-gene dimension: 1D
- Analysis: thermoelastic (`analysis=1`)

## Inputs

- `sg1-PL2-TE.sg`: isotropic baseline.
- `sg1-PL2-TE-ORTHO.sg`: orthotropic material with an elemental local coordinate system.
- `sg1-PL2-TE-ANISO.sg`: general-anisotropic material with an elemental local coordinate system.

Run each input as `SwiftComp <input> 2D H`. Its echo must report the stated submodel,
analysis, SG dimension, material isotropy, and—when non-isotropic—elemental orientation.
