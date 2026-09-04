from __future__ import annotations

from typing import ClassVar

from ._deprecations import warn_model_deprecation
from .query_types import SectionCenter, SectionMatrixKind
from .section_common import (
    KIRCHHOFF_LOVE_SHELL_SCHEMA,
    REISSNER_MINDLIN_SHELL_SCHEMA,
    StructuralTheorySchema,
    StructuralSectionSupport,
)


class KirchhoffLovePlateShellModel(StructuralSectionSupport):
    """Kirchhoff-Love Plate/Shell Model
    """

    dim = 2
    label = 'pl1'
    model_name = 'Kirchhoff-Love plate/shell model'
    theory_schema: ClassVar[StructuralTheorySchema] = KIRCHHOFF_LOVE_SHELL_SCHEMA
    _IN_PLANE_PROPERTIES: ClassVar[dict[str, str]] = {
        'E1': 'e1_i',
        'E2': 'e2_i',
        'G12': 'g12_i',
        'nu12': 'nu12_i',
        'eta121': 'eta121_i',
        'eta122': 'eta122_i',
    }
    _FLEXURAL_PROPERTIES: ClassVar[dict[str, str]] = {
        'E1': 'e1_o',
        'E2': 'e2_o',
        'G12': 'g12_o',
        'nu12': 'nu12_o',
        'eta121': 'eta121_o',
        'eta122': 'eta122_o',
    }
    _SECTION_CENTER_ATTRS: ClassVar[dict[SectionCenter, tuple[str, ...]]] = {
        SectionCenter.MASS: ('xm3',),
    }
    _SECTION_MATRIX_ATTRS: ClassVar[dict[SectionMatrixKind, str]] = {
        SectionMatrixKind.MASS: 'mass',
        SectionMatrixKind.STIFFNESS: 'stff',
        SectionMatrixKind.COMPLIANCE: 'cmpl',
        SectionMatrixKind.GEOMETRIC_STIFFNESS: 'stff_geo',
    }

    def __init__(self):

        self.name = ''
        self.id = None

        # Inertial
        # --------
        self.mass = None

        self.xm3 = None

        self.i11 = None
        self.i22 = None

        # ------------

        self.stff = None
        self.cmpl = None

        self.geo_correction_stff = None
        self.stff_geo = None

        self.e1_i = None
        self.e2_i = None
        self.g12_i = None
        self.nu12_i = None
        self.eta121_i = None
        self.eta122_i = None

        self.e1_o = None
        self.e2_o = None
        self.g12_o = None
        self.nu12_o = None
        self.eta121_o = None
        self.eta122_o = None

        self.n11_t = None
        self.n22_t = None
        self.n12_t = None
        self.m11_t = None
        self.m22_t = None
        self.m12_t = None


    def __repr__(self) -> str:
        s = [self.model_name]
        s.append('----------------')
        s.extend(self._format_matrix_block('mass matrix', self.mass))
        s.append('----------------')
        s.extend(self._format_matrix_block('stiffness matrix', self.stff))
        s.append('')
        s.extend(self._format_matrix_block('compliance matrix', self.cmpl))
        s.append('-------------------')
        s.extend(self._format_named_attribute_block('in-plane properties', self, self._IN_PLANE_PROPERTIES))
        s.append('')
        s.extend(
            self._format_named_attribute_block(
                'flexural properties',
                self,
                self._FLEXURAL_PROPERTIES,
            )
        )
        return '\n'.join(s)


    def __call__(self, x):
        ...


    def set(self, name, value, **kwargs):
        """Compatibility setter retained for legacy string callers."""
        warn_model_deprecation('KirchhoffLovePlateShellModel.set')
        ...

    def get(self, name):
        """Compatibility query API retained for legacy string callers."""
        warn_model_deprecation('KirchhoffLovePlateShellModel.get')

        # Stiffness
        if name.startswith('stf'):
            if name[-1] == 'c':
                return self._get_matrix_value(name, 3, self.stff)
            elif name[-1] == 'r':
                if name[-2] == 'g':
                    entry = self._get_matrix_value(name, 3, self.stff_geo)
                    if entry is not None:
                        return entry
                    else:
                        return self._get_matrix_value(name, 3, self.stff)

        elif name.startswith('mass'):
            return self._get_matrix_value(name, 4, self.mass)

        return









class ReissnerMindlinPlateShellModel(StructuralSectionSupport):
    """Reissner-Mindlin Plate/Shell Model
    """

    dim = 2
    label = 'pl2'
    model_name = 'Reissner-Mindlin plate/shell model'
    theory_schema: ClassVar[StructuralTheorySchema] = REISSNER_MINDLIN_SHELL_SCHEMA

    def __init__(self):
        raise NotImplementedError(
            'ReissnerMindlinPlateShellModel is not implemented yet.'
        )

