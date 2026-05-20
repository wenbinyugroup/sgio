"""SwiftComp input mapper."""

from __future__ import annotations

from typing import Any, Mapping

from sgio.core.sg import StructureGene


def map_input_to_structure_gene(parsed: Mapping[str, Any]) -> StructureGene:
    """Map parsed SwiftComp input payload into a ``StructureGene``."""
    configs = parsed["configs"]
    sg = StructureGene()
    sg.version = parsed["format_version"]
    sg.smdim = parsed["smdim"]
    sg.sgdim = configs["sgdim"]
    sg.analysis_config.physics = configs["physics"]
    sg.analysis_config.do_damping = configs.get("do_damping", 0)
    sg.analysis_config.is_temp_nonuniform = configs.get("is_temp_nonuniform", 0)
    sg.analysis_config.force_flag = configs.get("force_flag", 0)
    sg.analysis_config.steer_flag = configs.get("steer_flag", 0)
    sg.ndim_degen_elem = configs.get("ndim_degen_elem", 0)
    sg.num_slavenodes = configs.get("num_slavenodes", 0)

    if sg.smdim != 3:
        sg.analysis_config.model = configs["model"]
        if sg.smdim == 1:
            sg.initial_twist, *initial_curvature = configs.get(
                "curvature",
                [0.0, 0.0, 0.0],
            )
            sg.initial_curvature = initial_curvature
            sg.oblique = configs.get("oblique", [1.0, 0.0])
        elif sg.smdim == 2:
            sg.initial_curvature = configs.get("curvature", [0.0, 0.0])
            sg.lame_params = configs.get("lame", [1.0, 1.0])

    sg.mesh = parsed["mesh"]
    sg.materials = parsed["materials"]
    sg.mocombos = _map_material_rotation_combinations(
        parsed["material_rotation_combinations"],
        parsed["material_id_pairs"],
    )
    return sg


def _map_material_rotation_combinations(
    material_rotation_combinations: Mapping[int, tuple[int, float]],
    material_id_pairs: list[tuple[str, int]],
) -> dict[int, tuple[str, float]]:
    """Resolve SwiftComp material IDs in combination records back to names."""
    id_to_name = {mat_id: name for name, mat_id in material_id_pairs}
    return {
        combo_id: (id_to_name.get(mat_id, f"Material_{mat_id}"), angle)
        for combo_id, (mat_id, angle) in material_rotation_combinations.items()
    }
