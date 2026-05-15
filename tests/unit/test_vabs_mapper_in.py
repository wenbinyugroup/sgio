"""Tests for the VABS input mapper."""

import numpy as np
import pytest

from sgio.core.mesh import SGMesh
from sgio.iofunc.vabs.mapper_in import map_input_to_structure_gene


@pytest.mark.unit
def test_map_input_to_structure_gene_resolves_material_ids_to_names():
    """VABS mapper should convert raw material IDs into SG material-name combos."""
    mesh = SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        cells=[("line", np.array([[0, 1]]))],
    )
    parsed = {
        "format_version": "4.1",
        "configs": {
            "sgdim": 2,
            "physics": 1,
            "do_damping": 1,
            "is_temp_nonuniform": 0,
            "model": 1,
            "curvature": [0.25, 0.5, 0.75],
            "oblique": [0.8, 0.2],
        },
        "mesh": mesh,
        "material_rotation_combinations": {7: (3, 45.0)},
        "materials": {"mat_a": {"density": 1.0}},
        "material_id_pairs": [("mat_a", 3)],
    }

    sg = map_input_to_structure_gene(parsed)

    assert sg.version == "4.1"
    assert sg.smdim == 1
    assert sg.sgdim == 2
    assert sg.mesh is mesh
    assert sg.analysis_config.physics == 1
    assert sg.analysis_config.do_damping == 1
    assert sg.analysis_config.model == 1
    assert sg.initial_twist == 0.25
    assert sg.initial_curvature == [0.5, 0.75]
    assert sg.oblique == [0.8, 0.2]
    assert sg.materials["mat_a"]["density"] == 1.0
    assert sg.mocombos[7] == ("mat_a", 45.0)
