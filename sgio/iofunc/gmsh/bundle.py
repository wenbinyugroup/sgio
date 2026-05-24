from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from sgio.core import SGAnalysisConfig, StructureGene
from sgio.iofunc._mesh_convert import mesh_to_sg, restore_sg_from_mesh_extras
from sgio.iofunc.common.material_json import (
    deserialize_material_record,
    serialize_material_record,
)
from sgio.model import (
    CauchyContinuumModel,
    EulerBernoulliBeamModel,
    KirchhoffLovePlateShellModel,
    ReissnerMindlinPlateShellModel,
    TimoshenkoBeamModel,
)

from ._gmsh import read_buffer as read_gmsh_buffer

MATERIAL_KIND = "material"
SOLID_KIND = "solid"
BEAM_KIND = "beam"
SHELL_KIND = "shell"

CAUCHY_THEORY = "cauchy_continuum"
EULER_BERNOULLI_THEORY = "euler_bernoulli_beam"
TIMOSHENKO_THEORY = "timoshenko_beam"
KIRCHHOFF_LOVE_THEORY = "kirchhoff_love_shell"
REISSNER_MINDLIN_THEORY = "reissner_mindlin_shell"


@dataclass
class SectionSidecarRecord:
    """One `sections.json` record."""

    kind: str
    theory: str
    payload: object
    name: str | None = None
    id: int | None = None
    material: str | None = None
    orientation: float | None = None


_THEORY_TO_CLASS = {
    (MATERIAL_KIND, CAUCHY_THEORY): CauchyContinuumModel,
    (SOLID_KIND, CAUCHY_THEORY): CauchyContinuumModel,
    (BEAM_KIND, EULER_BERNOULLI_THEORY): EulerBernoulliBeamModel,
    (BEAM_KIND, TIMOSHENKO_THEORY): TimoshenkoBeamModel,
    (SHELL_KIND, KIRCHHOFF_LOVE_THEORY): KirchhoffLovePlateShellModel,
    (SHELL_KIND, REISSNER_MINDLIN_THEORY): ReissnerMindlinPlateShellModel,
}

_CLASS_TO_DESCRIPTOR = {
    CauchyContinuumModel: (MATERIAL_KIND, CAUCHY_THEORY),
    EulerBernoulliBeamModel: (BEAM_KIND, EULER_BERNOULLI_THEORY),
    TimoshenkoBeamModel: (BEAM_KIND, TIMOSHENKO_THEORY),
    KirchhoffLovePlateShellModel: (SHELL_KIND, KIRCHHOFF_LOVE_THEORY),
    ReissnerMindlinPlateShellModel: (SHELL_KIND, REISSNER_MINDLIN_THEORY),
}


def section_model_to_record(
    model: object,
    *,
    kind: str | None = None,
    theory: str | None = None,
    name: str | None = None,
    id: int | None = None,
    material: str | None = None,
    orientation: float | None = None,
) -> dict[str, Any]:
    """Serialize one section/material model into the `sections.json` record format."""
    resolved_kind, resolved_theory = _infer_record_descriptor(model, kind=kind, theory=theory)
    payload = _serialize_model_payload(model)
    resolved_name = name if name is not None else getattr(model, "name", None)
    resolved_id = id if id is not None else getattr(model, "id", None)

    record: dict[str, Any] = {
        "kind": resolved_kind,
        "theory": resolved_theory,
        "payload": payload,
    }
    if resolved_name not in (None, ""):
        record["name"] = resolved_name
    if resolved_id is not None:
        record["id"] = int(resolved_id)
    if material is not None:
        record["material"] = material
    if orientation is not None:
        record["orientation"] = float(orientation)
    return record


def write_sections_to_json(
    records: Sequence[Mapping[str, Any] | object],
    file_path: str | Path,
    *,
    indent: int = 2,
) -> str:
    """Write `sections.json` using the Phase 3 organization layer."""
    serialized_records = []
    for record in records:
        if isinstance(record, Mapping):
            serialized_records.append(dict(record))
        else:
            serialized_records.append(section_model_to_record(record))

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump({"sections": serialized_records}, file, indent=indent, ensure_ascii=False)
    return str(path)


def read_sections_from_json(file_path: str | Path) -> list[SectionSidecarRecord]:
    """Read and deserialize `sections.json`."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    raw_records = _normalize_section_records(data)

    records: list[SectionSidecarRecord] = []
    for index, raw_record in enumerate(raw_records):
        if not isinstance(raw_record, dict):
            raise TypeError(
                f"sections.json record at index {index} must be a dictionary, "
                f"got {type(raw_record).__name__}."
            )
        if "payload" in raw_record:
            kind = raw_record.get("kind")
            theory = raw_record.get("theory")
            payload_data = raw_record.get("payload")
            if not isinstance(kind, str) or not isinstance(theory, str):
                raise ValueError(
                    f"sections.json record at index {index} must define string kind/theory."
                )
            if not isinstance(payload_data, dict):
                raise TypeError(
                    f"sections.json record at index {index} must define payload as a dictionary."
                )
            payload = _deserialize_model_payload(kind, theory, payload_data)
            records.append(
                SectionSidecarRecord(
                    kind=kind,
                    theory=theory,
                    payload=payload,
                    name=raw_record.get("name"),
                    id=int(raw_record["id"]) if raw_record.get("id") is not None else None,
                    material=raw_record.get("material"),
                    orientation=(
                        float(raw_record["orientation"])
                        if raw_record.get("orientation") is not None
                        else None
                    ),
                )
            )
            continue

        payload = deserialize_material_record(raw_record)
        records.append(
            SectionSidecarRecord(
                kind=MATERIAL_KIND,
                theory=CAUCHY_THEORY,
                payload=payload,
                name=payload.name or None,
                id=payload.id,
            )
        )

    return records


def write_config_to_json(
    config: SGAnalysisConfig,
    file_path: str | Path,
    *,
    indent: int = 2,
) -> str:
    """Write `config.json`."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(asdict(config), file, indent=indent, ensure_ascii=False)
    return str(path)


def read_config_from_json(file_path: str | Path) -> SGAnalysisConfig:
    """Read `config.json`."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise TypeError("config.json must be a dictionary.")

    if "config" in data:
        if not isinstance(data["config"], dict):
            raise TypeError("config.json field 'config' must be a dictionary.")
        return SGAnalysisConfig(**data["config"])

    return SGAnalysisConfig(**data)


def read_sg_from_gmsh_bundle(
    main_msh: str | Path,
    sections_json: str | Path | None = None,
    config_json: str | Path | None = None,
    *,
    model_type: str | None = None,
    format_version: str = "4.1",
) -> StructureGene:
    """Assemble one `StructureGene` from `main.msh + sections.json + config.json`."""
    with open(main_msh, "rb") as file:
        mesh = read_gmsh_buffer(file, format_version=format_version)

    sgdim = int(mesh.cells[0].dim) if mesh.cells else 2
    resolved_model_type = model_type or _default_model_type_for_sgdim(sgdim)
    sg = mesh_to_sg(mesh, sgdim=sgdim, model_type=resolved_model_type)
    restore_sg_from_mesh_extras(sg, mesh)

    if config_json is not None:
        sg.analysis_config = read_config_from_json(config_json)

    records = read_sections_from_json(sections_json) if sections_json is not None else []
    if records:
        _apply_section_records_to_sg(sg, records)
        bundle_extras = sg.extras.setdefault("gmsh_bundle", {})
        bundle_extras["sections_records"] = [
            {
                "kind": record.kind,
                "theory": record.theory,
                "name": record.name,
                "id": record.id,
                "material": record.material,
                "orientation": record.orientation,
            }
            for record in records
        ]
        bundle_extras["section_models"] = {
            _record_storage_key(record): record.payload for record in records
        }

    if config_json is not None:
        sg.extras.setdefault("gmsh_bundle", {})["config"] = asdict(sg.analysis_config)

    return sg


def _apply_section_records_to_sg(sg: StructureGene, records: Sequence[SectionSidecarRecord]) -> None:
    """Attach sidecar section/material records to one structure gene."""
    name_index: dict[str, SectionSidecarRecord] = {}
    id_index: dict[int, SectionSidecarRecord] = {}
    for record in records:
        if record.name:
            if record.name in name_index:
                raise ValueError(f"Duplicate section sidecar name detected: {record.name}")
            name_index[record.name] = record
        if record.id is not None:
            if record.id in id_index:
                raise ValueError(f"Duplicate section sidecar id detected: {record.id}")
            id_index[record.id] = record

    for record in records:
        if isinstance(record.payload, CauchyContinuumModel) and record.name:
            sg.materials[record.name] = record.payload

    physical_name_by_id = _build_physical_name_by_id(sg)
    for section in sg.sections.values():
        property_id = int(section.property_id) if section.property_id is not None else None
        physical_name = (
            physical_name_by_id.get(property_id) if property_id is not None else None
        )

        matched_record = None
        if physical_name and physical_name in name_index:
            matched_record = name_index[physical_name]
        elif property_id is not None and property_id in id_index:
            matched_record = id_index[property_id]

        if matched_record is None:
            continue

        if isinstance(matched_record.payload, CauchyContinuumModel) and matched_record.name:
            section.material = matched_record.name

        if matched_record.material:
            section.material = matched_record.material
        if matched_record.orientation is not None:
            section.orientation = float(matched_record.orientation)

        section.extras["bundle_section_kind"] = matched_record.kind
        section.extras["bundle_section_theory"] = matched_record.theory
        section.extras["bundle_section_name"] = matched_record.name
        section.extras["bundle_section_id"] = matched_record.id
        section.extras["bundle_match_source"] = (
            "name" if physical_name and matched_record.name == physical_name else "id"
        )


def _build_physical_name_by_id(sg: StructureGene) -> dict[int, str]:
    """Build one physical-name lookup table from mesh field data."""
    physical_name_by_id: dict[int, str] = {}
    for name, values in getattr(sg.mesh, "field_data", {}).items():
        physical_id = int(values[0])
        physical_dim = int(values[1])
        if physical_dim == int(sg.sgdim):
            physical_name_by_id[physical_id] = name
    return physical_name_by_id


def _infer_record_descriptor(
    model: object,
    *,
    kind: str | None,
    theory: str | None,
) -> tuple[str, str]:
    """Infer the `(kind, theory)` pair for one supported sidecar model."""
    if kind is not None and theory is not None:
        return kind, theory

    for cls, descriptor in _CLASS_TO_DESCRIPTOR.items():
        if isinstance(model, cls):
            inferred_kind, inferred_theory = descriptor
            return kind or inferred_kind, theory or inferred_theory

    raise TypeError(f"Unsupported section sidecar model type: {type(model).__name__}")


def _serialize_model_payload(model: object) -> dict[str, Any]:
    """Serialize one supported model object to plain JSON-ready data."""
    if isinstance(model, CauchyContinuumModel):
        return serialize_material_record(model)

    if hasattr(model, "model_dump"):
        return dict(model.model_dump(exclude_none=True))

    payload = {
        key: value
        for key, value in vars(model).items()
        if not key.startswith("_") and value is not None
    }
    return payload


def _deserialize_model_payload(kind: str, theory: str, payload_data: Mapping[str, Any]) -> object:
    """Deserialize one sidecar payload to the corresponding Python model."""
    if (kind, theory) in {
        (MATERIAL_KIND, CAUCHY_THEORY),
        (SOLID_KIND, CAUCHY_THEORY),
    }:
        return deserialize_material_record(dict(payload_data))

    try:
        cls = _THEORY_TO_CLASS[(kind, theory)]
    except KeyError as exc:
        raise ValueError(f"Unsupported section sidecar descriptor: kind={kind!r}, theory={theory!r}") from exc

    if hasattr(cls, "model_validate"):
        return cls.model_validate(dict(payload_data))

    try:
        obj = cls()
    except NotImplementedError:
        obj = cls.__new__(cls)

    for key, value in payload_data.items():
        setattr(obj, key, value)
    return obj


def _record_storage_key(record: SectionSidecarRecord) -> str:
    """Build one stable storage key for bundle extras."""
    if record.name:
        return record.name
    if record.id is not None:
        return f"{record.kind}:{record.id}"
    return f"{record.kind}:{record.theory}"


def _normalize_section_records(data: Any) -> list[Any]:
    """Normalize supported `sections.json` top-level organizations."""

    if isinstance(data, dict):
        if "sections" not in data:
            raise TypeError("sections.json must contain a 'sections' list or be a top-level list.")
        if not isinstance(data["sections"], list):
            raise TypeError("sections.json field 'sections' must be a list.")
        return data["sections"]

    if isinstance(data, list):
        return data

    raise TypeError(
        "sections.json must be a dictionary containing a 'sections' list or a top-level list."
    )


def _default_model_type_for_sgdim(sgdim: int) -> str:
    """Return a conservative default model type for one SG dimension."""
    if sgdim == 1:
        return "BM1"
    if sgdim == 2:
        return "PL1"
    return "SD1"


__all__ = [
    "SectionSidecarRecord",
    "read_config_from_json",
    "read_sections_from_json",
    "read_sg_from_gmsh_bundle",
    "section_model_to_record",
    "write_config_to_json",
    "write_sections_to_json",
]
