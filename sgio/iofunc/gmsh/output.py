"""Gmsh output helpers."""

from __future__ import annotations


def read_output_buffer(*args, **kwargs):
    """Gmsh has no SG analysis-output reader in SGIO."""
    raise NotImplementedError("Gmsh output reading is not applicable")
