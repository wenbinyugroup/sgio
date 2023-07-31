from typing import Protocol, Iterable
from numbers import Number
import sgio.utils.io as sui
# import sgio.model as sm

class Model(Protocol):
    def __repr__(self) -> str:
        ...

    def __call__(self, x):
        ...

    def set(self, name:str, value:Number) -> None:
        ...

    def get(self, name:str):
        """Get model parameter (property) given a name."""



class MaterialSection(object):
    """A macroscopic structure model. Stores material or structural
    properties.

    Parameters
    ----------
    smdim : int, default 3
        Dimension of material/structure model.
        Beam (1), plate/shell (2), or 3D continuum (3).
        Defualt to 3.
    """

    def __init__(self, name:str='', smdim:int=3):
        #: int: Dimension of material/structure model.
        self.smdim = smdim
        #: str: Name of the material/structure.
        self.name = name

        # Mass property
        # -------------
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
        #: list of floats: Mass center. [x1, x2, x3]
        self.mass_center = None

        # Geometry property
        # -----------------
        #: float: Geometric center
        self.gc = None

        # Constitutive property
        self.constitutive = None


        # Elastic property
        # ----------------
        #: int: (continuum model) Isotropy type.
        #: Isotropic (0), orthotropic (1), anisotropic (2).
        # self.type = None
        #: dict of {str, float}: Engineering constants.
        #: Keys: `e1`, `e2`, `e3`, `nu12`, `nu13`, `nu23`, `g12`, `g13`, `g23`
        self.constants = {}
        #: list of lists of floats: Stiffness matrix.
        self.stff = None
        # self.stiffness = None
        #: list of lists floats: Compliance matrix.
        self.cmpl = None
        # self.compliance = None

        #: list of lists of floats:
        #: (beam/plate/shell models) Refined stiffness matrix
        # self.stiffness_refined = None
        #: list of lists of floats:
        #: (beam/plate/shell models) Refined compliance matrix
        # self.compliance_refined = None
        #: list of floats: (beam model) Neutral axes/Tension center. [x1, x2, x3]
        self.tension_center = None
        #: list of floats: (beam model) Elastic axis/Shear center. [x1, x2, x3]
        self.shear_center = None

        # Strength property
        # -----------------
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


    def __repr__(self):
        s = '\n'
        s += f'name: {self.name}\n'
        s += 'effective properties\n'
        s += f'structural model dimension: {self.smdim}\n'
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


    def get(self, name):
        r"""
        """
        v = None

        if self.smdim == 1:
            return self.constitutive.get(name)

        if name == 'density':
            v = self.density

        elif name in ['xt', 'yt', 'zt', 'xc', 'yc', 'zc', 'r', 't', 's']:
            v = self.strength_constants[name]

        elif self.smdim == 3:
            if name in ['e', 'e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu', 'nu12', 'nu13', 'nu23']:
                # v = self.constitutive.get(name)
                v = self.constants.get(name)

        return v
    

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
        return self.constitutive.getAll()
        # names = [
        #     'mu', 'mmoi1', 'mmoi2', 'mmoi3',
        #     'ea', 'ga22', 'ga33', 'gj', 'ei22', 'ei33',
        #     'mc2', 'mc3', 'tc2', 'tc3', 'sc2', 'sc3'
        # ]
        # for i in range(4):
        #     for j in range(4):
        #         names.append('stf{}{}c'.format(i+1, j+1))
        #         names.append('cmp{}{}c'.format(i+1, j+1))
        # for i in range(6):
        #     for j in range(6):
        #         names.append('ms{}{}'.format(i+1, j+1))
        #         names.append('stf{}{}r'.format(i+1, j+1))
        #         names.append('cmp{}{}r'.format(i+1, j+1))

        # dict_prop = {}
        # for n in names:
        #     dict_prop[n] = self.get(n)

        # return dict_prop









class SectionResponse():
    """Generalized stress/strain for an SG model.
    """
    def __init__(self):
        self.displacement:list = [0, 0, 0]
        """
        list of floats: Global displacement vector ``[u1, u2, u3]``.
        """

        self.directional_cosine:list = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
        """
        list of lists floats: Global rotation matrix.
        
        ..  code-block::

            [
                [C11, C12, C13],
                [C21, C22, C23],
                [C31, C32, C33]
            ]
        """

        self.load_type:int = 0
        """
        int: Type of the sectional response load

        * 0 - generalized stresses
        * 1 - generalized strains
        """

        self.load_tags = []

        self.load:list = []
        """list of list of floats: Global loads

        ============================ ============================================ ==============================================
        Model                        Generalized stresses                         Generalized strains
        ============================ ============================================ ==============================================
        Continuum                    ``[s11, s22, s33, s23, s13, s12]``           ``[e11, e22, e33, e23, e13, e12]``
        Kirchhoff-Love plate/shell   ``[N11, N22, N12, M11, M22, M12]``           ``[e11, e22, 2e12, k11, k22, 2k12]``
        Reissner-Mindlin plate/shell ``[N11, N22, N12, M11, M22, M12, N13, N23]`` ``[e11, e22, 2e12, k11, k22, 2k12, g13, g23]``
        Euler-Bernoulli beam         ``[F1, M1, M2, M3]``                         ``[e11, k11, k12, k13]``
        Timoshenko beam              ``[F1, F2, F3, M1, M2, M3]``                 ``[e11, g12, g13, k11, k12, k13]``
        ============================ ============================================ ==============================================
        """

        self.distr_load = [0, 0, 0, 0, 0, 0]
        self.distr_load_d1 = [0, 0, 0, 0, 0, 0]
        self.distr_load_d2 = [0, 0, 0, 0, 0, 0]
        self.distr_load_d3 = [0, 0, 0, 0, 0, 0]


    def strU(self, float_format='16.6e', delimiter=','):
        fstr = '{:'+float_format+'}'
        return delimiter.join([fstr.format(u) for u in self.displacement])


    def strC(self, float_format='16.6e', col_delimiter=',', row_delimiter=','):
        fstr = '{:'+float_format+'}'
        return row_delimiter.join(
            [(col_delimiter.join(
                [fstr.format(c) for c in row]
            )) for row in self.directional_cosine]
        )


    def strS(self, float_format='16.6e', delimiter=','):
        fstr = '{:'+float_format+'}'
        return delimiter.join([fstr.format(s) for s in self.load])


    def __repr__(self):
        lines = ['Displacement',]
        lines.append('\n'.join(['  u{} = {:16.6e}'.format(i+1, u) for i, u in enumerate(self.displacement)]))
        lines.append('Rotation (directional cosine)')
        lines.append('\n'.join(
            [('  ' + ', '.join(
                ['c{}{} = {:16.6e}'.format(i+1, j+1, c) for j, c in enumerate(row)]
            )) for i, row in enumerate(self.directional_cosine)]
        ))
        lines.append('Load')
        lines.append('\n'.join(['  {} = {:16.6e}'.format(t, s) for t, s in zip(self.load_tags, self.load)]))
        return '\n'.join(lines)


    def writeSGInputGlbU(self, file, float_format='16.6e'):
        sui.writeFormatFloats(file, self.displacement, float_format)
        file.write('\n')


    def writeSGInputGlbC(self, file, float_format='16.6e'):
        sui.writeFormatFloatsMatrix(file, self.directional_cosine, float_format)
        file.write('\n')


    def writeSGInputGlbS(self, file, file_format, int_format='8d', float_format='16.6e'):
        if file_format.lower().startswith('v'):
            if len(self.load) == 4:
                sui.writeFormatFloats(file, self.load)
            elif len(self.load) == 6:
                sui.writeFormatFloats(file, [self.load[i] for i in [0, 3, 4, 5]], float_format)
                sui.writeFormatFloats(file, [self.load[i] for i in [1, 2]], float_format)
                file.write('\n')
                sui.writeFormatFloats(file, self.distr_load, float_format)
                sui.writeFormatFloats(file, self.distr_load_d1, float_format)
                sui.writeFormatFloats(file, self.distr_load_d2, float_format)
                sui.writeFormatFloats(file, self.distr_load_d3, float_format)
        elif file_format.lower().startswith('s'):
            sui.writeFormatIntegers(file, [self.load_type,], int_format)
            # for load_case in self.global_loads:
            sui.writeFormatFloats(file, self.load, float_format)
        file.write('\n')




class StructureResponseCases():
    """Cases of generalized stress/strain.
    """
    def __init__(self):
        self.loc_tags = []
        """Response location tags
        """

        self.cond_tags = []
        """Response condition tags
        """

        self.responses = []
        """Responses

        ..  code-block::

            [
                {
                    'loc_tag1': loc_value1,
                    'loc_tag2': loc_value2,
                    ...,
                    'condition_tag1': condition_value1,
                    'condition_tag2': condition_value2,
                    ...,
                    'response': SectionResponse
                },
                {...},
                ...
            ]
        """

    def __repr__(self):
        lines = []
        for _resp in self.responses:
            lines.append('-'*20)
            lines.append('Location:')
            lines.append('\n'.join(['  {} = {}'.format(t, _resp[t]) for t in self.loc_tags]))
            lines.append('Condition:')
            lines.append('\n'.join(['  {} = {}'.format(t, _resp[t]) for t in self.cond_tags]))
            lines.append(str(_resp['response']))
        lines.append('-'*20)
        return '\n'.join(lines)


    def getResponsesByLocCond(self, **kwargs):
        """Get response by providing location and condition.

        """
        resps = []

        for _resp in self.responses:
            # resp = _resp
            found = True
            for _k, _v in kwargs.items():
                if _v != _resp[_k]:
                    found = False
                    break
            if found:
                resps.append(_resp)

        return resps


    def addResponseCase(self, loc, cond, sect_resp:SectionResponse):
        resp_case = {}

        # sect_resp = SectionResponse()

        # sect_resp.load_type = load_type
        # sect_resp.load_tags = load_tags

        # Read location ids
        for _tag, _value in zip(self.loc_tags, loc):
            # _i = tags_idx[_tag]
            resp_case[_tag] = _value

        # Read case ids
        for _tag, _value in zip(self.cond_tags, cond):
            # _i = tags_idx[_tag]
            resp_case[_tag] = _value

        # # Read loads
        # _load = []
        # for _tag in load_tags:
        #     _i = tags_idx[_tag]
        #     _load.append(float(row[_i]))
        # sect_resp.load = _load

        # # Read displacements
        # _disp = []
        # for _tag in disp_tags:
        #     _i = tags_idx[_tag]
        #     _disp.append(float(row[_i]))
        # sect_resp.displacement = _disp

        # # Read rotations
        # _rot = []
        # for _tag in rot_tags:
        #     _i = tags_idx[_tag]
        #     _rot.append(float(row[_i]))
        # sect_resp.directional_cosine = [
        #     _rot[:3], _rot[3:6], _rot[6:]
        # ]

        resp_case['response'] = sect_resp

        self.responses.append(resp_case)

