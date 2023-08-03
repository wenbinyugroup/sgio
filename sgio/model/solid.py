# from dataclasses import dataclass
from typing import Iterable
from numbers import Number

# class CauchyModel:
#     """Cauchy continuum model
#     """

#     dim = 3
#     model_name = 'Cauchy continuum model'

#     def __init__(self):
#         ...

#     def __repr__(self):
#         s = [self.model_name,]

#         return '\n'.join(s)




# @dataclass
# class Cauchy:
class CauchyContinuumModel:
    """Cauchy continuum model
    """

    dim = 3
    model_name = 'Cauchy continuum model'
    strain_name = ['e11', 'e22', 'e33', 'e23', 'e13', 'e12']
    stress_name = ['s11', 's22', 's33', 's23', 's13', 's12']

    constant_name = [
        'e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu12', 'nu13', 'nu23']
    constant_label = [
        'E1', 'E2', 'E3', 'G12', 'G13', 'G23', 'nu12', 'nu13', 'nu23']

    def __init__(self):

        self.name = ''
        self.id = None

        # Inertial
        # --------

        self.density : float = None
        self.temperature : float = 0

        self.isotropy : int = None
        """Isotropy type.

        * 0: Isotropic
        * 1: Orthotropic
        * 2: Anisotropic
        """

        # Consitutive

        #: Stiffness matrix
        self.cmpl: Iterable[Iterable[float]] = None
        #: Compliance matrix
        self.stff: Iterable[Iterable[float]] = None

        # Mechanical
        # ----------

        self.e1 : float = None
        self.e2 : float = None
        self.e3 : float = None
        self.g12 : float = None
        self.g13 : float = None
        self.g23 : float = None
        self.nu12 : float = None
        self.nu13 : float = None
        self.nu23 : float = None

        self.strength_constants : Iterable = None
        self.failure_criterion = None

        # Thermal
        # -------

        self.cte : Iterable[float] = None
        self.specific_heat : float = 0

        self.d_thetatheta : float = 0
        self.f_eff : float = 0


    def __repr__(self) -> str:
        s = [
            self.model_name,
            '-'*len(self.model_name),
            f'density = {self.density}',
            f'isotropy = {self.isotropy}'
        ]

        s.append('----------------')
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

        s.append('---------------------')
        s.append('engineering constants')
        for _label, _name in zip(self.constant_label, self.constant_name):
            _value = eval(f'self.{_name}')
            s.append(f'{_label} = {_value}')

        return '\n'.join(s)


    def __call__(self, x):
        return


    def set(self, name:str, value, **kwargs):
        if name == 'isotropy':
            if isinstance(value, str):
                if value.startswith('iso'):
                    self.isotropy = 0
                elif value.startswith('ortho') or value.startswith('eng') or value.startswith('lam'):
                    self.isotropy = 1
                elif value.startswith('aniso'):
                    self.isotropy = 2
                else:
                    self.isotropy = int(value)
            elif isinstance(value, int):
                self.isotropy = value

        elif name == 'elastic':
            self.setElastic(value, kwargs['input_type'])

        else:
            exec(f'self.{name} = {value}')

        return


    def setElastic(self, consts:Iterable, input_type):
        if self.isotropy == 0:
            self.e1 = float(consts[0])
            self.nu12 = float(consts[1])

        elif self.isotropy == 1:
            if input_type == 'lamina':
                self.e1 = float(consts[0])
                self.e2 = float(consts[1])
                self.g12 = float(consts[2])
                self.nu12 = float(consts[3])
                self.e3 = self.e2
                self.g13 = self.g12
                self.nu13 = self.nu12
                self.nu23 = 0.3
                self.g23 = self.e3 / (2.0 * (1 + self.nu23))
            elif input_type == 'engineering':
                self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
                self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
                self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))
            elif input_type == 'orthotropic':  # TODO
                pass

        elif self.isotropy == 2:  # TODO
            pass  

        return


    def get(self, name:str):
        r"""
        """

        v = None

        if name == 'density':
            v = self.density
        elif name == 'temperature':
            v = self.temperature
        elif name == 'isotropy':
            v = self.isotropy

        elif name == 'e':
            v = self.e1
        elif name == 'nu':
            v = self.nu12
        elif name in ['e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu12', 'nu13', 'nu23']:
            v = eval(f'self.{name}')

        elif name == 'c':
            v = self.stff
        elif name == 's':
            v = self.cmpl

        elif name == 'strength':
            v = self.strength_constants
        elif name == 'failure_criterion':
            v = self.failure_criterion

        elif name == 'cte':
            v = self.cte
        elif name == 'specific_heat':
            v = self.specific_heat

        elif name.startswith('c'):
            _i = int(name[1]) - 1
            _j = int(name[2]) - 1
            v = self.stff[_i][_j]
        elif name.startswith('s'):
            _i = int(name[1]) - 1
            _j = int(name[2]) - 1
            v = self.cmpl[_i][_j]

        return v









# Legacy

from .general import MaterialSection

class MaterialProperty(MaterialSection):
    """
    """

    def __init__(self, name=''):
        MaterialSection.__init__(self, 3)
        self.name = name

        self.temperature = 0

        #: int: (continuum model) Isotropy type.
        #: Isotropic (0), orthotropic (1), anisotropic (2).
        self.isotropy = None

        self.e1 = None
        self.e2 = None
        self.e3 = None
        self.g12 = None
        self.g13 = None
        self.g23 = None
        self.nu12 = None
        self.nu13 = None
        self.nu23 = None

        self.strength = {}

        self.cte = []
        self.specific_heat = 0

        self.d_thetatheta = 0
        self.f_eff = 0


    def __repr__(self):
        s = [
            f'density = {self.density}',
        ]

        if self.isotropy == 0:
            s.append('isotropic')
            s.append(f'E = {self.e1}, v = {self.nu12}')
        elif self.isotropy == 1:
            s.append('orthotropic')
            s.append(f'E1 = {self.e1}, E2 = {self.e2}, E3 = {self.e3}')
            s.append(f'G12 = {self.g12}, G13 = {self.g13}, G23 = {self.g23}')
            s.append(f'v12 = {self.nu12}, v13 = {self.nu13}, v23 = {self.nu23}')
        elif self.isotropy == 2:
            s.append('anisotropic')
            for i in range(6):
                _row = []
                for j in range(i, 6):
                    _row.append(f'C{i+1}{j+1} = {self.stff[i][j]}')
                s.append(', '.join(_row))

        return '\n'.join(s)


    def summary(self):
        stype = 'isotropic'
        sprop = [['e = {0}'.format(self.e1),], ['nu = {0}'.format(self.nu12),]]
        if self.isotropy == 1:
            stype = 'orthotropic'
            sprop = [
                ['e1 = {0}'.format(self.e1), 'e2 = {0}'.format(self.e2), 'e3 = {0}'.format(self.e3)],
                ['g12 = {0}'.format(self.g12), 'g13 = {0}'.format(self.g13), 'g23 = {0}'.format(self.g23)],
                ['nu12 = {0}'.format(self.nu12), 'nu13 = {0}'.format(self.nu13), 'nu23 = {0}'.format(self.nu23)]
            ]
        elif self.isotropy == 2:
            stype = 'anisotropic'
        print('type:', stype)
        print('density =', self.density)
        print('elastic properties:')
        for p in sprop:
            print(', '.join(p))
        return


    def get(self, name):
        r"""
        """
        v = None

        if name == 'density':
            v = self.density

        elif name in ['e', 'e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu', 'nu12', 'nu13', 'nu23']:
            v = self.constants[name]

        elif name in ['xt', 'yt', 'zt', 'xc', 'yc', 'zc', 'r', 't', 's']:
            v = self.strength_constants[name]
        # v = eval('self.{}'.format(name))

        return v


    def assignConstants(self, consts):
        if len(consts) == 2:
            self.isotropy = 0
            self.e1 = float(consts[0])
            self.nu12 = float(consts[1])
        elif len(consts) == 9:
            self.isotropy = 1
            self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
            self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
            self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))


    def setElasticProperty(self, consts, ctype):
        if ctype == 'isotropic' or ctype == 0:
            self.isotropy = 0
            self.e1 = float(consts[0])
            self.nu12 = float(consts[1])
        elif ctype == 'lamina':
            self.isotropy = 1
            self.e1 = float(consts[0])
            self.e2 = float(consts[1])
            self.g12 = float(consts[2])
            self.nu12 = float(consts[3])
            self.e3 = self.e2
            self.g13 = self.g12
            self.nu13 = self.nu12
            self.nu23 = 0.3
            self.g23 = self.e3 / (2.0 * (1 + self.nu23))
        elif ctype == 'engineering' or ctype == 1:
            self.isotropy = 1
            self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
            self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
            self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))
        elif ctype == 'orthotropic':
            self.isotropy = 1
        elif ctype == 'anisotropic' or ctype == 2:
            self.isotropy = 2

        return


    def setStrengthProperty(self, strength):
        self.strength['constants'] = list(map(float, strength))
        return


    def setFailureCriterion(self, criterion):
        if isinstance(criterion, str):
            self.strength['criterion'] = self.FAILURE_CRITERION_NAME_TO_ID[criterion]
        return


    def setCharacteristicLength(self, char_len=0):
        self.strength['chara_len'] = char_len
        return


