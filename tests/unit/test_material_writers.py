"""Test module for `sgio.iofunc.common.material_writers`.

Covers the SwiftComp thermal-record isotropy projection: `_write_material`
writes CTE + specific heat as one line whose length depends on isotropy
(1/3/6 CTE components), while sgio's internal `CauchyContinuumModel.cte` is
always a fixed 6-component Voigt vector. Writing all 6 unconditionally
shifted specific heat into what SwiftComp parses as an extra CTE component,
a silent wrong value (see docs archive issue 20260903-swiftcomp-cte-vector-length).
"""

from __future__ import annotations

import pytest

import sgio
from sgio.iofunc.common.material_writers import _project_cte


@pytest.mark.unit
class TestProjectCte:
    """`_project_cte` truncates to what SwiftComp's isotropy-dependent record holds."""

    def test_isotropic_keeps_one_component(self):
        assert _project_cte([5.8e-05, 5.8e-05, 5.8e-05, 0.0, 0.0, 0.0], 0) == [5.8e-05]

    def test_orthotropic_keeps_three_components(self):
        assert _project_cte([-5e-07, 1e-05, 1e-05, 0.0, 0.0, 0.0], 1) == [-5e-07, 1e-05, 1e-05]

    def test_anisotropic_keeps_all_six(self):
        cte = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        assert _project_cte(cte, 2) == cte

    def test_isotropic_rejects_unequal_normal_components(self):
        with pytest.raises(ValueError, match="equal in all three directions"):
            _project_cte([5.8e-05, 6.0e-05, 5.8e-05, 0.0, 0.0, 0.0], 0)

    def test_orthotropic_rejects_nonzero_shear(self):
        with pytest.raises(ValueError, match="shear components"):
            _project_cte([1.0, 2.0, 3.0, 0.0, 0.1, 0.0], 1)


def _material_block_thermal_line_lengths(sc_text: str) -> list[int]:
    """Extract the last (thermal) line of each material block, by token count.

    Each material block starts at its "... material id, anisotropy, ntemp"
    header line and ends at the next blank line; for `physics in [1, 4, 6]`
    the thermal record (CTE + specific heat) is always that block's last line.
    """
    lengths = []
    block: list[str] = []
    in_block = False
    for line in sc_text.splitlines():
        if "material id, anisotropy, ntemp" in line:
            in_block = True
            block = [line]
        elif in_block:
            if line.strip() == "":
                lengths.append(len(block[-1].split()))
                in_block = False
            else:
                block.append(line)
    return lengths


@pytest.mark.unit
def test_swiftcomp_thermal_line_length_matches_isotropy(gmsh_test_files, tmp_path):
    """The written thermal line must carry 2/4 numbers for isotropy 0/1, not 7.

    Regression fixture: `sg33_cube_two_materials_min_gmsh41.msh` pairs an
    isotropic `matrix` with an orthotropic `fibre`, so one write covers both
    branches. Before the fix both lines carried all 6 CTE components plus
    specific heat, so SwiftComp read specific heat out of the wrong column.
    """
    sg = sgio.read_sg_from_gmsh_bundle(
        main_msh=gmsh_test_files["root"] / "sg33_cube_two_materials_min_gmsh41.msh",
        sections_json=gmsh_test_files["root"] / "sections_thermoelastic_cte_bug.json",
        config_json=gmsh_test_files["root"] / "config_thermoelastic.json",
        model_type="SD1",
    )

    out_file = tmp_path / "thermoelastic.sg"
    sgio.write(sg=sg, filename=str(out_file), file_format="sc",
               format_version="2.1", model_type="SD1")

    # matrix (isotropy 0): a11, cp -- 2 numbers. fibre (isotropy 1): a11, a22, a33, cp -- 4.
    assert _material_block_thermal_line_lengths(out_file.read_text()) == [2, 4]


@pytest.mark.unit
def test_swiftcomp_specific_heat_round_trips(gmsh_test_files, tmp_path):
    """write -> read must reproduce specific_heat and cte exactly, not just avoid raising."""
    sg = sgio.read_sg_from_gmsh_bundle(
        main_msh=gmsh_test_files["root"] / "sg33_cube_two_materials_min_gmsh41.msh",
        sections_json=gmsh_test_files["root"] / "sections_thermoelastic_cte_bug.json",
        config_json=gmsh_test_files["root"] / "config_thermoelastic.json",
        model_type="SD1",
    )

    out_file = tmp_path / "thermoelastic.sg"
    sgio.write(sg=sg, filename=str(out_file), file_format="sc",
               format_version="2.1", model_type="SD1")

    sg_read_back = sgio.read(str(out_file), "sc", sgdim=3, model_type="SD1", physics=1)
    materials_by_specific_heat = {
        round(m.specific_heat): m for m in sg_read_back.materials.values()
    }

    matrix = materials_by_specific_heat[1100]
    assert matrix.specific_heat == pytest.approx(1100.0)
    assert matrix.cte == pytest.approx([5.8e-05, 5.8e-05, 5.8e-05, 0.0, 0.0, 0.0])

    fibre = materials_by_specific_heat[750]
    assert fibre.specific_heat == pytest.approx(750.0)
    assert fibre.cte == pytest.approx([-5e-07, 1e-05, 1e-05, 0.0, 0.0, 0.0])
