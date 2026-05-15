"""Abaqus output helpers."""

from __future__ import annotations


def read_output_buffer(*args, **kwargs):
    """Abaqus output reading is not implemented in SGIO."""
    raise NotImplementedError("Abaqus output reading is handled by Abaqus")
