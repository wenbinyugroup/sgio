"""Tests for the SwiftComp input mapper."""

import numpy as np
import pytest

from sgio.core.mesh import SGMesh
from sgio.iofunc.swiftcomp.mapper_in import map_input_to_structure_gene


@pytest.mark.unit
def test_map_input_to_structure_gene_maps_beam_specific_fields():
    """SwiftComp mapper should populate beam-specific SG fields."""
    mesh = SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        cells=[("line", np.array([[0, 1]]))],
    )
    parsed = {
        "format_version": "2.2",
        "smdim": 1,
        "configs": {
            "sgdim": 2,
            "physics": 1,
            "do_damping": 0,
            "is_temp_nonuniform": 1,
            "force_flag": 4,
            "steer_flag": 5,
            "ndim_degen_elem": 2,
            "num_slavenodes": 3,
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

    assert sg.version == "2.2"
    assert sg.smdim == 1
    assert sg.sgdim == 2
    assert sg.mesh is mesh
    assert sg.analysis_config.physics == 1
    assert sg.analysis_config.is_temp_nonuniform == 1
    assert sg.analysis_config.force_flag == 4
    assert sg.analysis_config.steer_flag == 5
    assert sg.analysis_config.model == 1
    assert sg.ndim_degen_elem == 2
    assert sg.num_slavenodes == 3
    assert sg.initial_twist == 0.25
    assert sg.initial_curvature == [0.5, 0.75]
    assert sg.oblique == [0.8, 0.2]
    assert sg.mocombos[7] == ("mat_a", 45.0)


@pytest.mark.unit
def test_map_input_to_structure_gene_maps_shell_specific_fields():
    """SwiftComp mapper should populate shell-specific curvature and Lame data."""
    mesh = SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]),
        cells=[("triangle", np.array([[0, 1, 2]]))],
    )
    parsed = {
        "format_version": "2.2",
        "smdim": 2,
        "configs": {
            "sgdim": 2,
            "physics": 0,
            "num_slavenodes": 0,
            "model": 0,
            "curvature": [1.2, 2.3],
            "lame": [3.4, 4.5],
        },
        "mesh": mesh,
        "material_rotation_combinations": {},
        "materials": {},
        "material_id_pairs": [],
    }

    sg = map_input_to_structure_gene(parsed)

    assert sg.smdim == 2
    assert sg.initial_curvature == [1.2, 2.3]
    assert sg.lame_params == [3.4, 4.5]
