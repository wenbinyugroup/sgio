"""End-to-end check: Abaqus thermal properties -> SwiftComp -> effective CTE."""

from __future__ import annotations

import shutil

import pytest

import sgio

# Isotropic-equivalent stiffness written as *Elastic, type=ANISOTROPIC, so the
# result depends only on the thermal data (E = 1000, nu = 0.3)
_LAM, _MU = 1.0e3 * 0.3 / (1.3 * 0.4), 1.0e3 / 2.6
_ANISO_ELASTIC = [
    _LAM + 2 * _MU, _LAM, _LAM + 2 * _MU, _LAM, _LAM, _LAM + 2 * _MU,
    0, 0, 0, _MU, 0, 0, 0, 0, _MU, 0, 0, 0, 0, 0, _MU,
]


def _cube_inp(material_lines: str) -> str:
    """Return a 2x2x2 C3D8 unit-cube .inp made of one material ``M``."""
    node_id = {}
    nodes = []
    for k in range(3):
        for j in range(3):
            for i in range(3):
                node_id[(i, j, k)] = len(nodes) + 1
                nodes.append(f"{len(nodes) + 1}, {i / 2}, {j / 2}, {k / 2}")
    elems = []
    for k in range(2):
        for j in range(2):
            for i in range(2):
                corners = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                           (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
                conn = [node_id[(i + a, j + b, k + c)] for a, b, c in corners]
                elems.append(f"{len(elems) + 1}, " + ", ".join(map(str, conn)))
    return (
        "*Heading\n*Node\n" + "\n".join(nodes)
        + "\n*Element, type=C3D8, elset=ALL\n" + "\n".join(elems)
        + "\n*Material, name=M\n" + material_lines
        + "*Solid Section, elset=ALL, material=M\n1.0,\n"
    )


@pytest.mark.integration
@pytest.mark.requires_solver
@pytest.mark.skipif(shutil.which('SwiftComp') is None, reason='SwiftComp not installed')
@pytest.mark.parametrize("material_lines, expected_cte", [
    (
        "*Elastic, type=ENGINEERING CONSTANTS\n"
        "100., 80., 60., 0.3, 0.25, 0.2, 30., 25., 20.\n"
        "*Expansion, type=ORTHO\n1e-06, 2e-06, 3e-06\n",
        [1e-06, 2e-06, 3e-06, 0.0, 0.0, 0.0],
    ),
    (
        "*Elastic, type=ANISOTROPIC\n"
        + ",\n".join(", ".join(map(str, _ANISO_ELASTIC[i:i + 8])) for i in (0, 8, 16))
        + ",\n*Expansion, type=ANISO\n1e-06, 2e-06, 3e-06, 4e-06, 5e-06, 6e-06\n",
        # Abaqus (a11, a22, a33, a12, a13, a23) -> SwiftComp (.., 2a23, 2a13, 2a12)
        [1e-06, 2e-06, 3e-06, 6e-06, 5e-06, 4e-06],
    ),
], ids=["ortho", "aniso"])
def test_single_material_effective_cte_equals_input(tmp_path, material_lines, expected_cte):
    inp = tmp_path / "cube.inp"
    inp.write_text(_cube_inp(material_lines + "*Specific Heat\n900.,\n"), encoding="utf-8")
    sc_file = str(tmp_path / "cube.sc")

    sgio.convert(str(inp), sc_file, "abaqus", "sc", sgdim=3, model_type="SD1",
                 physics="thermoelastic")
    sgio.run("SwiftComp", sc_file, "h", smdim=3)

    result = sgio.read_output_model(f"{sc_file}.k", "sc", model_type="SD1")
    assert result.cte == pytest.approx(expected_cte, abs=1e-12)
    assert result.specific_heat == pytest.approx(900.0)
