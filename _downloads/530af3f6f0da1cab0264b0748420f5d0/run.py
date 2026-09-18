"""Multiscale beam example.

Demonstrates the Phase 10 generic-FE workflow end to end, without running any
external solver:

1. Micro  -- read a VABS beam-section *homogenization output* into an effective
             Euler-Bernoulli beam model (``read_output_model``).
2. Macro  -- read a cantilever B31 beam mesh as a generic ``FEModel``
             (``read_fe_model``) and wrap it as a ``StructuralModel``.
3. Assemble -- inject the homogenized effective section as the macro beam's
             section material.
4. Inspect -- show the structural blocks (boundary/load/step) that the Abaqus
             reader captured into ``FEModel.extras`` as a fallback.

Run:
    python examples/multiscale_beam/run.py
"""
from __future__ import annotations

from pathlib import Path

import sgio
from sgio import Section

HERE = Path(__file__).parent
MICRO_OUTPUT = HERE / "micro_section.sg.K"      # VABS homogenization result
MACRO_MESH = HERE / "cantilever_macro.inp"      # Abaqus B31 beam mesh


def main() -> None:
    # --- 1. Micro: effective beam section from VABS homogenization output ----
    effective = sgio.read_output_model(str(MICRO_OUTPUT), "vabs", model_type="BM1")
    print("[micro] effective Euler-Bernoulli beam section")
    print(f"        EA   = {effective.ea:.6g}")
    print(f"        EI22 = {effective.ei22:.6g}")
    print(f"        EI33 = {effective.ei33:.6g}")
    print(f"        GJ   = {effective.gj:.6g}")

    # --- 2. Macro: read beam mesh as a generic FEModel, wrap as structural ---
    fe = sgio.read_fe_model(str(MACRO_MESH), "abaqus", model_type="BM1", sgdim=3)
    sm = sgio.StructuralModel.from_fe(fe)
    n_elems = sum(len(cb.data) for cb in sm.mesh.cells)
    print(f"\n[macro] beam mesh: {len(sm.mesh.points)} nodes, {n_elems} beam elements")

    # --- 3. Assemble: use the homogenized section as the macro beam material --
    sm.materials["blade_section"] = effective
    sm.sections["beam"] = Section(
        name="beam", material="blade_section", property_id=1
    )
    print("[macro] injected homogenized section as material 'blade_section'")
    print(f"        materials = {list(sm.materials)}")
    print(f"        sections  = {list(sm.sections)}")

    # --- 4. Inspect: structural payload captured by the Abaqus reader ---------
    print("\n[macro] structural blocks captured into fe.extras (fallback):")
    for key in ("abaqus_boundary", "abaqus_loads", "abaqus_steps"):
        blocks = sm.fe.extras.get(key, [])
        for block in blocks:
            print(f"        {key}: *{block['keyword']} {block['parameters']} "
                  f"data={block['data']}")

    print("\nMultiscale handoff complete: micro effective section -> macro beam model.")


if __name__ == "__main__":
    main()
