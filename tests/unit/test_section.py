"""Tests for FE sections and mocombos compatibility view."""

from __future__ import annotations

import pytest

import sgio
from sgio.core import Orientation, Section


@pytest.mark.unit
def test_section_and_orientation_are_independently_usable():
    """Section and Orientation should work as standalone FE objects."""
    orientation = Orientation(name="ori45", angle=45.0)
    section = Section(
        name="sec1",
        material="mat1",
        orientation=45.0,
        property_id=3,
    )

    assert orientation.name == "ori45"
    assert orientation.angle == 45.0
    assert section.name == "sec1"
    assert section.material == "mat1"
    assert section.orientation == 45.0
    assert section.property_id == 3


@pytest.mark.unit
def test_structure_gene_sections_are_primary_storage_for_mocombos():
    """Sections should drive the legacy mocombos view."""
    sg = sgio.StructureGene()

    section = sg.add_section(
        name="skin",
        material="cfrp",
        orientation=30.0,
        property_id=7,
    )

    assert isinstance(section, Section)
    assert sg.sections["skin"].property_id == 7
    assert dict(sg.mocombos.items()) == {7: ("cfrp", 30.0)}


@pytest.mark.unit
def test_mocombos_view_supports_legacy_mutation():
    """Legacy mocombos writes should update the backing sections."""
    sg = sgio.StructureGene()

    sg.mocombos[2] = ("glass", -45.0)

    assert sg.mocombos[2] == ("glass", -45.0)
    assert sg.sections["section_2"].material == "glass"
    assert sg.sections["section_2"].orientation == -45.0
    assert sg.sections["section_2"].property_id == 2


@pytest.mark.unit
def test_setting_mocombos_rebuilds_sections():
    """Assigning the legacy mocombos mapping should rebuild sections."""
    sg = sgio.StructureGene()
    sg.mocombos = {3: ("core", 0.0), 8: ("skin", 90.0)}

    assert sorted(sg.sections) == ["section_3", "section_8"]
    assert dict(sg.mocombos.items()) == {3: ("core", 0.0), 8: ("skin", 90.0)}
