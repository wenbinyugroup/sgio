# Multiscale Beam: Micro Homogenization to Macro Assembly

## Problem Description

A slender composite blade is analysed at two scales:

- **Micro scale** — a 2D beam cross-section (a Structure Gene) is homogenized by
  VABS into an *effective* 1D beam constitutive model (axial `EA`, bending
  `EI22`/`EI33`, torsion `GJ`).
- **Macro scale** — a 1D beam finite-element model uses that effective section
  along the blade span, together with its boundary conditions and tip load.

The task is to carry the micro-scale effective section into a macro beam model
**as data**, using the generic finite-element entry points, and without invoking
any external solver.

## Solution

The script wires four steps:

1. **Read the micro homogenization output** with {func}`sgio.read_output_model`.
   Pointed at a VABS `.sg.K` result it returns an `EulerBernoulliBeamModel`
   carrying the effective section stiffness.
2. **Read the macro beam mesh** with {func}`sgio.read_fe_model`, the explicit
   generic-FE entry point. The Abaqus `.inp` (B31 beam elements) maps to a
   backend-neutral {class}`sgio.FEModel`. Its `extras` carry the structural
   blocks the SG reader does not model — `*Boundary`, `*Cload`, `*Step` —
   captured as a non-lossy fallback.
3. **Wrap and assemble** the `FEModel` into a {class}`sgio.StructuralModel` via
   `StructuralModel.from_fe(...)`, then inject the homogenized section as the
   macro beam's section material (`materials` plus a referencing
   {class}`sgio.Section`).
4. **Inspect** the captured boundary/load/step payload from `fe.extras`, showing
   how a caller retrieves the structural data for downstream assembly.

```{literalinclude} ../../../examples/multiscale_beam/run.py
:language: python
```

The micro→macro handoff is pure data flow: the effective section object becomes
a material of the macro model. Model assembly and any solver export remain
explicit caller steps — sgio provides the IR and the entry points, not an
automated end-to-end pipeline.

## Result

Running the example prints the effective section, the macro mesh summary, the
injected section, and the captured structural blocks:

```text
[micro] effective Euler-Bernoulli beam section
        EA   = 3.07204e+08
        EI22 = 2.08882e+08
        EI33 = 3.65306e+09
        GJ   = 1.94298e+08

[macro] beam mesh: 5 nodes, 4 beam elements
[macro] injected homogenized section as material 'blade_section'
        materials = ['blade_section']
        sections  = ['beam']

[macro] structural blocks captured into fe.extras (fallback):
        abaqus_boundary: *Boundary {} data=[['ROOT', 'ENCASTRE']]
        abaqus_loads: *Cload {} data=[['TIP', 2, '-1000.0']]
        abaqus_steps: *Step {'name': 'TipLoad', 'nlgeom': 'NO'} data=[]

Multiscale handoff complete: micro effective section -> macro beam model.
```

```bash
python examples/multiscale_beam/run.py
```

## File List

- [run.py](../../../examples/multiscale_beam/run.py): The end-to-end script
- [micro_section.sg.K](../../../examples/multiscale_beam/micro_section.sg.K): VABS beam-section homogenization output (the micro effective properties)
- [cantilever_macro.inp](../../../examples/multiscale_beam/cantilever_macro.inp): Abaqus B31 cantilever beam mesh with root encastre and a tip load (the macro model)
