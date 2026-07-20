"""VABS input mapper.

This module maps raw VABS parser output into application-layer IR objects.
"""

from __future__ import annotations

from typing import Any, Mapping

from sgio.core.sg import StructureGene

from ..common import capture_material_and_combo_source_ids
from .keywords import DEFAULT_SMDIM


def map_input_to_structure_gene(parsed: Mapping[str, Any]) -> StructureGene:
    """Map parsed VABS input payload into a ``StructureGene``.

    Parameters
    ----------
    parsed : mapping[str, Any]
        Raw parser payload produced by :func:`parse_input_buffer`.

    Returns
    -------
    StructureGene
        Structure gene populated from the parsed payload.
    """
    configs = parsed["configs"]
    sg = StructureGene()
    sg.version = parsed["format_version"]
    sg.smdim = DEFAULT_SMDIM
    sg.sgdim = configs["sgdim"]
    sg.analysis_config.physics = configs["physics"]
    sg.analysis_config.do_damping = configs.get("do_damping", 0)
    sg.analysis_config.is_temp_nonuniform = configs.get("is_temp_nonuniform", 0)
    sg.analysis_config.model = configs["model"]
    sg.initial_twist, *initial_curvature = configs.get("curvature", [0.0, 0.0, 0.0])
    sg.initial_curvature = initial_curvature
    sg.oblique = configs.get("oblique", [1.0, 0.0])

    sg.mesh = parsed["mesh"]
    sg.materials = parsed["materials"]
    sg.mocombos = _map_material_rotation_combinations(
        parsed["material_rotation_combinations"],
        parsed["material_id_pairs"],
    )
    capture_material_and_combo_source_ids(sg, parsed["material_id_pairs"], "vabs")
    return sg


def _map_material_rotation_combinations(
    material_rotation_combinations: Mapping[int, tuple[int, float]],
    material_id_pairs: list[tuple[str, int]],
) -> dict[int, tuple[str, float]]:
    """Resolve VABS material IDs in combination records back to material names."""
    id_to_name = {mat_id: name for name, mat_id in material_id_pairs}
    return {
        combo_id: (id_to_name.get(mat_id, f"Material_{mat_id}"), angle)
        for combo_id, (mat_id, angle) in material_rotation_combinations.items()
    }
