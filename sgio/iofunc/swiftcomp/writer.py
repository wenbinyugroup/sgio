"""SwiftComp writer layer."""

from __future__ import annotations

from typing import Any, Mapping, TextIO

import sgio.utils as sutl

from ._input import (
    _writeDisplacementRotation,
    _writeHeader,
    _writeLoad,
    _writeMaterials,
    _writeMesh,
)
from .keywords import COMMENT_CHAR


def write_input_payload(file: TextIO, payload: Mapping[str, Any]) -> None:
    """Write a raw SwiftComp payload to a text buffer."""
    if payload["mode"] == "homogenization":
        _write_homogenization_payload(file, payload)
        return

    if payload["mode"] == "global":
        _write_global_payload(file, payload)
        return

    raise ValueError(f"Unsupported SwiftComp writer payload mode: {payload['mode']}")


def _write_homogenization_payload(file: TextIO, payload: Mapping[str, Any]) -> None:
    """Write a homogenization SwiftComp payload."""
    sg = payload["sg"]
    sg.version = payload["version"]
    _writeHeader(
        sg=sg,
        file=file,
        sfi=payload["sfi"],
        sff=payload["sff"],
        version=payload["version"],
    )
    _writeMesh(
        mesh=sg.mesh,
        file=file,
        sgdim=sg.sgdim,
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
        physics=payload["physics"],
        sfi=payload["sfi"],
        sff=payload["sff"],
        mat_id_map=payload["material_id_map"],
    )
    file.write(("{:" + payload["sff"] + "}\n").format(payload["omega"]))


def _write_global_payload(file: TextIO, payload: Mapping[str, Any]) -> None:
    """Write a global-response SwiftComp payload."""
    analysis = payload["analysis"]
    if analysis in ("d", "l") and payload["macro_responses"]:
        response = payload["macro_responses"][0]
        displacement = [0, 0, 0] if response.displacement is None else response.displacement.data
        rotation = (
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            if response.rotation is None
            else response.rotation.data
        )
        _writeDisplacementRotation(
            file=file,
            displacement=displacement,
            rotation=rotation,
            sff=payload["sff"],
        )
    elif analysis.startswith("f"):
        mat_id_map = {
            name: idx + 1 for idx, name in enumerate(payload["materials"].keys())
        }
        _writeMaterials(
            dict_materials=payload["materials"],
            file=file,
            analysis=analysis,
            physics=payload["physics"],
            sfi=payload["sfi"],
            sff=payload["sff"],
            mat_id_map=mat_id_map,
        )

    sutl.writeFormatIntegers(file, [payload["load_type"]], payload["sfi"])

    if analysis != "f":
        for response in payload["macro_responses"]:
            _writeLoad(
                file=file,
                macro_response=response,
                model=payload["model"],
                sff=payload["sff"],
            )


def _write_material_combo_records(
    file: TextIO,
    records: list[Mapping[str, float | int]],
    sfi: str = "8d",
    sff: str = "20.12e",
) -> None:
    """Write raw SwiftComp material-orientation combination records."""
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
