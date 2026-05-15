"""Backward-compatible VABS I/O entry points."""

from __future__ import annotations

import sgio.model as smdl
from sgio.core.sg import StructureGene

from .mapper_in import map_input_to_structure_gene
from .mapper_out import map_structure_gene_to_write_payload
from .output import read_output_buffer
from .parser import parse_input_buffer
from .writer import write_input_payload


def read_buffer(file, format_version: str) -> StructureGene:
    """Read a VABS input buffer into a ``StructureGene``."""
    parsed = parse_input_buffer(file, format_version=format_version)
    return map_input_to_structure_gene(parsed)


def write_buffer(
    sg: StructureGene,
    file,
    analysis: str = "h",
    sg_fmt: int = 1,
    model: int = 0,
    model_space: str = "",
    prop_ref_y: str = "x",
    macro_responses: list[smdl.StateCase] | None = None,
    sfi: str = "8d",
    sff: str = "20.12e",
    version: str | None = None,
    **kwargs,
):
    """Write a ``StructureGene`` to a VABS input buffer."""
    payload = map_structure_gene_to_write_payload(
        sg,
        analysis=analysis,
        sg_fmt=sg_fmt,
        model=model,
        model_space=model_space,
        prop_ref_y=prop_ref_y,
        macro_responses=macro_responses,
        sfi=sfi,
        sff=sff,
        version=version,
    )
    write_input_payload(file, payload)


def writeInputBuffer(
    sg: StructureGene,
    file,
    analysis,
    timoshenko_flag,
    vlasov_flag,
    trapeze_flag,
    thermal_flag,
    model_space: str = "",
    prop_ref_y: str = "x",
    sg_fmt: int = 1,
    sfi: str = "8d",
    sff: str = "20.12e",
    version: str | None = None,
):
    """Backward-compatible wrapper for legacy VABS homogenization writing."""
    payload = map_structure_gene_to_write_payload(
        sg,
        analysis=analysis,
        sg_fmt=sg_fmt,
        model=timoshenko_flag,
        model_space=model_space,
        prop_ref_y=prop_ref_y,
        sfi=sfi,
        sff=sff,
        version=version,
    )
    header = payload["header"]
    header["timoshenko_flag"] = timoshenko_flag
    header["vlasov_flag"] = vlasov_flag
    header["trapeze_flag"] = trapeze_flag
    header["thermal_flag"] = thermal_flag
    write_input_payload(file, payload)


def writeInputBufferGlobal(
    file,
    model,
    analysis,
    macro_responses: list[smdl.StateCase] | None = None,
    dict_materials=None,
    sfi: str = "8d",
    sff: str = "20.12e",
):
    """Backward-compatible wrapper for legacy VABS global-response writing."""
    payload = {
        "mode": "global",
        "analysis": analysis,
        "model": model,
        "macro_responses": [] if macro_responses is None else macro_responses,
        "materials": {} if dict_materials is None else dict_materials,
        "sfi": sfi,
        "sff": sff,
    }
    write_input_payload(file, payload)
