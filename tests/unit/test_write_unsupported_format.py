"""Regression test: sgio.write() must fail fast for unregistered formats
instead of silently deferring to meshio."""

from __future__ import annotations

import numpy as np
import pytest

import sgio
from sgio.core.mesh import CellBlock, SGMesh


@pytest.mark.unit
def test_write_unsupported_format_raises_value_error(tmp_path):
    sg = sgio.StructureGene()
    sg.mesh = SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        cells=[CellBlock("triangle", np.array([[0, 1, 2]], dtype=int))],
    )

    with pytest.raises(ValueError, match="Unsupported output format"):
        sgio.write(sg, str(tmp_path / "out.stl"), file_format="stl")
