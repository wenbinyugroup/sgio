"""Deprecation coverage for legacy ``sgio.model`` compatibility APIs."""

from __future__ import annotations

import importlib
from io import StringIO

import pytest

from sgio.model.beam import EulerBernoulliBeamModel
from sgio.model.response import SectionResponse, StructureResponseCase, StructureResponseCases
from sgio.model.shell import KirchhoffLovePlateShellModel
from sgio.model.solid import (
    CauchyContinuumModel,
    read_material_from_json,
    read_materials_from_json,
)


@pytest.mark.unit
class TestModelDeprecations:
    """Test that legacy compatibility APIs advertise their retirement plan."""

    def test_general_module_import_warns(self):
        """Reloading the legacy general shell should emit a deprecation warning."""
        import sgio.model.general as general_module

        with pytest.warns(DeprecationWarning, match='sgio\\.model\\.general'):
            importlib.reload(general_module)

    def test_response_legacy_types_warn(self):
        """Legacy response containers should warn on construction."""
        with pytest.warns(DeprecationWarning, match='SectionResponse'):
            response = SectionResponse()

        with pytest.warns(DeprecationWarning, match='StructureResponseCase'):
            StructureResponseCase(response=response)

        with pytest.warns(DeprecationWarning, match='StructureResponseCases'):
            StructureResponseCases()

    def test_response_writer_wrappers_warn(self):
        """Legacy response writer methods should warn before delegating."""
        with pytest.warns(DeprecationWarning, match='SectionResponse'):
            response = SectionResponse()

        with pytest.warns(DeprecationWarning, match='writeSGInputGlbU'):
            response.writeSGInputGlbU(StringIO())

        with pytest.warns(DeprecationWarning, match='writeSGInputGlbC'):
            response.writeSGInputGlbC(StringIO())

        with pytest.warns(DeprecationWarning, match='writeSGInputGlbS'):
            response.writeSGInputGlbS(StringIO(), 'vabs')

    def test_solid_legacy_string_api_warns(self):
        """Legacy solid getters and setters should warn."""
        solid = CauchyContinuumModel(isotropy=0)

        with pytest.warns(DeprecationWarning, match='CauchyContinuumModel\\.set'):
            solid.set('isotropy', 'iso')

        with pytest.warns(DeprecationWarning, match='CauchyContinuumModel\\.setElastic'):
            solid.setElastic([210e9, 0.3], input_type='isotropic')

        with pytest.warns(DeprecationWarning, match='CauchyContinuumModel\\.get'):
            assert solid.get('e') == pytest.approx(210e9)

    def test_section_legacy_string_api_warns(self):
        """Legacy beam and shell string queries should warn."""
        beam = EulerBernoulliBeamModel(ea=2.0)
        shell = KirchhoffLovePlateShellModel()

        with pytest.warns(DeprecationWarning, match='EulerBernoulliBeamModel\\.get'):
            assert beam.get('ea') == pytest.approx(2.0)

        with pytest.warns(DeprecationWarning, match='KirchhoffLovePlateShellModel\\.get'):
            assert shell.get('stf11c') is None

    def test_material_json_wrappers_warn(self, steel_isotropic_path, multiple_materials_path, tmp_path):
        """Legacy material JSON wrappers should warn before delegating."""
        with pytest.warns(DeprecationWarning, match='read_material_from_json'):
            assert 'Steel' in read_material_from_json(steel_isotropic_path)

        with pytest.warns(DeprecationWarning, match='read_materials_from_json'):
            assert 'Steel' in read_materials_from_json(multiple_materials_path)

        material = CauchyContinuumModel(name='Warn', isotropy=0, e=200e9, nu=0.3)
        target = tmp_path / 'warn.json'
        with pytest.warns(DeprecationWarning, match='write_to_json'):
            material.write_to_json(str(target))
