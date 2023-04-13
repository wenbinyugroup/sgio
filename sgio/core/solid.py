from sgio.core.general import MaterialSection


class MaterialProperty(MaterialSection):
    """
    """

    FAILURE_CRITERION_NAME_TO_ID = {
        'max_principal_stress': 1,
        'max_principal_strain': 2,
        'max_shear_stress': 3,
        'tresca': 3,
        'max_shear_strain': 4,
        'mises': 5,
        'max_stress': 1,
        'max_strain': 2,
        'tsai-hill': 3,
        'tsai-wu': 4,
        'hashin': 5
    }

    def __init__(self, name=''):
        MaterialSection.__init__(self, 3)
        self.name = name

        self.temperature = 0

        #: int: (continuum model) Isotropy type.
        #: Isotropic (0), orthotropic (1), anisotropic (2).
        self.anisotropy = None

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


    def summary(self):
        stype = 'isotropic'
        sprop = [['e = {0}'.format(self.e1),], ['nu = {0}'.format(self.nu12),]]
        if self.anisotropy == 1:
            stype = 'orthotropic'
            sprop = [
                ['e1 = {0}'.format(self.e1), 'e2 = {0}'.format(self.e2), 'e3 = {0}'.format(self.e3)],
                ['g12 = {0}'.format(self.g12), 'g13 = {0}'.format(self.g13), 'g23 = {0}'.format(self.g23)],
                ['nu12 = {0}'.format(self.nu12), 'nu13 = {0}'.format(self.nu13), 'nu23 = {0}'.format(self.nu23)]
            ]
        elif self.anisotropy == 2:
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
            self.anisotropy = 0
            self.e1 = float(consts[0])
            self.nu12 = float(consts[1])
        elif len(consts) == 9:
            self.anisotropy = 1
            self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
            self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
            self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))


    def setElasticProperty(self, consts, ctype):
        if ctype == 'isotropic':
            self.anisotropy = 0
            self.e1 = float(consts[0])
            self.nu12 = float(consts[1])
        elif ctype == 'lamina':
            self.anisotropy = 1
            self.e1 = float(consts[0])
            self.e2 = float(consts[1])
            self.g12 = float(consts[2])
            self.nu12 = float(consts[3])
            self.e3 = self.e2
            self.g13 = self.g12
            self.nu13 = self.nu12
            self.nu23 = 0.3
            self.g23 = self.e3 / (2.0 * (1 + self.nu23))
        elif ctype == 'engineering':
            self.anisotropy = 1
            self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
            self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
            self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))
        elif ctype == 'orthotropic':
            self.anisotropy = 1
        elif ctype == 'anisotropic':
            self.anisotropy = 1

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

