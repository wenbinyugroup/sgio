from __future__ import annotations

import math
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, computed_field

# from dataclasses import dataclass

# @dataclass
class EulerBernoulliBeamModel(BaseModel):
    """Euler-Bernoulli Beam Model
    """

    # Class attributes (not Pydantic fields)
    dim: int = 1
    label: str = 'bm1'
    model_name: str = 'Euler-Bernoulli beam model'

    # Basic properties
    name: str = Field(default='', description="Beam name")
    id: Optional[int] = Field(default=None, description="Beam ID")

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
        s = [
            self.model_name,
        ]

        s.append('-'*16)
        s.append('mass matrix')
        if not self.mass is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.mass[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('mass center = ({}, {})'.format(
            f'{self.xm2:14e}' if not self.xm2 is None else 'NONE',
            f'{self.xm3:14e}' if not self.xm3 is None else 'NONE'
        ))
        s.append('')
        s.append('mass matrix w.r.t. mass center')
        if not self.mass_mc is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.mass_mc[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('mass per unit span = {}'.format(
            f'{self.mu:14e}' if not self.mu is None else 'NONE'
        ))
        s.append('mass moment of inertia')
        s.append('  i11 = {}'.format(
            f'{self.i11:14e}' if not self.i11 is None else 'NONE'
        ))
        s.append('  i22 = {}'.format(
            f'{self.i22:14e}' if not self.i22 is None else 'NONE'
        ))
        s.append('  i33 = {}'.format(
            f'{self.i33:14e}' if not self.i33 is None else 'NONE'
        ))
        s.append('principal inertial axes rotation angle = {}'.format(
            f'{self.phi_pia:14e}' if not self.phi_pia is None else 'NONE'
        ))
        s.append('mass-weighted radius of gyration = {}'.format(
            f'{self.rg:14e}' if not self.rg is None else 'NONE'
        ))

        s.append('-'*16)
        s.append('stiffness matrix')
        if not self.stff is None:
            for i in range(4):
                _row = []
                for j in range(4):
                    _row.append(f'{self.stff[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('compliance matrix')
        if not self.cmpl is None:
            for i in range(4):
                _row = []
                for j in range(4):
                    _row.append(f'{self.cmpl[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('tension center = ({}, {})'.format(
            f'{self.xt2:14e}' if not self.xt2 is None else 'NONE',
            f'{self.xt3:14e}' if not self.xt3 is None else 'NONE'
        ))
        s.append('extension stiffness EA = {}'.format(
            f'{self.ea:14e}' if not self.ea is None else 'NONE',
        ))
        s.append('torsional stiffness GJ = {}'.format(
            f'{self.gj:14e}' if not self.gj is None else 'NONE',
        ))
        s.append('principal bending stiffness EI22 = {}'.format(
            f'{self.ei22:14e}' if not self.ei22 is None else 'NONE',
        ))
        s.append('principal bending stiffness EI33 = {}'.format(
            f'{self.ei33:14e}' if not self.ei33 is None else 'NONE',
        ))
        s.append('principal bending axes rotation angle = {}'.format(
            f'{self.phi_pba:14e}' if not self.phi_pba is None else 'NONE',
        ))

        return '\n'.join(s)


    def __call__(self, x):
        return


    def set(self, name, value, **kwargs):
        return


    def get(self, name):
        """Get beam properties using specific names.

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

        if isinstance(name, str):
            name = name.lower()

            # Mass
            if name.startswith('ms'):
                if self.mass is not None:
                    return self.mass[int(name[2])-1][int(name[3])-1]
                return None
            if name == 'mu':
                return self.mu
            if name == 'mmoi1':
                return self.i11
            if name == 'mmoi2':
                return self.i22
            if name == 'mmoi3':
                return self.i33
            if name in ['gyr1', 'gyrx']:
                return self.gyr1
            if name in ['gyr2', 'gyry']:
                return self.gyr2
            if name in ['gyr3', 'gyrz']:
                return self.gyr3

            # Stiffness
            if name.startswith('stf'):
                if self.stff is not None:
                    return self.stff[int(name[3])-1][int(name[4])-1]
                return None

            # Compliance
            if name.startswith('cmp'):
                if self.cmpl is not None:
                    return self.cmpl[int(name[3])-1][int(name[4])-1]
                return None

            if name == 'ea':
                return self.ea
            if name == 'gj':
                return self.gj
            if name in ['ei22', 'eiyy', 'ei2', 'eiy']:
                return self.ei22
            if name in ['ei33', 'eizz', 'ei3', 'eiz']:
                return self.ei33

            # Various centers
            if name == 'mcy' or name == 'mc2':
                return self.xm2
            if name == 'mcz' or name == 'mc3':
                return self.xm3
            if name == 'tcy' or name == 'tc2':
                return self.xt2
            if name == 'tcz' or name == 'tc3':
                return self.xt3

            # Principal axes
            if name == 'phi_pia':
                return self.phi_pia
            if name == 'phi_pba':
                return self.phi_pba

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









class TimoshenkoBeamModel:
    """Timoshenko Beam Model
    """

    dim = 1
    label = 'bm2'
    model_name = 'Timoshenko beam model'

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
        self.stff_c = []
        #: list of lists of floats:
        #: Classical compliance matrix (1-extension; 2-twist; 3,4-bending)
        self.cmpl_c = []

        #: list of lists of floats:
        #: Timoshenko stiffness matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
        self.stff = []
        #: list of lists of floats:
        #: Timoshenko compliance matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
        self.cmpl = []

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
    def gyr2(self): return math.sqrt(self.i22/self.mu)
    @property
    def gyr3(self): return math.sqrt(self.i33/self.mu)


    def __repr__(self):
        s = [
            self.model_name,
        ]

        s.append('-'*16)
        s.append('mass matrix')
        if not self.mass is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.mass[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')
        s.append('')
        s.append('mass matrix w.r.t. mass center')
        if not self.mass_mc is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.mass_mc[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('mass center = ({}, {})'.format(
            f'{self.xm2:14e}' if not self.xm2 is None else 'NONE',
            f'{self.xm3:14e}' if not self.xm3 is None else 'NONE'
        ))
        s.append('mass per unit span = {}'.format(
            f'{self.mu:14e}' if not self.mu is None else 'NONE'
        ))
        s.append('mass moment of inertia')
        s.append('  i11 = {}'.format(
            f'{self.i11:14e}' if not self.i11 is None else 'NONE'
        ))
        s.append('  i22 = {}'.format(
            f'{self.i22:14e}' if not self.i22 is None else 'NONE'
        ))
        s.append('  i33 = {}'.format(
            f'{self.i33:14e}' if not self.i33 is None else 'NONE'
        ))
        s.append('principal inertial axes rotation angle = {}'.format(
            f'{self.phi_pia:14e}' if not self.phi_pia is None else 'NONE'
        ))
        s.append('mass-weighted radius of gyration = {}'.format(
            f'{self.rg:14e}' if not self.rg is None else 'NONE'
        ))

        s.append('-'*16)
        s.append('stiffness matrix')
        if not self.stff is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.stff[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('compliance matrix')
        if not self.cmpl is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.cmpl[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('tension center = ({}, {})'.format(
            f'{self.xt2:14e}' if not self.xt2 is None else 'NONE',
            f'{self.xt3:14e}' if not self.xt3 is None else 'NONE'
        ))
        s.append('extension stiffness EA = {}'.format(
            f'{self.ea:14e}' if not self.ea is None else 'NONE',
        ))
        s.append('torsional stiffness GJ = {}'.format(
            f'{self.gj:14e}' if not self.gj is None else 'NONE',
        ))
        s.append('principal bending stiffness EI22 = {}'.format(
            f'{self.ei22:14e}' if not self.ei22 is None else 'NONE',
        ))
        s.append('principal bending stiffness EI33 = {}'.format(
            f'{self.ei33:14e}' if not self.ei33 is None else 'NONE',
        ))
        s.append('principal bending axes rotation angle = {}'.format(
            f'{self.phi_pba:14e}' if not self.phi_pba is None else 'NONE',
        ))
        s.append('shear center = ({}, {})'.format(
            f'{self.xs2:14e}' if not self.xs2 is None else 'NONE',
            f'{self.xs3:14e}' if not self.xs3 is None else 'NONE'
        ))
        s.append('principal shear stiffness GA22 = {}'.format(
            f'{self.ga22:14e}' if not self.ga22 is None else 'NONE',
        ))
        s.append('principal shear stiffness GA33 = {}'.format(
            f'{self.ga33:14e}' if not self.ga33 is None else 'NONE',
        ))
        s.append('principal shear axes rotation angle = {}'.format(
            f'{self.phi_psa:14e}' if not self.phi_psa is None else 'NONE',
        ))

        s.append('-'*16)
        s.append('stiffness matrix (classical)')
        if not self.stff_c is None:
            for i in range(4):
                _row = []
                for j in range(4):
                    _row.append(f'{self.stff_c[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('')
        s.append('compliance matrix (classical)')
        if not self.cmpl_c is None:
            for i in range(4):
                _row = []
                for j in range(4):
                    _row.append(f'{self.cmpl_c[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        return '\n'.join(s)


    def __call__(self, x):
        return


    def set(self, name, value, **kwargs):
        return


    def get(self, name):
        """Get beam properties using specific names.

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

        if isinstance(name, str):
            name = name.lower()

            # Mass
            if name.startswith('ms'):
                return self.mass[int(name[2])-1][int(name[3])-1]
            if name == 'mu':
                return self.mu
            if name == 'mmoi1':
                return self.i11
            if name == 'mmoi2':
                return self.i22
            if name == 'mmoi3':
                return self.i33
            if name in ['gyr1', 'gyrx']:
                return self.gyr1
            if name in ['gyr2', 'gyry']:
                return self.gyr2
            if name in ['gyr3', 'gyrz']:
                return self.gyr3

            # Stiffness
            if name.startswith('stf'):
                if name[-1] == 'c':
                    return self.stff_c[int(name[3])-1][int(name[4])-1]
                else:
                    return self.stff[int(name[3])-1][int(name[4])-1]

            # Compliance
            if name.startswith('cmp'):
                if name[-1] == 'c':
                    return self.cmpl_c[int(name[3])-1][int(name[4])-1]
                else:
                    return self.cmpl[int(name[3])-1][int(name[4])-1]

            if name == 'ea':
                return self.ea
            if name in ['ga22', 'gayy', 'ga2', 'gay']:
                return self.ga22
            if name in ['ga33', 'gazz', 'ga3', 'gaz']:
                return self.ga33
            if name == 'gj':
                return self.gj
            if name in ['ei22', 'eiyy', 'ei2', 'eiy']:
                return self.ei22
            if name in ['ei33', 'eizz', 'ei3', 'eiz']:
                return self.ei33

            # Various centers
            if name == 'mcy' or name == 'mc2':
                return self.xm2
            if name == 'mcz' or name == 'mc3':
                return self.xm3
            if name == 'tcy' or name == 'tc2':
                return self.xt2
            if name == 'tcz' or name == 'tc3':
                return self.xt3
            if name == 'scy' or name == 'sc2':
                return self.xs2
            if name == 'scz' or name == 'sc3':
                return self.xs3

            # Principal axes
            if name == 'phi_pia':
                return self.phi_pia
            if name == 'phi_pba':
                return self.phi_pba
            if name == 'phi_psa':
                return self.phi_psa

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

