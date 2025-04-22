from __future__ import annotations

import math

# from dataclasses import dataclass

# @dataclass
class EulerBernoulliBeamModel:
    """Euler-Bernoulli Beam Model
    """

    dim = 1
    label = 'bm1'
    model_name = 'Euler-Bernoulli beam model'

    def __init__(self):
        self.name = ''
        self.id = None

        # #: float: Geometric center location in x2 direction
        # self.xg2 = 0.
        # #: float: Geometric center location in x3 direction
        # self.xg3 = 0.

        # #: float: Area of the cross-section
        # self.area = 0.


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
        self.stff = None
        #: list of lists of floats:
        #: Classical compliance matrix (1-extension; 2-twist; 3,4-bending)
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

        # #: list of lists of floats:
        # #: Timoshenko stiffness matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
        # self.stff_t = []
        # #: list of lists of floats:
        # #: Timoshenko compliance matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
        # self.cmpl_t = []

        # #: float: Generalized shear center location in x2 direction
        # self.xs2 = None
        # #: float: Generalized shear center location in x3 direction
        # self.xs3 = None
        # #: float: Principal shear stiffness GA22
        # self.ga22 = None
        # #: float: Principal shear stiffness GA33
        # self.ga33 = None
        # #: float: Principal shear axes rotation angle in degree
        # self.phi_psa = None

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
                return self.stff[int(name[3])-1][int(name[4])-1]

            # Compliance
            if name.startswith('cmp'):
                return self.cmpl[int(name[3])-1][int(name[4])-1]

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









# # Legacy

# class BeamModel():
#     """A beam property class (smdim = 1)

#     """

#     def __init__(self):
#         # MaterialSection.__init__(self, smdim=1)

#         #: float: Geometric center location in x2 direction
#         self.xg2 = 0.
#         #: float: Geometric center location in x3 direction
#         self.xg3 = 0.

#         #: float: Area of the cross-section
#         self.area = 0.


#         # Inertial properties
#         # -------------------

#         #: list of list of floats:
#         #: The 6x6 mass matrix
#         self.mass = []

#         #: list of lists of floats:
#         #: The 6x6 mass matrix at the mass center
#         self.mass_cs = []

#         #: float: Mass center location in x2 direction
#         self.xm2 = 0.
#         #: float: Mass center location in x3 direction
#         self.xm3 = 0.

#         #: float: Mass per unit span
#         self.mu = 0.
#         #: float: Mass moments of inertia i11
#         self.i11 = 0.
#         #: float: Principal mass moments of inertia i22
#         self.i22 = 0.
#         #: float: Principle mass moments of inertia i33
#         self.i33 = 0.
#         #: float: Principal inertial axes rotation angle in degree
#         self.phi_pia = 0.
#         #: float: mass-weighted radius of gyration
#         self.rg = 0.


#         # Structural properties
#         # ---------------------

#         #: list of lists of floats:
#         #: Classical stiffness matrix (1-extension; 2-twist; 3,4-bending)
#         self.stff = []
#         #: list of lists of floats:
#         #: Classical compliance matrix (1-extension; 2-twist; 3,4-bending)
#         self.cmpl = []

#         #: float: Tension center location in x2 direction
#         self.xt2 = 0.
#         #: float: Tension center location in x3 direction
#         self.xt3 = 0.

#         #: float: Extension stiffness EA
#         self.ea = 0.
#         #: float: Torsional stiffness GJ
#         self.gj = 0.
#         #: float: Principal bending stiffness EI22
#         self.ei22 = 0.
#         #: float: Principal bending stiffness EI33
#         self.ei33 = 0.
#         #: float: Principle bending axes rotation angle in degree
#         self.phi_pba = 0.

#         #: list of lists of floats:
#         #: Timoshenko stiffness matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
#         self.stff_t = []
#         #: list of lists of floats:
#         #: Timoshenko compliance matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
#         self.cmpl_t = []

#         #: float: Generalized shear center location in x2 direction
#         self.xs2 = 0.
#         #: float: Generalized shear center location in x3 direction
#         self.xs3 = 0.
#         #: float: Principal shear stiffness GA22
#         self.ga22 = 0.
#         #: float: Principal shear stiffness GA33
#         self.ga33 = 0.
#         #: float: Principal shear axes rotation angle in degree
#         self.phi_psa = 0.


#     def printData(self):
#         fmt = '20.10E'
#         print('Summary')
#         print()
#         print('The 6x6 mass matrix')
#         print(utio.matrixToString(self.mass, fmt=fmt))
#         print()
#         print('The Mass Center of the Cross-Section')
#         # print(f'({self.xm2:{fmt}}, {self.xm3:{fmt}})')
#         print('({:{fmt}}, {:{fmt}})'.format(self.xm2, self.xm3, fmt=fmt))
#         print()
#         print('The Mass Properties with respect to Principal Inertial Axes')
#         # print(f'Mass per unit span = {self.mu:{fmt}}')
#         print('Mass per unit span = {:{fmt}}'.format(self.mu, fmt=fmt))
#         # print(f'Mass moments of innertia i11 = {self.i11:{fmt}}')
#         print('Mass moments of innertia i11 = {:{fmt}}'.format(self.i11, fmt=fmt))
#         # print(f'Principle mass moments of innertia i22 = {self.i22:{fmt}}')
#         print('Principle mass moments of innertia i22 = {:{fmt}}'.format(self.i22, fmt=fmt))
#         # print(f'Principle mass moments of innertia i33 = {self.i33:{fmt}}')
#         print('Principle mass moments of innertia i33 = {:{fmt}}'.format(self.i33, fmt=fmt))
#         # print(f'The principal inertial axes rotation = {self.phi_pia:{fmt}}')
#         print('The principal inertial axes rotation = {:{fmt}}'.format(self.phi_pia, fmt=fmt))
#         # print(f'The mass-weighted radius of gyration = {self.rg:{fmt}}')
#         print('The mass-weighted radius of gyration = {:{fmt}}'.format(self.rg, fmt=fmt))
#         print()
#         print('Classical Stiffness Matrix (1-extension; 2-twist; 3,4-bending)')
#         print(utio.matrixToString(self.stff, fmt=fmt))
#         print('Classical Flexibility Matrix (1-extension; 2-twist; 3,4-bending)')
#         print(utio.matrixToString(self.cmpl, fmt=fmt))
#         print()
#         print('The Tension Center of the Cross-Section')
#         # print(f'({self.xt2:{fmt}}, {self.xt3:{fmt}})')
#         print('({:{fmt}}, {:{fmt}})'.format(self.xt2, self.xt3, fmt=fmt))
#         print()
#         # print(f'The extension stiffness EA = {self.ea:{fmt}}')
#         print('The extension stiffness EA = {:{fmt}}'.format(self.ea, fmt=fmt))
#         # print(f'The torsional stiffness GJ = {self.gj:{fmt}}')
#         print('The torsional stiffness GJ = {:{fmt}}'.format(self.gj, fmt=fmt))
#         # print(f'Principal bending stiffness EI22 = {self.ei22:{fmt}}')
#         print('Principal bending stiffness EI22 = {:{fmt}}'.format(self.ei22, fmt=fmt))
#         # print(f'Principal bending stiffness EI33 = {self.ei33:{fmt}}')
#         print('Principal bending stiffness EI33 = {:{fmt}}'.format(self.ei33, fmt=fmt))
#         # print(f'The principal bending axes rotation = {self.phi_pba:{fmt}}')
#         print('The principal bending axes rotation = {:{fmt}}'.format(self.phi_pba, fmt=fmt))
#         print()
#         print('Timoshenko Stiffness Matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)')
#         print(utio.matrixToString(self.stff_t, fmt=fmt))
#         print('Timoshenko Flexibility Matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)')
#         print(utio.matrixToString(self.cmpl_t, fmt=fmt))
#         print()
#         print('The Generalized Shear Center of the Cross-Section')
#         # print(f'({self.xs2:{fmt}}, {self.xs3:{fmt}})')
#         print('({:{fmt}}, {:{fmt}})'.format(self.xs2, self.xs3, fmt=fmt))
#         print()
#         # print(f'Principal shear stiffness GA22 = {self.ga22:{fmt}}')
#         print('Principal shear stiffness GA22 = {:{fmt}}'.format(self.ga22, fmt=fmt))
#         # print(f'Principal shear stiffness GA33 = {self.ga33:{fmt}}')
#         print('Principal shear stiffness GA33 = {:{fmt}}'.format(self.ga33, fmt=fmt))
#         # print(f'The principal shear axes rotation = {self.phi_psa:{fmt}}')
#         print('The principal shear axes rotation = {:{fmt}}'.format(self.phi_psa, fmt=fmt))


#     def get(self, name):
#         """Get beam properties using specific names.

#         Parameters
#         ----------
#         name : str
#             Name of the property that will be returned.

#         Returns
#         -------
#         float:
#             Value of the specified beam property.

#         Notes
#         -----

#         ..  list-table:: Inertial properties
#             :header-rows: 1

#             * - Name
#               - Description
#             * - ``msijo`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 mass matrix at the origin
#             * - ``msijc`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 mass matrix at the mass center
#             * - ``mu``
#               - Mass per unit length
#             * - ``mmoi1`` | ``mmoi2`` | ``mmoi3``
#               - Mass moment of inertia about x1/x2/x3 axis

#         ..  list-table:: Stiffness properties
#             :header-rows: 1

#             * - Name
#               - Description
#             * - ``stfijc`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 4x4 classical stiffness matrix
#             * - ``stfijr`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 refined stiffness matrix
#             * - ``eac`` | ``ear``
#               - Axial stiffness of the classical/refined model
#             * - ``gjc`` | ``gjr``
#               - Torsional stiffness of the classical/refined model
#             * - ``ei2c`` | ``eifc`` | ``ei2r`` | ``eifr``
#               - Bending stiffness around x2 (flapwise) of the classical/refined model
#             * - ``ei3c`` | ``eicc`` | ``ei3r`` | ``eicr``
#               - Bending stiffness around x3 (chordwise or lead-lag) of the classical/refined model
#             * - ``cmpijc`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 4x4 classical compliance matrix
#             * - ``cmpijr`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 refined compliance matrix

#         ..  list-table:: Center offsets
#             :header-rows: 1

#             * - Name
#               - Description
#             * - ``mcy`` | ``mc2``
#               - y (or x2) component of the mass center
#             * - ``mcz`` | ``mc3``
#               - z (or x3) component of the mass center
#             * - ``tcy`` | ``tc2``
#               - y (or x2) component of the tension center
#             * - ``tcz`` | ``tc3``
#               - z (or x3) component of the tension center
#             * - ``scy`` | ``sc2``
#               - y (or x2) component of the shear center
#             * - ``scz`` | ``sc3``
#               - z (or x3) component of the shear center

#         .

#         """

#         if isinstance(name, str):
#             name = name.lower()

#             # Mass
#             if name.startswith('ms'):
#                 return self.mass[int(name[2])-1][int(name[3])-1]
#             if name == 'mu':
#                 return self.mu
#             if name == 'mmoi1':
#                 return self.i11
#             if name == 'mmoi2':
#                 return self.i22
#             if name == 'mmoi3':
#                 return self.i33

#             # Stiffness
#             if name.startswith('stf'):
#                 if name[-1] == 'c':
#                     return self.stff[int(name[3])-1][int(name[4])-1]
#                 elif name[-1] == 'r':
#                     return self.stff_t[int(name[3])-1][int(name[4])-1]

#             # Compliance
#             if name.startswith('cmp'):
#                 if name[-1] == 'c':
#                     return self.cmpl[int(name[3])-1][int(name[4])-1]
#                 elif name[-1] == 'r':
#                     return self.cmpl_t[int(name[3])-1][int(name[4])-1]

#             if name == 'ea':
#                 return self.ea
#             if name in ['ga22', 'gayy', 'ga2', 'gay']:
#                 return self.ga22
#             if name in ['ga33', 'gazz', 'ga3', 'gaz']:
#                 return self.ga33
#             if name == 'gj':
#                 return self.gj
#             if name in ['ei22', 'eiyy', 'ei2', 'eiy']:
#                 return self.ei22
#             if name in ['ei33', 'eizz', 'ei3', 'eiz']:
#                 return self.ei33

#             # Various centers
#             if name == 'mcy' or name == 'mc2':
#                 return self.xm2
#             if name == 'mcz' or name == 'mc3':
#                 return self.xm3
#             if name == 'tcy' or name == 'tc2':
#                 return self.xt2
#             if name == 'tcz' or name == 'tc3':
#                 return self.xt3
#             if name == 'scy' or name == 'sc2':
#                 return self.xs2
#             if name == 'scz' or name == 'sc3':
#                 return self.xs3

#         elif isinstance(name, list) or isinstance(name, tuple):
#             props = []
#             for n in name:
#                 props.append(self.get(n))
#             return props


#     def getAll(self):
#         """Get all beam properties.

#         Returns
#         -------
#         dict:
#             A Dictionary of all beam properties.

#         Notes
#         -----

#         Names are

#         - mu, mmoi1, mmoi2, mmoi3
#         - ea, ga22, ga33, gj, ei22, ei33
#         - mc2, mc3, tc2, tc3, sc2, sc3
#         - msij, stfijc, cmpijc, stfijr, cmpijr

#         """
#         names = [
#             'mu', 'mmoi1', 'mmoi2', 'mmoi3',
#             'ea', 'ga22', 'ga33', 'gj', 'ei22', 'ei33',
#             'mc2', 'mc3', 'tc2', 'tc3', 'sc2', 'sc3'
#         ]
#         for i in range(4):
#             for j in range(4):
#                 names.append('stf{}{}c'.format(i+1, j+1))
#                 names.append('cmp{}{}c'.format(i+1, j+1))
#         for i in range(6):
#             for j in range(6):
#                 names.append('ms{}{}'.format(i+1, j+1))
#                 names.append('stf{}{}r'.format(i+1, j+1))
#                 names.append('cmp{}{}r'.format(i+1, j+1))

#         dict_prop = {}
#         for n in names:
#             dict_prop[n] = self.get(n)

#         return dict_prop









# import copy
# import numpy as np
# import sgio.utils.io as utio

# from .general import MaterialSection


# class BeamProperty(MaterialSection):
#     """A beam property class (smdim = 1)

#     """

#     def __init__(self):
#         MaterialSection.__init__(self, smdim=1)

#         #: float: Geometric center location in x2 direction
#         self.xg2 = 0.
#         #: float: Geometric center location in x3 direction
#         self.xg3 = 0.

#         #: float: Area of the cross-section
#         self.area = 0.


#         # Inertial properties
#         # -------------------

#         #: list of list of floats:
#         #: The 6x6 mass matrix
#         self.mass = []

#         #: list of lists of floats:
#         #: The 6x6 mass matrix at the mass center
#         self.mass_cs = []

#         #: float: Mass center location in x2 direction
#         self.xm2 = 0.
#         #: float: Mass center location in x3 direction
#         self.xm3 = 0.

#         #: float: Mass per unit span
#         self.mu = 0.
#         #: float: Mass moments of inertia i11
#         self.i11 = 0.
#         #: float: Principal mass moments of inertia i22
#         self.i22 = 0.
#         #: float: Principle mass moments of inertia i33
#         self.i33 = 0.
#         #: float: Principal inertial axes rotation angle in degree
#         self.phi_pia = 0.
#         #: float: mass-weighted radius of gyration
#         self.rg = 0.


#         # Structural properties
#         # ---------------------

#         #: list of lists of floats:
#         #: Classical stiffness matrix (1-extension; 2-twist; 3,4-bending)
#         self.stff = []
#         #: list of lists of floats:
#         #: Classical compliance matrix (1-extension; 2-twist; 3,4-bending)
#         self.cmpl = []

#         #: float: Tension center location in x2 direction
#         self.xt2 = 0.
#         #: float: Tension center location in x3 direction
#         self.xt3 = 0.

#         #: float: Extension stiffness EA
#         self.ea = 0.
#         #: float: Torsional stiffness GJ
#         self.gj = 0.
#         #: float: Principal bending stiffness EI22
#         self.ei22 = 0.
#         #: float: Principal bending stiffness EI33
#         self.ei33 = 0.
#         #: float: Principle bending axes rotation angle in degree
#         self.phi_pba = 0.

#         #: list of lists of floats:
#         #: Timoshenko stiffness matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
#         self.stff_t = []
#         #: list of lists of floats:
#         #: Timoshenko compliance matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)
#         self.cmpl_t = []

#         #: float: Generalized shear center location in x2 direction
#         self.xs2 = 0.
#         #: float: Generalized shear center location in x3 direction
#         self.xs3 = 0.
#         #: float: Principal shear stiffness GA22
#         self.ga22 = 0.
#         #: float: Principal shear stiffness GA33
#         self.ga33 = 0.
#         #: float: Principal shear axes rotation angle in degree
#         self.phi_psa = 0.


#     def printData(self):
#         fmt = '20.10E'
#         print('Summary')
#         print()
#         print('The 6x6 mass matrix')
#         print(utio.matrixToString(self.mass, fmt=fmt))
#         print()
#         print('The Mass Center of the Cross-Section')
#         # print(f'({self.xm2:{fmt}}, {self.xm3:{fmt}})')
#         print('({:{fmt}}, {:{fmt}})'.format(self.xm2, self.xm3, fmt=fmt))
#         print()
#         print('The Mass Properties with respect to Principal Inertial Axes')
#         # print(f'Mass per unit span = {self.mu:{fmt}}')
#         print('Mass per unit span = {:{fmt}}'.format(self.mu, fmt=fmt))
#         # print(f'Mass moments of innertia i11 = {self.i11:{fmt}}')
#         print('Mass moments of innertia i11 = {:{fmt}}'.format(self.i11, fmt=fmt))
#         # print(f'Principle mass moments of innertia i22 = {self.i22:{fmt}}')
#         print('Principle mass moments of innertia i22 = {:{fmt}}'.format(self.i22, fmt=fmt))
#         # print(f'Principle mass moments of innertia i33 = {self.i33:{fmt}}')
#         print('Principle mass moments of innertia i33 = {:{fmt}}'.format(self.i33, fmt=fmt))
#         # print(f'The principal inertial axes rotation = {self.phi_pia:{fmt}}')
#         print('The principal inertial axes rotation = {:{fmt}}'.format(self.phi_pia, fmt=fmt))
#         # print(f'The mass-weighted radius of gyration = {self.rg:{fmt}}')
#         print('The mass-weighted radius of gyration = {:{fmt}}'.format(self.rg, fmt=fmt))
#         print()
#         print('Classical Stiffness Matrix (1-extension; 2-twist; 3,4-bending)')
#         print(utio.matrixToString(self.stff, fmt=fmt))
#         print('Classical Flexibility Matrix (1-extension; 2-twist; 3,4-bending)')
#         print(utio.matrixToString(self.cmpl, fmt=fmt))
#         print()
#         print('The Tension Center of the Cross-Section')
#         # print(f'({self.xt2:{fmt}}, {self.xt3:{fmt}})')
#         print('({:{fmt}}, {:{fmt}})'.format(self.xt2, self.xt3, fmt=fmt))
#         print()
#         # print(f'The extension stiffness EA = {self.ea:{fmt}}')
#         print('The extension stiffness EA = {:{fmt}}'.format(self.ea, fmt=fmt))
#         # print(f'The torsional stiffness GJ = {self.gj:{fmt}}')
#         print('The torsional stiffness GJ = {:{fmt}}'.format(self.gj, fmt=fmt))
#         # print(f'Principal bending stiffness EI22 = {self.ei22:{fmt}}')
#         print('Principal bending stiffness EI22 = {:{fmt}}'.format(self.ei22, fmt=fmt))
#         # print(f'Principal bending stiffness EI33 = {self.ei33:{fmt}}')
#         print('Principal bending stiffness EI33 = {:{fmt}}'.format(self.ei33, fmt=fmt))
#         # print(f'The principal bending axes rotation = {self.phi_pba:{fmt}}')
#         print('The principal bending axes rotation = {:{fmt}}'.format(self.phi_pba, fmt=fmt))
#         print()
#         print('Timoshenko Stiffness Matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)')
#         print(utio.matrixToString(self.stff_t, fmt=fmt))
#         print('Timoshenko Flexibility Matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)')
#         print(utio.matrixToString(self.cmpl_t, fmt=fmt))
#         print()
#         print('The Generalized Shear Center of the Cross-Section')
#         # print(f'({self.xs2:{fmt}}, {self.xs3:{fmt}})')
#         print('({:{fmt}}, {:{fmt}})'.format(self.xs2, self.xs3, fmt=fmt))
#         print()
#         # print(f'Principal shear stiffness GA22 = {self.ga22:{fmt}}')
#         print('Principal shear stiffness GA22 = {:{fmt}}'.format(self.ga22, fmt=fmt))
#         # print(f'Principal shear stiffness GA33 = {self.ga33:{fmt}}')
#         print('Principal shear stiffness GA33 = {:{fmt}}'.format(self.ga33, fmt=fmt))
#         # print(f'The principal shear axes rotation = {self.phi_psa:{fmt}}')
#         print('The principal shear axes rotation = {:{fmt}}'.format(self.phi_psa, fmt=fmt))


#     def get(self, name):
#         """Get beam properties using specific names.

#         Parameters
#         ----------
#         name : str
#             Name of the property that will be returned.

#         Returns
#         -------
#         float:
#             Value of the specified beam property.

#         Notes
#         -----

#         ..  list-table:: Inertial properties
#             :header-rows: 1

#             * - Name
#               - Description
#             * - ``msijo`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 mass matrix at the origin
#             * - ``msijc`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 mass matrix at the mass center
#             * - ``mu``
#               - Mass per unit length
#             * - ``mmoi1`` | ``mmoi2`` | ``mmoi3``
#               - Mass moment of inertia about x1/x2/x3 axis

#         ..  list-table:: Stiffness properties
#             :header-rows: 1

#             * - Name
#               - Description
#             * - ``stfijc`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 4x4 classical stiffness matrix
#             * - ``stfijr`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 refined stiffness matrix
#             * - ``eac`` | ``ear``
#               - Axial stiffness of the classical/refined model
#             * - ``gjc`` | ``gjr``
#               - Torsional stiffness of the classical/refined model
#             * - ``ei2c`` | ``eifc`` | ``ei2r`` | ``eifr``
#               - Bending stiffness around x2 (flapwise) of the classical/refined model
#             * - ``ei3c`` | ``eicc`` | ``ei3r`` | ``eicr``
#               - Bending stiffness around x3 (chordwise or lead-lag) of the classical/refined model
#             * - ``cmpijc`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 4x4 classical compliance matrix
#             * - ``cmpijr`` (``i``, ``j`` are numbers 1 to 6)
#               - Entry (i, j) of the 6x6 refined compliance matrix

#         ..  list-table:: Center offsets
#             :header-rows: 1

#             * - Name
#               - Description
#             * - ``mcy`` | ``mc2``
#               - y (or x2) component of the mass center
#             * - ``mcz`` | ``mc3``
#               - z (or x3) component of the mass center
#             * - ``tcy`` | ``tc2``
#               - y (or x2) component of the tension center
#             * - ``tcz`` | ``tc3``
#               - z (or x3) component of the tension center
#             * - ``scy`` | ``sc2``
#               - y (or x2) component of the shear center
#             * - ``scz`` | ``sc3``
#               - z (or x3) component of the shear center

#         .

#         """

#         # mm = self.mass_origin
#         # stf_c = self.stiffness
#         # cmp_c = self.compliance
#         # stf_r = self.stiffness_refined
#         # cmp_r = self.compliance_refined

#         # if type(center).__name__ == 'str':
#         #     if center == 'tc':
#         #         mm, stf_c, cmp_c, stf_r, cmp_r = calcOffsetBeamProperty(self.tension_center[1], self.tension_center[2])
#         #     elif center == 'sc':
#         #         mm, stf_c, cmp_c, stf_r, cmp_r = calcOffsetBeamProperty(self.shear_center[1], self.shear_center[2])
#         #     elif center == 'mc':
#         #         mm, stf_c, cmp_c, stf_r, cmp_r = calcOffsetBeamProperty(self.mass_center[1], self.mass_center[2])

#         if isinstance(name, str):
#             name = name.lower()

#             # Mass
#             if name.startswith('ms'):
#                 return self.mass[int(name[2])-1][int(name[3])-1]
#             if name == 'mu':
#                 return self.mu
#             if name == 'mmoi1':
#                 return self.i11
#             if name == 'mmoi2':
#                 return self.i22
#             if name == 'mmoi3':
#                 return self.i33

#             # Stiffness
#             if name.startswith('stf'):
#                 if name[-1] == 'c':
#                     return self.stff[int(name[3])-1][int(name[4])-1]
#                 elif name[-1] == 'r':
#                     return self.stff_t[int(name[3])-1][int(name[4])-1]

#             # Compliance
#             if name.startswith('cmp'):
#                 if name[-1] == 'c':
#                     return self.cmpl[int(name[3])-1][int(name[4])-1]
#                 elif name[-1] == 'r':
#                     return self.cmpl_t[int(name[3])-1][int(name[4])-1]

#             if name == 'ea':
#                 return self.ea
#             if name in ['ga22', 'gayy', 'ga2', 'gay']:
#                 return self.ga22
#             if name in ['ga33', 'gazz', 'ga3', 'gaz']:
#                 return self.ga33
#             if name == 'gj':
#                 return self.gj
#             if name in ['ei22', 'eiyy', 'ei2', 'eiy']:
#                 return self.ei22
#             if name in ['ei33', 'eizz', 'ei3', 'eiz']:
#                 return self.ei33

#             # Various centers
#             if name == 'mcy' or name == 'mc2':
#                 return self.xm2
#             if name == 'mcz' or name == 'mc3':
#                 return self.xm3
#             if name == 'tcy' or name == 'tc2':
#                 return self.xt2
#             if name == 'tcz' or name == 'tc3':
#                 return self.xt3
#             if name == 'scy' or name == 'sc2':
#                 return self.xs2
#             if name == 'scz' or name == 'sc3':
#                 return self.xs3

#         elif isinstance(name, list) or isinstance(name, tuple):
#             props = []
#             for n in name:
#                 props.append(self.get(n))
#             return props


#     def getAll(self):
#         """Get all beam properties.

#         Returns
#         -------
#         dict:
#             A Dictionary of all beam properties.

#         Notes
#         -----

#         Names are

#         - mu, mmoi1, mmoi2, mmoi3
#         - ea, ga22, ga33, gj, ei22, ei33
#         - mc2, mc3, tc2, tc3, sc2, sc3
#         - msij, stfijc, cmpijc, stfijr, cmpijr

#         """
#         names = [
#             'mu', 'mmoi1', 'mmoi2', 'mmoi3',
#             'ea', 'ga22', 'ga33', 'gj', 'ei22', 'ei33',
#             'mc2', 'mc3', 'tc2', 'tc3', 'sc2', 'sc3'
#         ]
#         for i in range(4):
#             for j in range(4):
#                 names.append('stf{}{}c'.format(i+1, j+1))
#                 names.append('cmp{}{}c'.format(i+1, j+1))
#         for i in range(6):
#             for j in range(6):
#                 names.append('ms{}{}'.format(i+1, j+1))
#                 names.append('stf{}{}r'.format(i+1, j+1))
#                 names.append('cmp{}{}r'.format(i+1, j+1))

#         dict_prop = {}
#         for n in names:
#             dict_prop[n] = self.get(n)

#         return dict_prop


#     def calcPropertyAt(self, new_origin):
#         """Offset the beam reference center and recalculate beam properties.

#         Parameters
#         ----------
#         offset_x2 : float
#             x2 of the offset of the new center with respect to the current one.
#         offset_x3 : float
#             x3 of the offset of the new center with respect to the current one.

#         """

#         bp_new = copy.copy(self)

#         # offset = [0.0, offset[0], offset[1]]
#         if isinstance(new_origin, str):
#             if new_origin == 'gc':
#                 offset_x2 = self.xg2
#                 offset_x3 = self.xg3
#             elif new_origin == 'mc':
#                 offset_x2 = self.xm2
#                 offset_x3 = self.xm3
#             elif new_origin == 'tc':
#                 offset_x2 = self.xt2
#                 offset_x3 = self.xt3
#             elif new_origin == 'sc':
#                 offset_x2 = self.xs2
#                 offset_x3 = self.xs3
#         else:
#             offset_x2 = new_origin[0]
#             offset_x3 = new_origin[1]

#         bp_new.xg2 -= offset_x2
#         bp_new.xg3 -= offset_x3

#         # Offset mass matrix
#         mm_o = np.asarray(self.mass_cs)
#         if (offset_x2 != self.xm2) or (offset_x3 != self.xm3):
#             # mm_c = np.asarray(self.mass_mc)
#             mu = mm_o[0, 0]
#             mi_c = mm_o[3:, 3:]

#             x2 = self.xm2 - offset_x2
#             x3 = self.xm3 - offset_x3
#             r_tilde = np.array([
#                 [0, -x3, x2],
#                 [x3, 0, 0],
#                 [-x2, 0, 0]
#             ])

#             mm_o[:3, 3:] = mu * r_tilde.T
#             mm_o[3:, :3] = mu * r_tilde

#             # I_o = I_c + m * r_tilde.r_tilde^T
#             mm_o[3:, 3:] = mm_o[3:, 3:] + mu * np.dot(r_tilde, r_tilde.T)
#         bp_new.mass = mm_o
#         bp_new.xm2 -= offset_x2
#         bp_new.xm3 -= offset_x3


#         # Offset stiffness and compliance
#         trfm_4 = np.eye(4)
#         trfm_6 = np.eye(6)

#         trfm_4[2, 0] = offset_x3
#         trfm_4[3, 0] = -offset_x2

#         trfm_6[4, 0] = offset_x3
#         trfm_6[5, 0] = -offset_x2
#         trfm_6[3, 1] = -offset_x3
#         trfm_6[3, 2] = offset_x2

#         cmp_4 = np.asarray(self.cmpl)
#         cmp_6 = np.asarray(self.cmpl_t)

#         bp_new.cmpl = np.dot(trfm_4.T, np.dot(cmp_4, trfm_4))
#         bp_new.cmpl_t = np.dot(trfm_6.T, np.dot(cmp_6, trfm_6))

#         bp_new.stff = np.linalg.inv(bp_new.cmpl)
#         bp_new.stff_t = np.linalg.inv(bp_new.cmpl_t)

#         bp_new.xt2 -= offset_x2
#         bp_new.xt3 -= offset_x3

#         bp_new.xs2 -= offset_x2
#         bp_new.xs3 -= offset_x3

#         return bp_new


#     def writeToFile(self, fn, fmt='vabs'):
#         with open(fn, 'w') as fo:
#             if fmt.startswith('v'):
#                 self.writeToFileVABS(fo)

#         return


#     def writeToFileVABS(self, fo):
#         fmt_float = '20.10E'

#         fo.write('\n The 6X6 Mass Matrix\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloatsMatrix(fo, self.mass, fmt=fmt_float, indent=1)

#         fo.write('\n The Mass Center of the Cross Section\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloats(fo, (self.xm2, self.xm3), fmt=fmt_float, indent=1)

#         fo.write('\n The 6X6 Mass Matrix at the Mass Center\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloatsMatrix(fo, self.mass_cs, fmt='20.12E', indent=1)

#         fo.write('\n The Mass Properties with respect to Principal Inertial Axes\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         fo.write(' {:39s}={:20.10E}\n'.format('Mass per unit span', self.mu))
#         fo.write(' {:39s}={:20.10E}\n'.format('Mass moment of inertia i11', self.i11))
#         fo.write(' {:39s}={:20.10E}\n'.format('Principal mass moments of inertia i22', self.i22))
#         fo.write(' {:39s}={:20.10E}\n'.format('Principal mass moments of inertia i33', self.i33))
#         fo.write(' The principal inertial axes rotated from user coordinate system by {} degrees about the positive direction of x1 axis.\n'.format(self.phi_pia))
#         fo.write(' {:39s}={:20.10E}\n'.format('The mass-weighted radius of gyration', self.rg))

#         fo.write('\n The Geometric Center of the Cross Section\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloats(fo, (self.xg2, self.xg3), fmt=fmt_float, indent=1)

#         fo.write('\n The Area of the Cross Section\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         fo.write(' Area ={:20.10E}\n'.format(self.area))

#         fo.write('\n Classical Stiffness Matrix (1-extension; 2-twist; 3,4-bending)\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloatsMatrix(fo, self.stff, fmt='20.10E', indent=1)

#         fo.write('\n Classical Compliance Matrix (1-extension; 2-twist; 3,4-bending)\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloatsMatrix(fo, self.cmpl, fmt='20.10E', indent=1)

#         fo.write('\n The Tension Center of the Cross Section\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloats(fo, (self.xt2, self.xt3), fmt=fmt_float, indent=1)

#         fo.write('\n')
#         fo.write(' {:34s}={:20.10E}\n'.format('The extension stiffness EA', self.ea))
#         fo.write(' {:34s}={:20.10E}\n'.format('The torsional stiffness GJ', self.gj))
#         fo.write(' {:34s}={:20.10E}\n'.format('Principal bending stiffness EI22', self.ei22))
#         fo.write(' {:34s}={:20.10E}\n'.format('Principal bending stiffness EI33', self.ei33))
#         fo.write(' The principal bending axes rotated from the user coordinate system by {} degrees about the positive direction of x1 axis.\n'.format(self.phi_pba))

#         fo.write('\n Timoshenko Stiffness Matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloatsMatrix(fo, self.stff_t, fmt=fmt_float, indent=1)

#         fo.write('\n Timoshenko Compliance Matrix (1-extension; 2,3-shear, 4-twist; 5,6-bending)\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloatsMatrix(fo, self.cmpl_t, fmt=fmt_float, indent=1)

#         fo.write('\n The Shear Center of the Cross Section in the User Coordinate System\n')
#         fo.write(' '+'='*56)
#         fo.write('\n\n')
#         utio.writeFormatFloats(fo, (self.xs2, self.xs3), fmt=fmt_float, indent=1)

#         fo.write('\n')
#         fo.write(' {:31s}={:20.10E}\n'.format('Principal shear stiffness GA22', self.ga22))
#         fo.write(' {:31s}={:20.10E}\n'.format('Principal shear stiffness GA33', self.ga33))
#         fo.write(' The principal shear axes rotated from user coordinate system by {} degrees about the positive direction of x1 axis.\n'.format(self.phi_psa))

#         return
