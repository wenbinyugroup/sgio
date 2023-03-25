from msgd.model.general import MaterialSection
import msgd.utils.io as utio




class ShellProperty(MaterialSection):
    """A plate/shell property class (smdim = 2)
    """
    def __init__(self):
        MaterialSection.__init__(self, smdim=1)

        self.mass = []

        self.xm3 = None

        self.i11 = None
        self.i22 = None

        self.stff = []
        self.cmpl = []

        self.geo_correction_stff = []
        self.stff_geo = []

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

    def printData(self):
        fmt = '20.10E'
        print('Summary')
        print()
        print('Effective Mass Matrix')
        print(utio.matrixToString(self.mass, fmt=fmt))
        print()
        print('The Mass Center')
        # print(f'({self.xm3:{fmt}})')
        print('({:{fmt}})'.format(self.xm3, fmt=fmt))
        print()
        # print(f'Mass moments of inertia i11 = i22 = {self.i11:{fmt}}')
        print('Mass moments of inertia i11 = i22 = {:{fmt}}'.format(self.i11, fmt=fmt))

        print()
        print('The Effective Stiffness Matrix')
        print(utio.matrixToString(self.stff, fmt=fmt))
        print('The Effective Compliance Matrix')
        print(utio.matrixToString(self.cmpl, fmt=fmt))
        print()
        print('In-Plane Properties')
        # print(f'E1 = {self.e1_i:{fmt}}')
        print('E1 = {:{fmt}}'.format(self.e1_i, fmt=fmt))
        # print(f'E2 = {self.e2_i:{fmt}}')
        print('E2 = {:{fmt}}'.format(self.e2_i, fmt=fmt))
        # print(f'G12 = {self.g12_i:{fmt}}')
        print('G12 = {:{fmt}}'.format(self.g12_i, fmt=fmt))
        # print(f'nu12 = {self.nu12_i:{fmt}}')
        print('nu12 = {:{fmt}}'.format(self.nu12_i, fmt=fmt))
        # print(f'eta121 = {self.eta121_i:{fmt}}')
        print('eta121 = {:{fmt}}'.format(self.eta121_i, fmt=fmt))
        # print(f'eta122 = {self.eta122_i:{fmt}}')
        print('eta122 = {:{fmt}}'.format(self.eta122_i, fmt=fmt))
        print()
        print('Flexural Properties')
        # print(f'E1 = {self.e1_o:{fmt}}')
        print('E1 = {:{fmt}}'.format(self.e1_o, fmt=fmt))
        # print(f'E2 = {self.e2_o:{fmt}}')
        print('E2 = {:{fmt}}'.format(self.e2_o, fmt=fmt))
        # print(f'G12 = {self.g12_o:{fmt}}')
        print('G12 = {:{fmt}}'.format(self.g12_o, fmt=fmt))
        # print(f'nu12 = {self.nu12_o:{fmt}}')
        print('nu12 = {:{fmt}}'.format(self.nu12_o, fmt=fmt))
        # print(f'eta121 = {self.eta121_o:{fmt}}')
        print('eta121 = {:{fmt}}'.format(self.eta121_o, fmt=fmt))
        # print(f'eta122 = {self.eta122_o:{fmt}}')
        print('eta122 = {:{fmt}}'.format(self.eta122_o, fmt=fmt))
        print()
        print('The Geometric Correction to the Stiffness Matrix')
        print(utio.matrixToString(self.geo_correction_stff, fmt=fmt))
        print('The Total Stiffness Matrix after Geometric Correction')
        print(utio.matrixToString(self.stff_geo, fmt=fmt))


    def get(self, name):
        r"""
        """

        # Stiffness
        if name.startswith('stf'):
            if name[-1] == 'c':
                return self.stff[int(name[3])-1][int(name[4])-1]
            elif name[-1] == 'r':
                if name[-2] == 'g':
                    if len(self.stff_geo) > 0:
                        return self.stff_geo[int(name[3])-1][int(name[4])-1]
                    else:
                        return self.stff[int(name[3])-1][int(name[4])-1]

        elif name.startswith('mass'):
            return self.mass[int(name[4])-1][int(name[5])-1]

        return

