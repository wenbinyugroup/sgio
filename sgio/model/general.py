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

    def getDisplacement(self):
        return self.displacement

    def getDirectionCosine(self):
        return self.directional_cosine

    def getLoad(self):
        return self.load

    def getDistributedLoad(self):
        return [
            self.distr_load,
            self.distr_load_d1,
            self.distr_load_d2,
            self.distr_load_d3
        ]

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




class StructureResponseCase():
    """
    """
    def __init__(self):
        self._loc_tags = []
        self._loc_values = []
        self._cond_tags = []
        self._cond_values = []
        self._response:SectionResponse = None

    def __repr__(self):
        lines = []
        lines.append('Location:')
        for t, v in zip(self._loc_tags, self._loc_values):
            lines.append(f'  {t} = {v}')
        lines.append('Condition:')
        for t, v in zip(self._cond_tags, self._cond_values):
            lines.append(f'  {t} = {v}')
        lines.append(str(self._response))
        return '\n'.join(lines)

    def getLocation(self, tag):
        """
        """
        value = None
        for _t, _v in zip(self._loc_tags, self._loc_values):
            if tag == _t:
                value = _v
                break
        return value

    def getCondition(self, tag):
        """
        """
        value = None
        for _t, _v in zip(self._cond_tags, self._cond_values):
            if tag == _t:
                value = _v
                break
        return value

    def getLocationOrCondition(self, tag):
        """
        """
        value = self.getLocation(tag)
        if value is None:
            value = self.getCondition(tag)
        return value




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

        self.responses:list[StructureResponseCase] = []
        """Responses
        """

    def __repr__(self):
        lines = []
        for _resp in self.responses:
            lines.append('-'*20)
            lines.append(str(_resp))
            # lines.append('Location:')
            # lines.append('\n'.join(['  {} = {}'.format(t, _resp[t]) for t in self.loc_tags]))
            # lines.append('Condition:')
            # lines.append('\n'.join(['  {} = {}'.format(t, _resp[t]) for t in self.cond_tags]))
            # lines.append(str(_resp['response']))
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
                # if _v != _resp[_k]:
                if _v != _resp.getLocationOrCondition(_k):
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

