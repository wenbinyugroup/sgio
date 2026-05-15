"""VABS writer layer.

This module is responsible only for turning raw VABS write payloads into text.
"""

from __future__ import annotations

from typing import Any, Mapping, TextIO

from ._input import (
    _writeGlobalResponses,
    _writeHeader,
    _writeMaterials,
    _writeMesh,
)
from .keywords import COMMENT_CHAR


def write_input_payload(file: TextIO, payload: Mapping[str, Any]) -> None:
    """Write a raw VABS payload to a text buffer."""
    if payload["mode"] == "homogenization":
        _write_homogenization_payload(file, payload)
        return

    if payload["mode"] == "global":
        _write_global_payload(file, payload)
        return

    raise ValueError(f"Unsupported VABS writer payload mode: {payload['mode']}")


def _write_homogenization_payload(file: TextIO, payload: Mapping[str, Any]) -> None:
    """Write a homogenization VABS payload."""
    header = payload["header"]
    _writeHeader(
        header["format_flag"],
        header["nlayer"],
        header["timoshenko_flag"],
        header["damping_flag"],
        header["thermal_flag"],
        header["curve_flag"],
        header["oblique_flag"],
        header["trapeze_flag"],
        header["vlasov_flag"],
        header["initial_curvatures"],
        header["obliqueness"],
        header["nnode"],
        header["nelem"],
        header["nmate"],
        file,
        payload["sfi"],
        payload["sff"],
    )

    _writeMesh(
        payload["mesh"],
        file,
        model_space=payload["model_space"],
        prop_ref_y=payload["prop_ref_y"],
        int_fmt=payload["sfi"],
        float_fmt=payload["sff"],
    )
    _write_material_combo_records(
        file,
        payload["material_combos"],
        sfi=payload["sfi"],
        sff=payload["sff"],
    )
    _writeMaterials(
        dict_materials=payload["materials"],
        file=file,
        analysis="h",
        thermal_flag=header["thermal_flag"],
        sfi=payload["sfi"],
        sff=payload["sff"],
        mat_id_map=payload["material_id_map"],
    )


def _write_global_payload(file: TextIO, payload: Mapping[str, Any]) -> None:
    """Write a global-response VABS payload."""
    if payload["analysis"].startswith("f"):
        mat_id_map = {
            name: idx + 1 for idx, name in enumerate(payload["materials"].keys())
        }
        _writeMaterials(
            payload["materials"],
            file,
            analysis="f",
            sfi=payload["sfi"],
            sff=payload["sff"],
            mat_id_map=mat_id_map,
        )

    _writeGlobalResponses(
        file,
        payload["macro_responses"],
        payload["model"],
        payload["sff"],
    )


def _write_material_combo_records(
    file: TextIO,
    records: list[Mapping[str, float | int]],
    sfi: str = "8d",
    sff: str = "20.12e",
) -> None:
    """Write raw VABS material-orientation combination records."""
    int_fmt = "{:" + sfi + "}"
    float_fmt = "{:" + sff + "}"

    for index, record in enumerate(records):
        file.write(
            (int_fmt + int_fmt + float_fmt).format(
                int(record["combo_id"]),
                int(record["material_id"]),
                float(record["angle"]),
            )
        )
        if index == 0:
            file.write(
                f"  {COMMENT_CHAR} combination id, material id, in-plane rotation angle"
            )
        file.write("\n")
    file.write("\n")
