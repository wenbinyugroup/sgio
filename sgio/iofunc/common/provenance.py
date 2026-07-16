"""Shared helpers for solver-file id provenance capture.

Solver formats (VABS, SwiftComp) label materials and material-orientation
combinations with integers. Those integers are a property of the file, not the
material's identity (the name is the ground truth). To reproduce a file's
numbering on a same-format re-export, readers record the source ids as
provenance; writers prefer them via
:func:`sgio.iofunc.common.material_writers.build_material_id_map`.
"""

from __future__ import annotations

from sgio.core.sg import StructureGene


def capture_material_and_combo_source_ids(
    sg: StructureGene,
    material_id_pairs: list[tuple[str, int]],
    format_name: str,
) -> None:
    """Record source solver ids so a same-format re-export preserves numbering.

    Parameters
    ----------
    sg : StructureGene
        Structure gene whose materials and sections were just populated from a
        solver file.
    material_id_pairs : list[tuple[str, int]]
        ``(material_name, source_id)`` pairs parsed from the file.
    format_name : str
        Format key under which to store the provenance (e.g. ``"vabs"``).
    """
    # Material ids: remember the label each material had in the source file.
    for name, mat_id in material_id_pairs:
        sg.fe_model.material_source_ids.setdefault(name, {})[format_name] = int(mat_id)

    # Combo/layer ids: the mocombos setter already stored them as property_id;
    # mirror them onto the per-format provenance for later property_id removal.
    for section in sg.sections.values():
        if section.property_id is not None:
            section.source_ids[format_name] = int(section.property_id)
