from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..._global import FAILURE_CRITERION_NAME_TO_ID
from ...model.solid import CauchyContinuumModel

_FAILURE_CRITERION_ID_TO_NAME = {
    1: "max_principal_stress",
    2: "max_principal_strain",
    3: "tsai-hill",
    4: "tsai-wu",
    5: "hashin",
}


def write_material_to_json(
    material: CauchyContinuumModel,
    file_path: str,
    *,
    exclude_none: bool = True,
    indent: int | None = None,
) -> None:
    """Write one material to JSON using the standard section/material record schema.

    Parameters
    ----------
    material : CauchyContinuumModel
        Material model to serialize.
    file_path : str
        Target JSON file path.
    exclude_none : bool, optional
        If ``True``, omit fields whose value is ``None``.
    indent : int or None, optional
        JSON indentation passed to :func:`json.dump`.
    """

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [serialize_material_record(material, exclude_none=exclude_none)]

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=indent, ensure_ascii=False)


def read_material_from_json(file_path: str) -> dict[str, CauchyContinuumModel]:
    """Read one material definition from JSON.

    Parameters
    ----------
    file_path : str
        JSON file path.

    Returns
    -------
    dict[str, CauchyContinuumModel]
        Dictionary keyed by material name.
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    material_records = _extract_material_records(data, source=file_path, allow_single_dict=True)
    if len(material_records) != 1:
        raise ValueError(
            f"Expected exactly one material in {file_path}, found {len(material_records)}."
        )
    material = deserialize_material_record(material_records[0])
    if not material.name:
        raise ValueError("Material must have a non-empty name field")
    return {material.name: material}


def read_materials_from_json(file_path: str) -> dict[str, CauchyContinuumModel]:
    """Read material definitions from JSON.

    Parameters
    ----------
    file_path : str
        JSON file path.

    Returns
    -------
    dict[str, CauchyContinuumModel]
        Dictionary keyed by material name.
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    material_records = _extract_material_records(data, source=file_path, allow_single_dict=False)

    materials: dict[str, CauchyContinuumModel] = {}
    for index, mat_data in enumerate(material_records):
        material = deserialize_material_record(mat_data)
        if not material.name:
            raise ValueError(f"Material at index {index} must have a non-empty name field")
        if material.name in materials:
            raise ValueError(f"Duplicate material name found: {material.name}")
        materials[material.name] = material

    return materials


def serialize_material_record(
    material: CauchyContinuumModel,
    *,
    exclude_none: bool = True,
) -> dict[str, Any]:
    """Serialize one material using the standard grouped record schema.

    Parameters
    ----------
    material : CauchyContinuumModel
        Material model to serialize.
    exclude_none : bool, optional
        If ``True``, omit fields whose value is ``None``.

    Returns
    -------
    dict[str, Any]
        JSON-ready material record.
    """

    record: dict[str, Any] = {
        "name": material.name,
        "model": material.label,
        "isotropy": material.isotropy,
        "density": material.density,
        "temperature": material.temperature,
    }

    if material.id is not None:
        record["label"] = str(material.id)

    elastic = _build_elastic_record(material, exclude_none=exclude_none)
    strength = _build_strength_record(material, exclude_none=exclude_none)
    if elastic or not exclude_none:
        record["elastic"] = elastic
    if strength or not exclude_none:
        record["strength"] = strength

    if not exclude_none or material.strength_measure != 0:
        record["strength_measure"] = material.strength_measure
    failure_criterion = _serialize_failure_criterion(material.failure_criterion)
    if failure_criterion is not None or not exclude_none:
        record["failure_criterion"] = failure_criterion
    if not exclude_none or material.char_len != 0:
        record["char_len"] = material.char_len
    if material.strength_constants is not None or not exclude_none:
        record["strength_constants"] = material.strength_constants
    if material.cte is not None or not exclude_none:
        record["cte"] = material.cte
    if not exclude_none or material.specific_heat != 0:
        record["specific_heat"] = material.specific_heat
    if not exclude_none or material.d_thetatheta != 0:
        record["d_thetatheta"] = material.d_thetatheta
    if not exclude_none or material.f_eff != 0:
        record["f_eff"] = material.f_eff

    return record


def deserialize_material_record(record: dict[str, Any]) -> CauchyContinuumModel:
    """Deserialize one standard grouped material record.

    Parameters
    ----------
    record : dict[str, Any]
        Material record data.

    Returns
    -------
    CauchyContinuumModel
        Material model instance.
    """

    if not isinstance(record, dict):
        raise TypeError(f"Expected material record to be a dictionary, got {type(record).__name__}")

    payload = dict(record)
    payload.pop("model", None)

    raw_label = payload.pop("label", None)
    if payload.get("id") is None and raw_label not in (None, ""):
        payload["id"] = _coerce_material_id(raw_label)

    elastic = payload.pop("elastic", None)
    if elastic is not None:
        if not isinstance(elastic, dict):
            raise TypeError("Material field 'elastic' must be a dictionary.")
        payload.update(elastic)

    strength = payload.pop("strength", None)
    if strength is not None:
        if not isinstance(strength, dict):
            raise TypeError("Material field 'strength' must be a dictionary.")
        payload.update(strength)

    payload["failure_criterion"] = _deserialize_failure_criterion(
        payload.get("failure_criterion", 0)
    )

    return CauchyContinuumModel(**payload)


def _extract_material_records(
    data: Any,
    *,
    source: str,
    allow_single_dict: bool,
) -> list[dict[str, Any]]:
    """Normalize supported JSON organizations into a list of material records."""

    if isinstance(data, dict):
        if "sections" in data:
            sections = data["sections"]
            if not isinstance(sections, list):
                raise TypeError("sections.json field 'sections' must be a list.")
            records = []
            for index, section in enumerate(sections):
                if not isinstance(section, dict):
                    raise TypeError(
                        f"Section record at index {index} is not a dictionary: "
                        f"{type(section).__name__}"
                    )
                if "payload" in section:
                    kind = section.get("kind")
                    theory = section.get("theory")
                    if kind not in {"material", "solid"} or theory != "cauchy_continuum":
                        continue
                    payload = section["payload"]
                    if not isinstance(payload, dict):
                        raise TypeError(
                            f"Payload at section index {index} is not a dictionary: "
                            f"{type(payload).__name__}"
                        )
                    merged_payload = dict(payload)
                    if section.get("name") not in (None, "") and not merged_payload.get("name"):
                        merged_payload["name"] = section["name"]
                    if section.get("id") is not None and "label" not in merged_payload:
                        merged_payload["label"] = str(section["id"])
                    records.append(merged_payload)
                else:
                    records.append(section)
            return records
        if allow_single_dict and _looks_like_material_record(data):
            return [data]
        expected = "dictionary or list" if allow_single_dict else "list"
        raise TypeError(
            f"Expected JSON {expected} for material records in {source}, "
            f"got unsupported dictionary shape."
        )

    if isinstance(data, list):
        records: list[dict[str, Any]] = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise TypeError(
                    f"Material at index {index} is not a dictionary: {type(item).__name__}"
                )
            records.append(item)
        return records

    raise TypeError(
        f"Expected JSON {'dictionary or list' if allow_single_dict else 'list'} for "
        f"material records in {source}, "
        f"got {type(data).__name__}"
    )


def _looks_like_material_record(record: dict[str, Any]) -> bool:
    """Return whether one dictionary looks like a material record."""

    return bool(
        {"name", "elastic", "strength", "isotropy", "e", "e1", "stff", "cmpl"} & set(record)
    )


def _build_elastic_record(
    material: CauchyContinuumModel,
    *,
    exclude_none: bool,
) -> dict[str, Any]:
    """Build the grouped linear-elastic sub-record."""

    elastic: dict[str, Any] = {}
    for field_name in ("e1", "e2", "e3", "g12", "g13", "g23", "nu12", "nu13", "nu23"):
        value = getattr(material, field_name)
        if value is not None or not exclude_none:
            elastic[field_name] = value

    has_engineering_constants = any(
        elastic.get(field_name) is not None
        for field_name in ("e1", "e2", "e3", "g12", "g13", "g23", "nu12", "nu13", "nu23")
    )

    if (not has_engineering_constants and material.stff is not None) or not exclude_none:
        elastic["stff"] = material.stff
    if (
        not has_engineering_constants
        and material.stff is None
        and material.cmpl is not None
    ) or not exclude_none:
        elastic["cmpl"] = material.cmpl
    return elastic


def _build_strength_record(
    material: CauchyContinuumModel,
    *,
    exclude_none: bool,
) -> dict[str, Any]:
    """Build the grouped strength sub-record."""

    strength: dict[str, Any] = {}
    for field_name in ("x1t", "x2t", "x3t", "x1c", "x2c", "x3c", "x23", "x13", "x12"):
        value = getattr(material, field_name)
        if value is not None or not exclude_none:
            strength[field_name] = value
    return strength


def _coerce_material_id(value: Any) -> int | None:
    """Convert one optional external label token into an integer material id."""

    if value in (None, ""):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(stripped)
        except ValueError:
            return None
    return None


def _serialize_failure_criterion(value: int) -> str | int | None:
    """Serialize one failure-criterion identifier to its canonical JSON token."""

    if value == 0:
        return None
    return _FAILURE_CRITERION_ID_TO_NAME.get(value, value)


def _deserialize_failure_criterion(value: Any) -> int:
    """Normalize one failure-criterion JSON token into the internal integer form."""

    if value in (None, "", 0):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower().replace(" ", "_")
        if not normalized:
            return 0
        try:
            return int(normalized)
        except ValueError:
            pass
        if normalized not in FAILURE_CRITERION_NAME_TO_ID:
            raise ValueError(f"Unsupported failure criterion token: {value!r}")
        return FAILURE_CRITERION_NAME_TO_ID[normalized]
    raise TypeError(
        f"Failure criterion must be int, str, or null, got {type(value).__name__}"
    )


__all__ = [
    "deserialize_material_record",
    "read_material_from_json",
    "read_materials_from_json",
    "serialize_material_record",
    "write_material_to_json",
]
