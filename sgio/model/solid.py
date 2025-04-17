from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from numbers import Number

def initConstantName():
    return ['e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu12', 'nu13', 'nu23']

def initConstantLabel():
    return ['E1', 'E2', 'E3', 'G12', 'G13', 'G23', 'nu12', 'nu13', 'nu23']

def initStrengthName():
    return ['x1t', 'x2t', 'x3t', 'x1c', 'x2c', 'x3c', 'x23', 'x13', 'x12']

def initStrengthLabel():
    return ['X1t', 'X2t', 'X3t', 'X1c', 'X2c', 'X3c', 'X23', 'X13', 'X12']

@dataclass
class CauchyContinuumProperty:
    density:float = 0

    isotropy:int = 0
    """Isotropy type.

    * 0: Isotropic
    * 1: Orthotropic
    * 2: Anisotropic
    """

    # Stiffness properties
    stff:Iterable[Iterable[float]] = None
    cmpl:Iterable[Iterable[float]] = None

    constant_name:Iterable[str] = field(default_factory=initConstantName)
    constant_label:Iterable[str] = field(default_factory=initConstantLabel)

    e1:float = None
    e2:float = None
    e3:float = None
    g12:float = None
    g13:float = None
    g23:float = None
    nu12:float = None
    nu13:float = None
    nu23:float = None

    # Strength properties
    strength_name:Iterable[str] = field(default_factory=initStrengthName)
    strength_label:Iterable[str] = field(default_factory=initStrengthLabel)

    x1t:float = None  # xt
    x2t:float = None  # yt
    x3t:float = None  # zt
    x1c:float = None  # xc
    x2c:float = None  # yc
    x3c:float = None  # zc
    x23:float = None  # r
    x13:float = None  # t
    x12:float = None  # s

    strength_measure = 0  # 0: stress, 1: strain

    strength_constants:Iterable[float] = None

    char_len:float = 0

    cte:Iterable[float] = None
    specific_heat:float = 0

    def __repr__(self) -> str:
        s = [
            f'density = {self.density}',
            f'isotropy = {self.isotropy}'
        ]

        s.append('-'*20)
        s.append('stiffness matrix')
        if not self.stff is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.stff[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('compliance matrix')
        if not self.cmpl is None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.cmpl[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('-'*20)
        s.append('engineering constants')
        for _label, _name in zip(self.constant_label, self.constant_name):
            _value = eval(f'self.{_name}')
            s.append(f'{_label} = {_value}')

        s.append('-'*20)
        s.append('strength')
        for _label, _name in zip(self.strength_label, self.strength_name):
            _value = eval(f'self.{_name}')
            s.append(f'{_label} = {_value}')

        s.append('-'*20)
        s.append('cte')
        if not self.cte is None:
            s.append('  '.join(list(map(str, self.cte))))
        else:
            s.append('NONE')

        return '\n'.join(s)




class CauchyContinuumModel:
    """Cauchy continuum model
    """

    dim = 3
    model_name = 'Cauchy continuum model'
    strain_name = ['e11', 'e22', 'e33', 'e23', 'e13', 'e12']
    stress_name = ['s11', 's22', 's33', 's23', 's13', 's12']

    def __init__(self, name:str=''):

        self.name = name
        self.id = None

        self.property = CauchyContinuumProperty()

        # Inertial
        # --------

        # self.density : float = None
        self.temperature : float = 0

        # self.strength_constants : Iterable = None
        self.failure_criterion = 0

        # Thermal
        # -------

        # self.cte : Iterable[float] = None
        # self.specific_heat : float = 0

        self.d_thetatheta : float = 0
        self.f_eff : float = 0


    def __repr__(self) -> str:
        s = [
            self.model_name,
            '-'*len(self.model_name),
            # f'density = {self.density}',
            # f'isotropy = {self.isotropy}'
        ]

        s.append(str(self.property))

        s.append(f'failure criterion = {self.failure_criterion}')

        return '\n'.join(s)


    def __eq__(self, m2):
        return self.property == m2.property


    def __call__(self, x):
        return


    def get(self, name:str):
        """Get material properties.

        Parameters
        -----------
        name : str
            Name of the property that will be returned.

        Returns
        ---------
        int or float or :obj:`Iterable`:
            Value of the specified beam property.

        Notes
        -------

        ..  list-table:: Properties
            :header-rows: 1

            * - ``name``
              - Description
            * - density
              - Density of the material
            * - temperature
              -
            * - isotropy
              - Isotropy of the material
            * - e
              - Young's modulus of isotropic materials
            * - nu
              - Poisson's ratio of isotropic materials
            * - e1 | e2 | e3
              - Modulus of elasticity in material direction 1, 2, or 3
            * - nu12 | nu13 | nu23
              - Poisson's ratio in material plane 1-2, 1-3, or 2-3
            * - g12 | g13 | g23
              - Shear modulus in material plane 1-2, 1-3, or 2-3
            * - c
              - 6x6 stiffness matrix
            * - cij (i, j = 1 to 6)
              - Component (i, j) of the stiffness matrix
            * - s
              - 6x6 compliance matrix
            * - sij (i, j = 1 to 6)
              - Component (i, j) of the compliance matrix
            * - strength
              -
            * - alpha
              - CTE of isotropic materials
            * - alpha11 | alpha22 | alpha33 | alpha12 | alpha13 | alpha23
              - The 11, 22, 33, 12, 13, or 23 component of CTE
            * - specific_heat
              -
        """

        v = None

        if name == 'density':
            v = self.property.density
        elif name == 'temperature':
            v = self.temperature
        elif name == 'isotropy':
            v = self.property.isotropy

        # Stiffness
        elif name == 'e':
            v = self.property.e1
        elif name == 'nu':
            v = self.property.nu12
        elif name in ['e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu12', 'nu13', 'nu23']:
            v = eval(f'self.property.{name}')

        elif name == 'c':
            v = self.property.stff
        elif name == 's':
            v = self.property.cmpl

        # Strength
        elif name == 'x':
            v = self.property.x1t
        elif name in ['x1t', 'x2t', 'x3t', 'x1c', 'x2c', 'x3c', 'x23', 'x13', 'x12']:
            v = eval(f'self.property.{name}')
        elif name == 'strength':
            v = self.property.strength_constants
        elif name == 'char_len':
            v = self.property.char_len
        elif name == 'failure_criterion':
            v = self.failure_criterion

        # Thermal
        elif name == 'cte':
            v = self.property.cte
        elif name == 'specific_heat':
            v = self.property.specific_heat

        elif name.startswith('alpha'):
            if name == 'alpha':
                v = self.property.cte[0]
            else:
                _ij = name[-2:]
                for _k, __ij in enumerate(['11', '22', '33', '23', '13', '12']):
                    if _ij == __ij:
                        v = self.property.cte[_k]
                        break
        elif name.startswith('c'):
            _i = int(name[1]) - 1
            _j = int(name[2]) - 1
            v = self.property.stff[_i][_j]
        elif name.startswith('s'):
            _i = int(name[1]) - 1
            _j = int(name[2]) - 1
            v = self.property.cmpl[_i][_j]

        return v


    def set(self, name:str, value, **kwargs):
        """Set material properties.

        Parameters
        ------------
        name : str
            Name of the property that will be set.

        value : str or int or float
            Value of the property that will be set.

        """
        if name == 'isotropy':
            if isinstance(value, str):
                if value.startswith('iso'):
                    self.property.isotropy = 0
                elif value.startswith('ortho') or value.startswith('eng') or value.startswith('lam'):
                    self.property.isotropy = 1
                elif value.startswith('aniso'):
                    self.property.isotropy = 2
                else:
                    self.property.isotropy = int(value)
            elif isinstance(value, int):
                self.property.isotropy = value

        elif name == 'elastic':
            self.setElastic(value, **kwargs)

        elif name == 'strength_constants':
            if len(value) == 9:
                self.property.x1t = value[0]
                self.property.x2t = value[1]
                self.property.x3t = value[2]
                self.property.x1c = value[3]
                self.property.x2c = value[4]
                self.property.x3c = value[5]
                self.property.x23 = value[6]
                self.property.x13 = value[7]
                self.property.x12 = value[8]

            self.property.strength_constants = value

        else:
            exec(f'self.property.{name} = {value}')

        return


    def setElastic(self, consts:Iterable, input_type='', **kwargs):
        if self.property.isotropy == 0:
            self.property.e1 = float(consts[0])
            self.property.nu12 = float(consts[1])

        elif self.property.isotropy == 1:
            if input_type == 'lamina':
                self.property.e1 = float(consts[0])
                self.property.e2 = float(consts[1])
                self.property.g12 = float(consts[2])
                self.property.nu12 = float(consts[3])
                self.property.e3 = self.property.e2
                self.property.g13 = self.property.g12
                self.property.nu13 = self.property.nu12
                self.property.nu23 = 0.3
                self.property.g23 = self.property.e3 / (2.0 * (1 + self.property.nu23))
            elif input_type == 'engineering':
                self.property.e1, self.property.e2, self.property.e3 = list(map(float, consts[:3]))
                self.property.g12, self.property.g13, self.property.g23 = list(map(float, consts[3:6]))
                self.property.nu12, self.property.nu13, self.property.nu23 = list(map(float, consts[6:]))
            elif input_type == 'orthotropic':  # TODO
                pass
            else:
                self.property.e1, self.property.e2, self.property.e3 = list(map(float, consts[:3]))
                self.property.g12, self.property.g13, self.property.g23 = list(map(float, consts[3:6]))
                self.property.nu12, self.property.nu13, self.property.nu23 = list(map(float, consts[6:]))

        elif self.property.isotropy == 2:
            if input_type == 'stiffness':
                self.property.stff = consts
            elif input_type == 'compliance':
                self.property.cmpl = consts

        return










# Legacy

# from .general import MaterialSection

# class MaterialProperty(MaterialSection):
#     """
#     """

#     def __init__(self, name=''):
#         MaterialSection.__init__(self, 3)
#         self.name = name

#         self.temperature = 0

#         #: int: (continuum model) Isotropy type.
#         #: Isotropic (0), orthotropic (1), anisotropic (2).
#         self.isotropy = None

#         self.e1 = None
#         self.e2 = None
#         self.e3 = None
#         self.g12 = None
#         self.g13 = None
#         self.g23 = None
#         self.nu12 = None
#         self.nu13 = None
#         self.nu23 = None

#         self.strength = {}

#         self.cte = []
#         self.specific_heat = 0

#         self.d_thetatheta = 0
#         self.f_eff = 0


#     def __repr__(self):
#         s = [
#             f'density = {self.density}',
#         ]

#         if self.isotropy == 0:
#             s.append('isotropic')
#             s.append(f'E = {self.e1}, v = {self.nu12}')
#         elif self.isotropy == 1:
#             s.append('orthotropic')
#             s.append(f'E1 = {self.e1}, E2 = {self.e2}, E3 = {self.e3}')
#             s.append(f'G12 = {self.g12}, G13 = {self.g13}, G23 = {self.g23}')
#             s.append(f'v12 = {self.nu12}, v13 = {self.nu13}, v23 = {self.nu23}')
#         elif self.isotropy == 2:
#             s.append('anisotropic')
#             for i in range(6):
#                 _row = []
#                 for j in range(i, 6):
#                     _row.append(f'C{i+1}{j+1} = {self.stff[i][j]}')
#                 s.append(', '.join(_row))

#         return '\n'.join(s)


#     def summary(self):
#         stype = 'isotropic'
#         sprop = [['e = {0}'.format(self.e1),], ['nu = {0}'.format(self.nu12),]]
#         if self.isotropy == 1:
#             stype = 'orthotropic'
#             sprop = [
#                 ['e1 = {0}'.format(self.e1), 'e2 = {0}'.format(self.e2), 'e3 = {0}'.format(self.e3)],
#                 ['g12 = {0}'.format(self.g12), 'g13 = {0}'.format(self.g13), 'g23 = {0}'.format(self.g23)],
#                 ['nu12 = {0}'.format(self.nu12), 'nu13 = {0}'.format(self.nu13), 'nu23 = {0}'.format(self.nu23)]
#             ]
#         elif self.isotropy == 2:
#             stype = 'anisotropic'
#         print('type:', stype)
#         print('density =', self.density)
#         print('elastic properties:')
#         for p in sprop:
#             print(', '.join(p))
#         return


#     def get(self, name):
#         r"""
#         """
#         v = None

#         if name == 'density':
#             v = self.density

#         elif name in ['e', 'e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu', 'nu12', 'nu13', 'nu23']:
#             v = self.constants[name]

#         elif name in ['xt', 'yt', 'zt', 'xc', 'yc', 'zc', 'r', 't', 's']:
#             v = self.strength_constants[name]
#         # v = eval('self.{}'.format(name))

#         return v


#     def assignConstants(self, consts):
#         if len(consts) == 2:
#             self.isotropy = 0
#             self.e1 = float(consts[0])
#             self.nu12 = float(consts[1])
#         elif len(consts) == 9:
#             self.isotropy = 1
#             self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
#             self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
#             self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))


#     def setElasticProperty(self, consts, ctype):
#         if ctype == 'isotropic' or ctype == 0:
#             self.isotropy = 0
#             self.e1 = float(consts[0])
#             self.nu12 = float(consts[1])
#         elif ctype == 'lamina':
#             self.isotropy = 1
#             self.e1 = float(consts[0])
#             self.e2 = float(consts[1])
#             self.g12 = float(consts[2])
#             self.nu12 = float(consts[3])
#             self.e3 = self.e2
#             self.g13 = self.g12
#             self.nu13 = self.nu12
#             self.nu23 = 0.3
#             self.g23 = self.e3 / (2.0 * (1 + self.nu23))
#         elif ctype == 'engineering' or ctype == 1:
#             self.isotropy = 1
#             self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
#             self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
#             self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))
#         elif ctype == 'orthotropic':
#             self.isotropy = 1
#         elif ctype == 'anisotropic' or ctype == 2:
#             self.isotropy = 2

#         return


#     def setStrengthProperty(self, strength):
#         self.strength['constants'] = list(map(float, strength))
#         return


#     def setFailureCriterion(self, criterion):
#         if isinstance(criterion, str):
#             self.strength['criterion'] = self.FAILURE_CRITERION_NAME_TO_ID[criterion]
#         return


#     def setCharacteristicLength(self, char_len=0):
#         self.strength['chara_len'] = char_len
#         return


