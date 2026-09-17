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


