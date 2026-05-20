"""Backward-compatible Abaqus I/O entry points."""

from __future__ import annotations

from .mapper_in import map_input_to_structure_gene
from .parser import parse_input_file


def read(filename: str, **kwargs):
    """Read an Abaqus input file into a ``StructureGene``."""
    parsed = parse_input_file(filename, **kwargs)
    return map_input_to_structure_gene(parsed)
