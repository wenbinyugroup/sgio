class MSGDFEModel():
    r"""
    """

    def __init__(self, name=''):
        self.name = name

        self.nodes = {}
        self.elements = {}
        self.node_sets = {}
        self.element_sets = {}

    def summary(self):
        print('Nodes')
        print(self.nodes)
        print()
        print('Node sets')
        print(self.node_sets)
        print()
        print('Elements')
        print(self.elements)
        print()
        print('Element sets')
        print(self.element_sets)









class MaterialSection(object):
    r""" A macroscopic structure model. Stores material or structural
    properties.

    Parameters
    ----------
    smdim : int, default 3
        Dimension of material/structure model.
        Beam (1), plate/shell (2), or 3D continuum (3).
        Defualt to 3.
    """

    def __init__(self, smdim=3):
        #: int: Dimension of material/structure model.
        self.smdim = smdim
        #: str: Name of the material/structure.
        self.name = ''

        #: list of lists of floats: Mass matrix at the origin.
        self.mass_origin = None
        #: list of lists of floats: Mass matrix at the mass center.
        self.mass_mc = None
        #: float: Density of the material/structure.
        self.density = None
        #: list of floats: Mass moments of inertia.
        self.mmoi = [0, 0, 0]
        #: float: Mass-weighted radius of gyration.
        self.mwrg = None
        #: float: Geometric center
        self.gc = None
        #: int: (continuum model) Isotropy type.
        #: Isotropic (0), orthotropic (1), anisotropic (2).
        self.type = None
        #: dict of {str, float}: Engineering constants.
        #: Keys: `e1`, `e2`, `e3`, `nu12`, `nu13`, `nu23`, `g12`, `g13`, `g23`
        self.constants = {}
        #: list of lists of floats: Stiffness matrix.
        self.stiffness = None
        self.stff = None
        #: list of lists floats: Compliance matrix.
        self.compliance = None
        self.cmpl = None

        #: list of lists of floats:
        #: (beam/plate/shell models) Refined stiffness matrix
        self.stiffness_refined = None
        #: list of lists of floats:
        #: (beam/plate/shell models) Refined compliance matrix
        self.compliance_refined = None

        #: list of floats: Mass center. [x1, x2, x3]
        self.mass_center = None
        #: list of floats: (beam model) Neutral axes/Tension center. [x1, x2, x3]
        self.tension_center = None
        #: list of floats: (beam model) Elastic axis/Shear center. [x1, x2, x3]
        self.shear_center = None

        #: int: Failure criterion.
        self.failure_criterion = None
        #: dict: Strength properties.
        # {
        #   'xt|x1t':,
        #   'yt|x2t':,
        #   'zt|x3t':,
        #   'xc|x1c':,
        #   'yc|x2c':,
        #   'zc|x3c':,
        #   'r|x23':,
        #   't|x13':,
        #   's|x12':
        # }
        self.strength_constants = {}

        self.char_len = 0

        # self.strength = {
        #     'criterion': 0,
        #     'chara_len': 0,
        #     'constants': []
        # }

    def __str__(self):
        s = '\n'
        s = s + 'Effective properties of the SG\n'
        s = s + 'Structure model dimension: {0}\n'.format(self.smdim)
        if self.smdim == 3:
            pass
        elif self.smdim == 2:
            pass
        elif self.smdim == 1:
            pass

        return s


    def summary(self):
        print('')
        print('Effective properties of the SG')
        print('Structure model dimension: {0}'.format(self.smdim))

        ep = self.eff_props[self.smdim]
        if self.smdim == 3:
            pass
        elif self.smdim == 2:
            pass
        elif self.smdim == 1:
            stf = ep['stiffness']
            print('The Effective Stiffness Matrix')
            for row in stf['classical']:
                print(row)
            if len(stf['refined']) > 0:
                print('Generalized Timoshenko Stiffness')
                for row in stf['refined']:
                    print(row)









class Load():
    r"""
    """

    def __init__(self):
        return


