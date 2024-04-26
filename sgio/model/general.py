from __future__ import annotations

import copy
from typing import Protocol, Iterable
from numbers import Number
import sgio.utils.io as sui
# import sgio.model as sm

class Model(Protocol):
    """
    """
    def __repr__(self) -> str:
        ...

    def __call__(self, x):
        ...

    def set(self, name:str, value:Number) -> None:
        ...

    def get(self, name:str):
        """Get model parameter (property) given a name."""




def getModelDim(model:str) -> int:
    """
    """

    mdim = 0
    if model[:2].lower() == 'sd':
        mdim = 3
    elif model[:2].lower() == 'pl':
        mdim = 2
    elif model[:2].lower() == 'bm':
        mdim = 1

    return mdim




# class State():
#     """Generalized strain and stress.
#     """
#     def __init__(self, strain=[], stress=[]):
#         self._e = strain
#         self._s = stress

#     @property
#     def strain(self): return self._e
#     @strain.setter
#     def strain(self, value): self._e = value
#     @property
#     def stress(self): return self._s
#     @stress.setter
#     def stress(self, value): self._s = value

#     # def getStrain(self):
#     #     return self._e

#     # def getStress(self):
#     #     return self._s




class State():
    """
    """
    def __init__(
        self, name:str='', data:list|dict={}, label:list[str]=[],
        location:str=''):
        self.name:str = name
        self.label:list[str] = label
        self.location:str = location  # Choose from 'node', 'element'
        # print(f'data = {data}')
        self.data:list|dict = data
        # print(f'self.data = {self.data}')
        """
        point data: []
        field data: {
            1: [],
            2: [],
            ...
        }
        """

    # @property
    # def name(self): return self._name
    # @property
    # def data(self): return self._data
    # @property
    # def label(self): return self._label
    # @property
    # def location(self): return self._location

    def __repr__(self):
        _str = [
            f'state: {self.name} ({self.label})',
        ]

        if isinstance(self.data, list):
            _str.append(f'  point data: {self.data}')

        elif isinstance(self.data, dict):
            _str.append(f'  field data: {len(self.data)} {self.location} data')
            for _k, _v in self.data.items():
                _str.append(f'    {_k}: {_v}')

        return '\n'.join(_str)

    def toDictionary(self):
        return {
            'name': self.name,
            'data': self.data,
            'label': self.label,
            'location': self.location
        }

    def addData(self, data:list, loc=None):
        if loc is None:
            self.data = data
        elif isinstance(self.data, dict):
            self.data[loc] = data

    """
    A function returning the state data at a list of given locations.

    Parameters
    ----------
    locs : list
        List of locations.

    Returns
    -------
    State
        A copy of the State object with the data at the given locations.
    """
    def at(self, locs:Iterable):
        _data = []

        if isinstance(self.data, list):
            _data = self.data
        elif isinstance(self.data, dict):
            if len(locs) == 1:
                try:
                    _data = self.data[locs[0]]
                except KeyError:
                    pass
            else:
                _data = {}
                for _i in locs:
                    try:
                        _data[_i] = self.data[_i]
                    except KeyError:
                        pass
                # data = dict([(i, self.data[i]) for i in locs])

        if len(_data) == 0:
            return None

        return State(
            self.name,
            copy.deepcopy(_data),
            self.label,
            self.location
            )




class StateCase():
    """
    """
    def __init__(self, case:dict={}, states:dict={}):
        self._case:dict = case
        """
        {
            'tag1': value1,
            'tag2': value2,
            ...
        }
        """

        self._states:dict = states
        """
        {
            'name': State,
            ...
        }
        """

    @property
    def case(self): return self._case
    @property
    def states(self): return self._states

    def getState(self, name):
        return self._states[name]

    @property
    def displacement(self):
        try:
            return self._states['displacement']
        except KeyError:
            return None

    @property
    def rotation(self):
        try:
            return self._states['rotation']
        except KeyError:
            return None

    @property
    def load(self):
        try:
            return self._states['load']
        except KeyError:
            return None

    @property
    def distributed_load(self):
        try:
            return self._states['distributed_load']
        except KeyError:
            return None

    def __repr__(self):
        lines = [
            'state case',
            'case:',
        ]
        for _k, _v in self._case.items():
            lines.append(f'  {_k}: {_v}')
        lines.append('states:')
        for _k, _v in self._states.items():
            lines.append(f'  {str(_v)}')

        return '\n'.join(lines)

    def toDictionary(self):
        return {
            'case': self._case,
            'states': dict([(k, v.toDictionary()) for k, v in self._states.items()])
        }

    def addState(
        self, name:str, state:State=None,
        data=None, entity_id=None, loc_type=''
        ):
        if not name in self._states.keys():
            self._states[name] = State(
                name=name,
                data={},
                location=loc_type
                )

        if not state is None:
            self._states[name] = state

        elif not entity_id is None:
            self._states[name].addData(
                data=data, loc=entity_id
            )
            # self._states[name].data[entity_id] = value

        else:
            if isinstance(data, list):
                self._states[name].data = data
            elif isinstance(data, dict):
                self._states[name].data.update(data)

        # print(f'added state {self._states[name]}')

    def at(self, locs:Iterable, state_name=None):
        """
        A function returning all states with data
        at a list of given locations.

        Parameters
        ----------
        locs : list
            List of locations.

        Returns
        -------
        StateCase
            A copy of the StateCase object with the states at the given locations.
        """
        states = {}

        _state_names = []
        if state_name is None:
            _state_names = self._states.keys()
        elif isinstance(state_name, str):
            _state_names = [state_name,]
        elif isinstance(state_name, list):
            _state_names = state_name

        for _name in _state_names:
            _state = self.states[_name].at(locs)
            if not _state is None:
                states[_name] = self.states[_name].at(locs)

        if len(states) == 0:
            return None

        return StateCase(
            case=self._case,
            states=states
            )


# class StateFields():
#     """Generalized strain and stress fields.
#     """
#     def __init__(self, node_displ={},
#         intp_strain={}, intp_stress={}, intp_strain_m={}, intp_stress_m={},
#         node_strain={}, node_stress={}, node_strain_m={}, node_stress_m={},
#         elem_strain={}, elem_stress={}, elem_strain_m={}, elem_stress_m={},
#         ):
#         # Displacement
#         self._node_displ = node_displ

#         # State at integration points [coordinates, state]
#         self._intp_strain = intp_strain
#         self._intp_stress = intp_stress
#         self._intp_strain_m = intp_strain_m
#         self._intp_stress_m = intp_stress_m

#         # State at nodes [nid, state]
#         self._node_strain = node_strain
#         self._node_stress = node_stress
#         self._node_strain_m = node_strain_m
#         self._node_stress_m = node_stress_m

#         # Averaged state at elements [eid, state]
#         self._elem_strain = elem_strain
#         self._elem_stress = elem_stress
#         self._elem_strain_m = elem_strain_m
#         self._elem_stress_m = elem_stress_m

#     def getDisplacementField(self):
#         return self._node_displ

#     def getStrainField(self, where:str='element', cs:str='structure'):
#         """

#         Parameters
#         ----------
#         where
#             Location of the field.
#             - 'i': integration points
#             - 'n': nodes
#             - 'e': elements
#         cs
#             Reference coordinate system.
#             - 's': structural model frame
#             - 'm': material frame
#         """
#         if where.startswith('i'):
#             if cs.startswith('s'):
#                 return self._intp_strain
#             elif cs.startswith('m'):
#                 return self._intp_strain_m
#         elif where.startswith('n'):
#             if cs.startswith('s'):
#                 return self._node_strain
#             elif cs.startswith('m'):
#                 return self._node_strain_m
#         elif where.startswith('e'):
#             if cs.startswith('s'):
#                 return self._elem_strain
#             elif cs.startswith('m'):
#                 return self._elem_strain_m

#     def getStressField(self, where:str='element', cs:str='structure'):
#         """

#         Parameters
#         ----------
#         where
#             Location of the field.
#             - 'i': integration points
#             - 'n': nodes
#             - 'e': elements
#         cs
#             Reference coordinate system.
#             - 's': structural model frame
#             - 'm': material frame
#         """
#         if where.startswith('i'):
#             if cs.startswith('s'):
#                 return self._intp_stress
#             elif cs.startswith('m'):
#                 return self._intp_stress_m
#         elif where.startswith('n'):
#             if cs.startswith('s'):
#                 return self._node_stress
#             elif cs.startswith('m'):
#                 return self._node_stress_m
#         elif where.startswith('e'):
#             if cs.startswith('s'):
#                 return self._elem_stress
#             elif cs.startswith('m'):
#                 return self._elem_stress_m




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

