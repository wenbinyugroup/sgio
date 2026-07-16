"""Phase 2 regression tests for VABS solver-id provenance round-trip.

These lock the core acceptance criterion of
``plan-20260715-solver-id-provenance.md``: reading a VABS file and writing it
back to VABS preserves the material id numbering even when the in-memory
material order no longer matches the file's id order (the "shuffled label"
case that positional numbering cannot reproduce).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import sgio

_FIXTURE = Path("tests/fixtures/vabs/version_4_0/sg21t_tri3_vabs40.sg")


@pytest.mark.conversion
@pytest.mark.vabs
def test_vabs_reader_captures_material_source_ids():
    """The VABS reader should record each material's source id as provenance."""
    sg = sgio.read(str(_FIXTURE), "vabs", format_version="4.0", model_type="BM2")

    provenance = dict(sg.fe_model.material_source_ids)
    assert provenance == {
        "Material_1": {"vabs": 1},
        "Material_2": {"vabs": 2},
        "Material_3": {"vabs": 3},
        "Material_4": {"vabs": 4},
    }
    # Combo/section provenance mirrors the property id for the same format.
    for section in sg.sections.values():
        assert section.source_ids["vabs"] == section.property_id


@pytest.mark.conversion
@pytest.mark.vabs
def test_vabs_write_preserves_material_ids_under_shuffled_order(tmp_path: Path):
    """Shuffled in-memory material order must not change exported material ids.

    Reversing the materials dict order while keeping provenance intact is a
    non-identity permutation: positional numbering would relabel every material
    (Material_4 -> id 1), whereas prefer-then-fill keeps Material_k -> id k.
    """
    source_sg = sgio.read(str(_FIXTURE), "vabs", format_version="4.0", model_type="BM2")

    # Original elastic payload keyed by material name (the ground-truth identity).
    original_stff = {
        name: np.asarray(material.model_dump()["stff"], dtype=float)
        for name, material in source_sg.materials.items()
    }

    # Simulate a file whose material definition order differs from id order by
    # reversing the dict; provenance (keyed by name) is unaffected.
    reversed_names = list(reversed(list(source_sg.fe_model.materials)))
    source_sg.fe_model.materials = {
        name: source_sg.fe_model.materials[name] for name in reversed_names
    }

    out_path = tmp_path / "reexport.sg"
    # model_space only affects node projection, not material numbering, which is
    # what this test locks.
    sgio.write(
        source_sg,
        str(out_path),
        "vabs",
        format_version="4.0",
        model_type="BM2",
        model_space="yz",
    )

    reread = sgio.read(str(out_path), "vabs", format_version="4.0", model_type="BM2")

    # Names are id-derived on read, so identity is preserved only if each
    # material was written back at its original id. With positional numbering
    # the reversed order would place Material_4's payload at id 1.
    for name, stff in original_stff.items():
        np.testing.assert_allclose(
            np.asarray(reread.materials[name].model_dump()["stff"], dtype=float),
            stff,
            err_msg=f"material id for {name} was not preserved across re-export",
        )
    assert dict(reread.fe_model.material_source_ids) == {
        "Material_1": {"vabs": 1},
        "Material_2": {"vabs": 2},
        "Material_3": {"vabs": 3},
        "Material_4": {"vabs": 4},
    }
