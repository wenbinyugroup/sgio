from __future__ import annotations

import math
from typing import ClassVar, List, Optional

from pydantic import BaseModel, Field, field_validator, computed_field

from ._deprecations import warn_model_deprecation
from .query_types import SectionAxis, SectionCenter, SectionMatrixKind
from .section_common import (
    EULER_BERNOULLI_BEAM_SCHEMA,
    StructuralTheorySchema,
    StructuralSectionSupport,
    TIMOSHENKO_BEAM_SCHEMA,
)

# from dataclasses import dataclass

# @dataclass
class EulerBernoulliBeamModel(StructuralSectionSupport, BaseModel):
    """Euler-Bernoulli Beam Model
    """

    # Class attributes (not Pydantic fields)
    dim: int = 1
    label: str = 'bm1'
    model_name: str = 'Euler-Bernoulli beam model'
    theory_schema: ClassVar[StructuralTheorySchema] = EULER_BERNOULLI_BEAM_SCHEMA
    _SCALAR_ALIASES: ClassVar[dict[str, str]] = {
        'mu': 'mu',
        'mmoi1': 'i11',
        'mmoi2': 'i22',
        'mmoi3': 'i33',
        'gyr1': 'gyr1',
        'gyrx': 'gyr1',
        'gyr2': 'gyr2',
        'gyry': 'gyr2',
        'gyr3': 'gyr3',
        'gyrz': 'gyr3',
        'ea': 'ea',
        'gj': 'gj',
        'ei22': 'ei22',
        'eiyy': 'ei22',
        'ei2': 'ei22',
        'eiy': 'ei22',
        'ei33': 'ei33',
        'eizz': 'ei33',
        'ei3': 'ei33',
        'eiz': 'ei33',
    }
    _CENTER_ALIASES: ClassVar[dict[str, str]] = {
        'mcy': 'xm2',
        'mc2': 'xm2',
        'mcz': 'xm3',
        'mc3': 'xm3',
        'tcy': 'xt2',
        'tc2': 'xt2',
        'tcz': 'xt3',
        'tc3': 'xt3',
    }
    _AXIS_ALIASES: ClassVar[dict[str, str]] = {
        'phi_pia': 'phi_pia',
        'phi_pba': 'phi_pba',
    }
    _SECTION_CENTER_ATTRS: ClassVar[dict[SectionCenter, tuple[str, ...]]] = {
        SectionCenter.MASS: ('xm2', 'xm3'),
        SectionCenter.TENSION: ('xt2', 'xt3'),
    }
    _SECTION_AXIS_ATTRS: ClassVar[dict[SectionAxis, str]] = {
        SectionAxis.INERTIAL: 'phi_pia',
        SectionAxis.BENDING: 'phi_pba',
    }
    _SECTION_MATRIX_ATTRS: ClassVar[dict[SectionMatrixKind, str]] = {
        SectionMatrixKind.MASS: 'mass',
        SectionMatrixKind.MASS_CENTER: 'mass_mc',
        SectionMatrixKind.STIFFNESS: 'stff',
        SectionMatrixKind.COMPLIANCE: 'cmpl',
    }

    # Basic properties
    name: str = Field(default='', description="Beam name")
    id: Optional[int] = Field(default=None, description="Beam ID")

    # Geometric properties
    xg2: Optional[float] = Field(default=None, description="Geometric center location in x2 direction")
    xg3: Optional[float] = Field(default=None, description="Geometric center location in x3 direction")
    area: Optional[float] = Field(default=None, ge=0, description="Area of the cross-section")

    # Inertial properties
    mass: Optional[List[List[float]]] = Field(
        default=None,
        description="The 6x6 mass matrix"
    )
    mass_mc: Optional[List[List[float]]] = Field(
        default=None,
        description="The 6x6 mass matrix at the mass center"
    )

    # Mass center locations
    xm2: Optional[float] = Field(default=None, description="Mass center location in x2 direction")
    xm3: Optional[float] = Field(default=None, description="Mass center location in x3 direction")

    # Mass properties
    mu: Optional[float] = Field(default=None, ge=0, description="Mass per unit span")
    i11: Optional[float] = Field(default=None, ge=0, description="Mass moments of inertia i11")
    i22: Optional[float] = Field(default=None, ge=0, description="Principal mass moments of inertia i22")
    i33: Optional[float] = Field(default=None, ge=0, description="Principal mass moments of inertia i33")
    phi_pia: float = Field(default=0, description="Principal inertial axes rotation angle in degree")
    rg: Optional[float] = Field(default=None, ge=0, description="Mass-weighted radius of gyration")

    # Structural properties
    stff: Optional[List[List[float]]] = Field(
        default=None,
        description="Classical stiffness matrix (1-extension; 2-twist; 3,4-bending)"
    )
    cmpl: Optional[List[List[float]]] = Field(
        default=None,
        description="Classical compliance matrix (1-extension; 2-twist; 3,4-bending)"
    )

    # Tension center locations
    xt2: Optional[float] = Field(default=None, description="Tension center location in x2 direction")
    xt3: Optional[float] = Field(default=None, description="Tension center location in x3 direction")

    # Stiffness properties
    ea: Optional[float] = Field(default=None, ge=0, description="Extension stiffness EA")
    gj: Optional[float] = Field(default=None, ge=0, description="Torsional stiffness GJ")
    ei22: Optional[float] = Field(default=None, ge=0, description="Principal bending stiffness EI22")
    ei33: Optional[float] = Field(default=None, ge=0, description="Principal bending stiffness EI33")
    phi_pba: float = Field(default=0, description="Principal bending axes rotation angle in degree")

    # Pydantic configuration
    model_config = {"arbitrary_types_allowed": True}

    # Field validators
    @field_validator('mass', 'mass_mc')
    @classmethod
    def validate_6x6_matrix(cls, v):
        """Validate that mass matrices are 6x6"""
        if v is not None:
            if not isinstance(v, list) or len(v) != 6:
                raise ValueError('Matrix must be 6x6 (6 rows)')
            for i, row in enumerate(v):
                if not isinstance(row, list) or len(row) != 6:
                    raise ValueError(f'Row {i} must have 6 columns')
        return v

    @field_validator('stff', 'cmpl')
    @classmethod
    def validate_4x4_matrix(cls, v):
        """Validate that stiffness/compliance matrices are 4x4"""
        if v is not None:
            if not isinstance(v, list) or len(v) != 4:
                raise ValueError('Matrix must be 4x4 (4 rows)')
            for i, row in enumerate(v):
                if not isinstance(row, list) or len(row) != 4:
                    raise ValueError(f'Row {i} must have 4 columns')
        return v

    # Computed properties
    @computed_field
    @property
    def gyr1(self) -> Optional[float]:
        """Mass-weighted radius of gyration (same as rg)"""
        return self.rg

    @computed_field
    @property
    def gyr2(self) -> Optional[float]:
        """Radius of gyration about x2 axis"""
        if self.i22 is not None and self.mu is not None and self.mu > 0:
            return math.sqrt(self.i22 / self.mu)
        return None

    @computed_field
    @property
    def gyr3(self) -> Optional[float]:
        """Radius of gyration about x3 axis"""
        if self.i33 is not None and self.mu is not None and self.mu > 0:
            return math.sqrt(self.i33 / self.mu)
        return None


    def __repr__(self):
        s = [self.model_name]
        s.append('-' * 16)
        s.extend(self._format_matrix_block('mass matrix', self.mass))
        s.append('')
        s.append(self._format_center_line('mass center', self.xm2, self.xm3))
        s.append('')
        s.extend(self._format_matrix_block('mass matrix w.r.t. mass center', self.mass_mc))
        s.append('')
        s.append(self._format_scalar_line('mass per unit span', self.mu))
        s.append('mass moment of inertia')
        s.append(self._format_scalar_line('  i11', self.i11))
        s.append(self._format_scalar_line('  i22', self.i22))
        s.append(self._format_scalar_line('  i33', self.i33))
        s.append(self._format_scalar_line('principal inertial axes rotation angle', self.phi_pia))
        s.append(self._format_scalar_line('mass-weighted radius of gyration', self.rg))
        s.append('-' * 16)
        s.extend(self._format_matrix_block('stiffness matrix', self.stff))
        s.append('')
        s.extend(self._format_matrix_block('compliance matrix', self.cmpl))
        s.append('')
        s.append(self._format_center_line('tension center', self.xt2, self.xt3))
        s.append(self._format_scalar_line('extension stiffness EA', self.ea))
        s.append(self._format_scalar_line('torsional stiffness GJ', self.gj))
        s.append(self._format_scalar_line('principal bending stiffness EI22', self.ei22))
        s.append(self._format_scalar_line('principal bending stiffness EI33', self.ei33))
        s.append(self._format_scalar_line('principal bending axes rotation angle', self.phi_pba))
        return '\n'.join(s)


    def __call__(self, x):
        return


    def set(self, name, value, **kwargs):
        """Compatibility setter retained for legacy string callers."""
        warn_model_deprecation('EulerBernoulliBeamModel.set')
        return


    def get(self, name):
        """Compatibility query API retained for legacy string callers.

        Parameters
        ----------
        name : str or list of str
            Name(s) of the property that will be returned.

        Returns
        -------
        float or list of float:
            Value(s) of the specified beam property.

        Notes
        -----

        ..  list-table:: Inertial properties
            :header-rows: 1

            * - Name
              - Description
            * - ``msij`` (``i``, ``j`` = 1 to 6)
              - Entry (i, j) of the 6x6 mass matrix at the origin
            * - ``mu``
              - Mass per unit length
            * - ``mmoi1`` | ``mmoi2`` | ``mmoi3``
              - Mass moment of inertia about x1/x2/x3 axis

        ..  list-table:: Stiffness properties
            :header-rows: 1

            * - Name
              - Description
            * - ``stfij`` (``i``, ``j`` = 1 to 6)
              - Entry (i, j) of the 4x4 classical stiffness matrix
            * - ``cmpij`` (``i``, ``j`` = 1 to 6)
              - Entry (i, j) of the 4x4 classical compliance matrix
            * - ``ea``
              - Axial stiffness of the model
            * - ``gj``
              - Torsional stiffness of the model
            * - ``ei22`` | ``eiyy``
              - Bending stiffness around x2 (flapwise) of the model
            * - ``ei33`` | ``eizz``
              - Bending stiffness around x3 (chordwise or lead-lag) of the model

        ..  list-table:: Center offsets
            :header-rows: 1

            * - Name
              - Description
            * - ``mcy`` | ``mc2``
              - y (or x2) component of the mass center
            * - ``mcz`` | ``mc3``
              - z (or x3) component of the mass center
            * - ``tcy`` | ``tc2``
              - y (or x2) component of the tension center
            * - ``tcz`` | ``tc3``
              - z (or x3) component of the tension center

        """
        warn_model_deprecation('EulerBernoulliBeamModel.get')

        if isinstance(name, str):
            name = name.lower()

            # Mass
            if name.startswith('ms'):
                return self._get_matrix_value(name, 2, self.mass)

            # Stiffness
            if name.startswith('stf'):
                return self._get_matrix_value(name, 3, self.stff)

            # Compliance
            if name.startswith('cmp'):
                return self._get_matrix_value(name, 3, self.cmpl)

            found, value = self._get_aliased_value(self, name, self._SCALAR_ALIASES)
            if found:
                return value

            found, value = self._get_aliased_value(self, name, self._CENTER_ALIASES)
            if found:
                return value

            found, value = self._get_aliased_value(self, name, self._AXIS_ALIASES)
            if found:
                return value

            # Return None for unrecognized properties (e.g., ga22, ga33 which are Timoshenko-only)
            return None

        elif isinstance(name, list) or isinstance(name, tuple):
            props = []
            for n in name:
                props.append(self.get(n))
            return props

        return None


    def getAll(self):
        """Get all beam properties.

        Returns
        -------
        dict:
            A Dictionary of all beam properties.

        Notes
        -----

        Names are

        - mu, mmoi1, mmoi2, mmoi3
        - ea, ga22, ga33, gj, ei22, ei33
        - mc2, mc3, tc2, tc3
        - stfij, cmpij

        """
        warn_model_deprecation('EulerBernoulliBeamModel.getAll')
        names = [
            'mu', 'mmoi1', 'mmoi2', 'mmoi3',
            'ea', 'ga22', 'ga33', 'gj', 'ei22', 'ei33',
            'mc2', 'mc3', 'tc2', 'tc3'
        ]
        for i in range(4):
            for j in range(4):
                names.append('stf{}{}'.format(i+1, j+1))
                names.append('cmp{}{}'.format(i+1, j+1))

        dict_prop = {}
        for n in names:
            dict_prop[n] = self.get(n)

        return dict_prop









class TimoshenkoBeamModel(StructuralSectionSupport):
    """Timoshenko Beam Model
    """

    dim = 1
    label = 'bm2'
    model_name = 'Timoshenko beam model'
    theory_schema: ClassVar[StructuralTheorySchema] = TIMOSHENKO_BEAM_SCHEMA
    _SCALAR_ALIASES: ClassVar[dict[str, str]] = {
        'mu': 'mu',
        'mmoi1': 'i11',
        'mmoi2': 'i22',
        'mmoi3': 'i33',
        'gyr1': 'gyr1',
        'gyrx': 'gyr1',
        'gyr2': 'gyr2',
        'gyry': 'gyr2',
        'gyr3': 'gyr3',
        'gyrz': 'gyr3',
        'ea': 'ea',
        'ga22': 'ga22',
        'gayy': 'ga22',
        'ga2': 'ga22',
        'gay': 'ga22',
        'ga33': 'ga33',
        'gazz': 'ga33',
        'ga3': 'ga33',
        'gaz': 'ga33',
        'gj': 'gj',
        'ei22': 'ei22',
        'eiyy': 'ei22',
        'ei2': 'ei22',
        'eiy': 'ei22',
        'ei33': 'ei33',
        'eizz': 'ei33',
        'ei3': 'ei33',
        'eiz': 'ei33',
    }
    _CENTER_ALIASES: ClassVar[dict[str, str]] = {
        'mcy': 'xm2',
        'mc2': 'xm2',
        'mcz': 'xm3',
        'mc3': 'xm3',
        'tcy': 'xt2',
        'tc2': 'xt2',
        'tcz': 'xt3',
        'tc3': 'xt3',
        'scy': 'xs2',
        'sc2': 'xs2',
        'scz': 'xs3',
        'sc3': 'xs3',
    }
    _AXIS_ALIASES: ClassVar[dict[str, str]] = {
        'phi_pia': 'phi_pia',
        'phi_pba': 'phi_pba',
        'phi_psa': 'phi_psa',
    }
    _SECTION_CENTER_ATTRS: ClassVar[dict[SectionCenter, tuple[str, ...]]] = {
        SectionCenter.MASS: ('xm2', 'xm3'),
        SectionCenter.TENSION: ('xt2', 'xt3'),
        SectionCenter.SHEAR: ('xs2', 'xs3'),
    }
    _SECTION_AXIS_ATTRS: ClassVar[dict[SectionAxis, str]] = {
        SectionAxis.INERTIAL: 'phi_pia',
        SectionAxis.BENDING: 'phi_pba',
        SectionAxis.SHEAR: 'phi_psa',
    }
    _SECTION_MATRIX_ATTRS: ClassVar[dict[SectionMatrixKind, str]] = {
        SectionMatrixKind.MASS: 'mass',
        SectionMatrixKind.MASS_CENTER: 'mass_mc',
        SectionMatrixKind.STIFFNESS: 'stff',
        SectionMatrixKind.COMPLIANCE: 'cmpl',
        SectionMatrixKind.CLASSICAL_STIFFNESS: 'stff_c',
        SectionMatrixKind.CLASSICAL_COMPLIANCE: 'cmpl_c',
    }

    def __init__(self):
        self.name = ''
        self.id = None

        #: float: Geometric center location in x2 direction
        self.xg2 = None
        #: float: Geometric center location in x3 direction
        self.xg3 = None

        #: float: Area of the cross-section
        self.area = None


        # Inertial properties
        # -------------------

        #: list of list of floats:
        #: The 6x6 mass matrix
        self.mass = None

        #: list of lists of floats:
        #: The 6x6 mass matrix at the mass center
        self.mass_mc = None

        #: float: Mass center location in x2 direction
        self.xm2 = None
        #: float: Mass center location in x3 direction
        self.xm3 = None

        #: float: Mass per unit span
        self.mu = None
        #: float: Mass moments of inertia i11
        self.i11 = None
        #: float: Principal mass moments of inertia i22
        self.i22 = None
        #: float: Principle mass moments of inertia i33
        self.i33 = None
        #: float: Principal inertial axes rotation angle in degree
        self.phi_pia = 0
        #: float: mass-weighted radius of gyration
        self.rg = None


        # Structural properties
        # ---------------------

        #: list of lists of floats:
        #: Classical stiffness matrix (1-extension; 2-twist; 3,4-bending)
        self.stff_c = None
        #: list of lists of floats:
        #: Classical compliance matrix (1-extension; 2-twist; 3,4-bending)
        self.cmpl_c = None

        #: list of lists of floats:
        #: Timoshenko stiffness matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
        self.stff = None
        #: list of lists of floats:
        #: Timoshenko compliance matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
        self.cmpl = None

        #: float: Tension center location in x2 direction
        self.xt2 = None
        #: float: Tension center location in x3 direction
        self.xt3 = None

        #: float: Extension stiffness EA
        self.ea = None
        #: float: Torsional stiffness GJ
        self.gj = None
        #: float: Principal bending stiffness EI22
        self.ei22 = None
        #: float: Principal bending stiffness EI33
        self.ei33 = None
        #: float: Principle bending axes rotation angle in degree
        self.phi_pba = 0

        #: float: Generalized shear center location in x2 direction
        self.xs2 = None
        #: float: Generalized shear center location in x3 direction
        self.xs3 = None
        #: float: Principal shear stiffness GA22
        self.ga22 = None
        #: float: Principal shear stiffness GA33
        self.ga33 = None
        #: float: Principal shear axes rotation angle in degree
        self.phi_psa = 0

    @property
    def gyr1(self): return self.rg
    @property
    def gyr2(self):
        if self.i22 is None or self.mu in (None, 0):
            return None
        return math.sqrt(self.i22 / self.mu)
    @property
    def gyr3(self):
        if self.i33 is None or self.mu in (None, 0):
            return None
        return math.sqrt(self.i33 / self.mu)


    def __repr__(self):
        s = [self.model_name]
        s.append('-' * 16)
        s.extend(self._format_matrix_block('mass matrix', self.mass))
        s.append('')
        s.extend(self._format_matrix_block('mass matrix w.r.t. mass center', self.mass_mc))
        s.append('')
        s.append(self._format_center_line('mass center', self.xm2, self.xm3))
        s.append(self._format_scalar_line('mass per unit span', self.mu))
        s.append('mass moment of inertia')
        s.append(self._format_scalar_line('  i11', self.i11))
        s.append(self._format_scalar_line('  i22', self.i22))
        s.append(self._format_scalar_line('  i33', self.i33))
        s.append(self._format_scalar_line('principal inertial axes rotation angle', self.phi_pia))
        s.append(self._format_scalar_line('mass-weighted radius of gyration', self.rg))
        s.append('-' * 16)
        s.extend(self._format_matrix_block('stiffness matrix', self.stff))
        s.append('')
        s.extend(self._format_matrix_block('compliance matrix', self.cmpl))
        s.append('')
        s.append(self._format_center_line('tension center', self.xt2, self.xt3))
        s.append(self._format_scalar_line('extension stiffness EA', self.ea))
        s.append(self._format_scalar_line('torsional stiffness GJ', self.gj))
        s.append(self._format_scalar_line('principal bending stiffness EI22', self.ei22))
        s.append(self._format_scalar_line('principal bending stiffness EI33', self.ei33))
        s.append(self._format_scalar_line('principal bending axes rotation angle', self.phi_pba))
        s.append(self._format_center_line('shear center', self.xs2, self.xs3))
        s.append(self._format_scalar_line('principal shear stiffness GA22', self.ga22))
        s.append(self._format_scalar_line('principal shear stiffness GA33', self.ga33))
        s.append(self._format_scalar_line('principal shear axes rotation angle', self.phi_psa))
        s.append('-' * 16)
        s.extend(self._format_matrix_block('stiffness matrix (classical)', self.stff_c))
        s.append('')
        s.extend(self._format_matrix_block('compliance matrix (classical)', self.cmpl_c))
        return '\n'.join(s)


    def __call__(self, x):
        return


    def set(self, name, value, **kwargs):
        """Compatibility setter retained for legacy string callers."""
        warn_model_deprecation('TimoshenkoBeamModel.set')
        return


    def get(self, name):
        """Compatibility query API retained for legacy string callers.

        Parameters
        ----------
        name : str
            Name of the property that will be returned.

        Returns
        -------
        float:
            Value of the specified beam property.

        Notes
        -----

        ..  list-table:: Inertial properties
            :header-rows: 1

            * - Name
              - Description
            * - ``msijo`` (``i``, ``j`` are numbers 1 to 6)
              - Entry (i, j) of the 6x6 mass matrix at the origin
            * - ``msijc`` (``i``, ``j`` are numbers 1 to 6)
              - Entry (i, j) of the 6x6 mass matrix at the mass center
            * - ``mu``
              - Mass per unit length
            * - ``mmoi1`` | ``mmoi2`` | ``mmoi3``
              - Mass moment of inertia about x1/x2/x3 axis

        ..  list-table:: Stiffness properties
            :header-rows: 1

            * - Name
              - Description
            * - ``stfijc`` (``i``, ``j`` are numbers 1 to 6)
              - Entry (i, j) of the 4x4 classical stiffness matrix
            * - ``stfijr`` (``i``, ``j`` are numbers 1 to 6)
              - Entry (i, j) of the 6x6 refined stiffness matrix
            * - ``eac`` | ``ear``
              - Axial stiffness of the classical/refined model
            * - ``gjc`` | ``gjr``
              - Torsional stiffness of the classical/refined model
            * - ``ei2c`` | ``eifc`` | ``ei2r`` | ``eifr``
              - Bending stiffness around x2 (flapwise) of the classical/refined model
            * - ``ei3c`` | ``eicc`` | ``ei3r`` | ``eicr``
              - Bending stiffness around x3 (chordwise or lead-lag) of the classical/refined model
            * - ``cmpijc`` (``i``, ``j`` are numbers 1 to 6)
              - Entry (i, j) of the 4x4 classical compliance matrix
            * - ``cmpijr`` (``i``, ``j`` are numbers 1 to 6)
              - Entry (i, j) of the 6x6 refined compliance matrix

        ..  list-table:: Center offsets
            :header-rows: 1

            * - Name
              - Description
            * - ``mcy`` | ``mc2``
              - y (or x2) component of the mass center
            * - ``mcz`` | ``mc3``
              - z (or x3) component of the mass center
            * - ``tcy`` | ``tc2``
              - y (or x2) component of the tension center
            * - ``tcz`` | ``tc3``
              - z (or x3) component of the tension center
            * - ``scy`` | ``sc2``
              - y (or x2) component of the shear center
            * - ``scz`` | ``sc3``
              - z (or x3) component of the shear center

        .

        """
        warn_model_deprecation('TimoshenkoBeamModel.get')

        if isinstance(name, str):
            name = name.lower()

            # Mass
            if name.startswith('ms'):
                return self._get_matrix_value(name, 2, self.mass)

            # Stiffness
            if name.startswith('stf'):
                if name[-1] == 'c':
                    return self._get_matrix_value(name, 3, self.stff_c)
                return self._get_matrix_value(name, 3, self.stff)

            # Compliance
            if name.startswith('cmp'):
                if name[-1] == 'c':
                    return self._get_matrix_value(name, 3, self.cmpl_c)
                return self._get_matrix_value(name, 3, self.cmpl)

            found, value = self._get_aliased_value(self, name, self._SCALAR_ALIASES)
            if found:
                return value

            found, value = self._get_aliased_value(self, name, self._CENTER_ALIASES)
            if found:
                return value

            found, value = self._get_aliased_value(self, name, self._AXIS_ALIASES)
            if found:
                return value

        elif isinstance(name, list) or isinstance(name, tuple):
            props = []
            for n in name:
                props.append(self.get(n))
            return props


    def getAll(self):
        """Get all beam properties.

        Returns
        -------
        dict:
            A Dictionary of all beam properties.

        Notes
        -----

        Names are

        - mu, mmoi1, mmoi2, mmoi3
        - ea, ga22, ga33, gj, ei22, ei33
        - mc2, mc3, tc2, tc3, sc2, sc3
        - msij, stfijc, cmpijc, stfijr, cmpijr

        """
        warn_model_deprecation('TimoshenkoBeamModel.getAll')
        names = [
            'mu', 'mmoi1', 'mmoi2', 'mmoi3',
            'ea', 'ga22', 'ga33', 'gj', 'ei22', 'ei33',
            'mc2', 'mc3', 'tc2', 'tc3', 'sc2', 'sc3'
        ]
        for i in range(4):
            for j in range(4):
                names.append('stf{}{}c'.format(i+1, j+1))
                names.append('cmp{}{}c'.format(i+1, j+1))
        for i in range(6):
            for j in range(6):
                names.append('ms{}{}'.format(i+1, j+1))
                names.append('stf{}{}'.format(i+1, j+1))
                names.append('cmp{}{}'.format(i+1, j+1))

        dict_prop = {}
        for n in names:
            dict_prop[n] = self.get(n)

        return dict_prop

