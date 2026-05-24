from __future__ import annotations

from pathlib import Path

import sgio


def write_gmsh_bundle_sidecars(
    sg: sgio.StructureGene,
    output_dir: str | Path,
    *,
    sections_filename: str = "sections.json",
    config_filename: str = "config.json",
) -> tuple[Path, Path]:
    """Write `sections.json` and `config.json` for one SG-on-Gmsh bundle.

    The helper follows the current bundle convention used by the examples:

    - `main.msh` carries mesh-bound data.
    - `sections.json` carries material payloads keyed by `layer_<property_id>`.
    - `config.json` carries `SGAnalysisConfig`.
    """

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    records = []
    for section in sg.sections.values():
        if section.property_id is None:
            continue
        material = sg.materials.get(section.material)
        if material is None:
            continue
        records.append(
            sgio.section_model_to_record(
                material,
                name=f"layer_{int(section.property_id)}",
                id=int(section.property_id),
                material=section.material,
                orientation=float(section.orientation),
            )
        )

    sections_path = output_root / sections_filename
    config_path = output_root / config_filename
    sgio.write_sections_to_json(records, sections_path)
    sgio.write_config_to_json(sg.analysis_config, config_path)
    return sections_path, config_path
