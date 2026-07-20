"""Phase 3 regression tests for SwiftComp solver-id provenance round-trip.

Symmetric to ``test_vabs_provenance``: reading a SwiftComp file and writing it
back to SwiftComp preserves the material id numbering even when the in-memory
material order no longer matches the file's id order.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import sgio

_FIXTURE = Path("tests/fixtures/swiftcomp/sg23_tri6_sc21.sg")


@pytest.mark.conversion
def test_swiftcomp_reader_captures_material_source_ids():
    """The SwiftComp reader should record each material's source id."""
    sg = sgio.read(str(_FIXTURE), "swiftcomp", model_type="SD1")

    assert dict(sg.fe_model.material_source_ids) == {
        "Material_1": {"swiftcomp": 1},
        "Material_2": {"swiftcomp": 2},
    }
    for section in sg.sections.values():
        assert section.source_ids["swiftcomp"] == section.property_id


@pytest.mark.conversion
def test_swiftcomp_write_preserves_material_ids_under_shuffled_order(tmp_path: Path):
    """Shuffled in-memory material order must not change exported material ids."""
    source_sg = sgio.read(str(_FIXTURE), "swiftcomp", model_type="SD1")

    original_stff = {
        name: np.asarray(material.model_dump()["stff"], dtype=float)
        for name, material in source_sg.materials.items()
    }

    # Reverse the materials dict (non-identity permutation) while keeping the
    # name-keyed provenance intact.
    reversed_names = list(reversed(list(source_sg.fe_model.materials)))
    source_sg.fe_model.materials = {
        name: source_sg.fe_model.materials[name] for name in reversed_names
    }

    out_path = tmp_path / "reexport.sg"
    # model_space only affects node projection, not material numbering.
    sgio.write(
        source_sg, str(out_path), "swiftcomp", model_type="SD1", model_space="xy"
    )

    reread = sgio.read(str(out_path), "swiftcomp", model_type="SD1")

    # Identity survives only if each material was written back at its source id;
    # positional numbering under the reversed order would swap the two payloads.
    for name, stff in original_stff.items():
        np.testing.assert_allclose(
            np.asarray(reread.materials[name].model_dump()["stff"], dtype=float),
            stff,
            err_msg=f"material id for {name} was not preserved across re-export",
        )
    assert dict(reread.fe_model.material_source_ids) == {
        "Material_1": {"swiftcomp": 1},
        "Material_2": {"swiftcomp": 2},
    }
