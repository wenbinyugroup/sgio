"""The ``materials`` and ``sections`` blocks of an SG manifest.

``materials`` lists each material once as a grouped material record.
``sections`` binds a mesh physical group -- matched by ``name``, falling back
to ``id`` -- to a material and a layup angle.
"""

from __future__ import annotations

from typing import Any

from sgio._exceptions import IncompleteModelDataError
from sgio.core import StructureGene
from sgio.model import CauchyContinuumModel

from ._mesh_convert import mesh_to_sg
from .common.material_json import deserialize_material_record, serialize_material_record

_SECTION_KEYS = {'name', 'id', 'material', 'orientation'}


def read_materials(records: Any) -> dict[str, CauchyContinuumModel]:
    """Deserialize the ``materials`` block, keyed by material name.

    Parameters
    ----------
    records : list of dict
        Grouped material records, each with a unique ``name``.

    Returns
    -------
    dict[str, CauchyContinuumModel]
        Materials keyed by name.
    """
    if not isinstance(records, list):
        raise TypeError("SG manifest field 'materials' must be a list.")
    materials: dict[str, CauchyContinuumModel] = {}
    for record in records:
        if not isinstance(record, dict) or not record.get('name'):
            raise ValueError("Every SG manifest material must be an object with a 'name'.")
        if record['name'] in materials:
            raise ValueError(f"Duplicate SG manifest material name: {record['name']!r}.")
        materials[record['name']] = deserialize_material_record(record)
    return materials


def read_sections(records: Any, materials: dict[str, CauchyContinuumModel]) -> list[dict]:
    """Validate the ``sections`` block against the declared materials.

    Parameters
    ----------
    records : list of dict
        Section records with ``name`` and/or ``id``, ``material`` and an
        optional ``orientation`` (degrees, 0 when omitted).
    materials : dict[str, CauchyContinuumModel]
        Materials the sections may reference.

    Returns
    -------
    list of dict
        The validated section records.
    """
    if not isinstance(records, list):
        raise TypeError("SG manifest field 'sections' must be a list.")
    names: set[str] = set()
    ids: set[int] = set()
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("Every SG manifest section must be an object.")
        unknown = set(record) - _SECTION_KEYS
        if unknown:
            raise ValueError(f"Unknown SG manifest section fields {sorted(unknown)}.")
        if record.get('name') is None and record.get('id') is None:
            raise ValueError("Every SG manifest section needs a 'name' or an 'id'.")
        if record.get('material') not in materials:
            raise ValueError(
                f"SG manifest section {record.get('name', record.get('id'))!r} references "
                f"undeclared material {record.get('material')!r}."
            )
        _add_unique(names, record.get('name'), 'name')
        _add_unique(ids, record.get('id'), 'id')
    return records


def _add_unique(seen: set, value: Any, key: str) -> None:
    """Record one section identity, rejecting duplicates."""
    if value is None:
        return
    if value in seen:
        raise ValueError(f"Duplicate SG manifest section {key}: {value!r}.")
    seen.add(value)


def structure_gene_from_mesh(mesh, sgdim: int, model_type: str, data: dict) -> StructureGene:
    """Build a structure gene from a mesh and the manifest's material blocks.

    Parameters
    ----------
    mesh : SGMesh
        Mesh read from the model file; restricted in place to section elements.
    sgdim : int
        SG dimension.
    model_type : str
        Macro model type.
    data : dict
        Manifest data holding ``materials`` and ``sections``.

    Returns
    -------
    StructureGene
        Structure gene whose sections reference the declared materials.
    """
    for key in ('materials', 'sections'):
        if key not in data:
            raise IncompleteModelDataError(
                f"The model file carries mesh data only; the SG manifest needs '{key}'."
            )
    materials = read_materials(data['materials'])
    sections = read_sections(data['sections'], materials)

    sg = mesh_to_sg(
        mesh, sgdim=sgdim, model_type=model_type,
        section_names={s['name'] for s in sections if s.get('name') is not None},
        section_ids={int(s['id']) for s in sections if s.get('id') is not None},
    )
    for name, material in materials.items():
        sg.materials[name] = material
    _bind_sections(sg, sections)
    return sg


def _bind_sections(sg: StructureGene, sections: list[dict]) -> None:
    """Set material and layup angle of each mesh section from its record."""
    by_name = {s['name']: s for s in sections if s.get('name') is not None}
    by_id = {int(s['id']): s for s in sections if s.get('id') is not None}
    name_by_tag = {int(values[0]): name for name, values in sg.mesh.field_data.items()}

    for section in sg.sections.values():
        tag = int(section.property_id)
        record = by_name.get(name_by_tag.get(tag))
        source = 'name'
        if record is None:
            record, source = by_id.get(tag), 'id'
        section.material = record['material']
        section.orientation = float(record.get('orientation', 0.0))
        section.extras['section_match_source'] = source


def materials_to_records(sg: StructureGene) -> list[dict]:
    """Serialize the structure gene's materials into the ``materials`` block."""
    return [
        {**serialize_material_record(material), 'name': name}
        for name, material in sg.materials.items()
    ]


def sections_to_records(sg: StructureGene) -> list[dict]:
    """Serialize the structure gene's sections into the ``sections`` block."""
    name_by_tag = {int(values[0]): name for name, values in sg.mesh.field_data.items()}
    records = []
    for section in sorted(sg.sections.values(), key=lambda s: s.property_id):
        tag = int(section.property_id)
        record: dict[str, Any] = {'id': tag}
        if tag in name_by_tag:
            record = {'name': name_by_tag[tag], **record}
        record['material'] = section.material
        record['orientation'] = float(section.orientation)
        records.append(record)
    return records
