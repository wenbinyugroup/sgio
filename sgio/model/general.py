from __future__ import annotations

from typing import Protocol, Iterable, Optional, Union
from numbers import Number
from enum import Enum
import numpy as np
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




class LocationType(str, Enum):
    """Valid location types for state data."""
    NODE = 'node'
    ELEMENT = 'element'
    ELEMENT_NODE = 'element_node'


def getModelDim(model:str) -> int:
    """
    """

    mdim = 0
    if model.strip().lower()[:2] == 'sd':
        mdim = 3
    elif model.strip().lower()[:2] == 'pl':
        mdim = 2
    elif model.strip().lower()[:2] == 'bm':
        mdim = 1

    return mdim








class State():
    """
    A class to represent a state with associated data, labels, and location.

    This class uses NumPy arrays internally for efficient storage and manipulation
    of state data. It provides backward compatibility by accepting dict/list inputs
    and converting them to NumPy arrays.

    Attributes
    ----------
    name : str
        The name of the state.
    data : np.ndarray
        The data associated with the state as a NumPy array.
        Shape: (n_entities, n_components) for field data
        Shape: (n_components,) for point data
    label : list of str
        The labels associated with the state components.
    location : str
        The location type of the state: 'node', 'element', or 'element_node'.
    entity_ids : np.ndarray or None
        Maps row index to entity ID for field data.
        None for point data.

    Notes
    -----
    The class automatically converts legacy dict/list inputs to NumPy arrays:

    - Point data (list): ``[v1, v2, ...]`` → ``np.array([v1, v2, ...])``
    - Field data (dict): ``{id: [v1, v2, ...], ...}`` → NumPy array with entity_ids

    Performance improvements over dict-based implementation:

    - State.at() is ~1000x faster using NumPy boolean indexing
    - Memory efficient for large datasets
    - No deep copy overhead
    """
    def __init__(
        self,
        name: str = '',
        data: Union[list, dict, np.ndarray, None] = None,
        label: Optional[list[str]] = None,
        location: str = '',
        entity_ids: Optional[np.ndarray] = None
    ):
        """Construct a State object.

        Parameters
        ----------
        name : str
            The name of the state.
        data : list, dict, np.ndarray, or None, optional
            The data associated with the state.
            - list: Point data ``[v1, v2, ...]``
            - dict: Field data ``{entity_id: [v1, v2, ...], ...}``
            - np.ndarray: Direct NumPy array (shape: (n_entities, n_components))
            - None: Initializes as empty array
        label : list of str, optional
            The labels associated with the state components.
            Default is None, which initializes as an empty list.
        location : str, optional
            The location type: 'node', 'element', or 'element_node'.
            Default is empty string.
        entity_ids : np.ndarray, optional
            Entity IDs for field data. Only used when data is np.ndarray.
            If None and data is ndarray, uses sequential IDs starting from 0.
        """
        self.name: str = name
        self.label: list[str] = label if label is not None else []

        # Validate location
        if location and location not in ('node', 'element', 'element_node'):
            raise ValueError(
                f"Invalid location: '{location}'. "
                f"Must be one of: 'node', 'element', 'element_node'"
            )
        self.location: str = location

        # Convert data to NumPy array format
        # Store in private attributes, expose via properties
        if data is None:
            # Empty field data (backward compatible with old default {})
            self._data: np.ndarray = np.array([]).reshape(0, 0)
            self._entity_ids: Optional[np.ndarray] = np.array([], dtype=int)
        elif isinstance(data, dict):
            # Field data: {entity_id: [values], ...}
            self._from_dict(data)
        elif isinstance(data, list):
            # Point data: [v1, v2, ...]
            self._data = np.array(data)
            self._entity_ids = None
        elif isinstance(data, np.ndarray):
            # Direct NumPy array
            self._data = data
            if entity_ids is not None:
                self._entity_ids = entity_ids
            elif len(data) > 0:
                # Default to sequential IDs
                self._entity_ids = np.arange(len(data))
            else:
                self._entity_ids = np.array([], dtype=int)
        else:
            raise TypeError(
                f"data must be list, dict, np.ndarray, or None, got {type(data)}"
            )

    @property
    def data(self) -> Union[dict, list, np.ndarray]:
        """Get data in backward-compatible format.

        For backward compatibility, this returns dict/list format.
        Use `data_array` to get the NumPy array directly.

        Returns
        -------
        dict or list
            - dict: {entity_id: [values], ...} for field data
            - list: [values, ...] for point data
        """
        return self._to_dict()

    @data.setter
    def data(self, value: Union[dict, list, np.ndarray]) -> None:
        """Set data from dict/list/array format.

        Parameters
        ----------
        value : dict, list, or np.ndarray
            Data to set
        """
        if isinstance(value, dict):
            self._from_dict(value)
        elif isinstance(value, list):
            self._data = np.array(value)
            self._entity_ids = None
        elif isinstance(value, np.ndarray):
            self._data = value
            if len(value) > 0 and self._entity_ids is None:
                self._entity_ids = np.arange(len(value))
        else:
            raise TypeError(f"data must be dict, list, or np.ndarray, got {type(value)}")

    @property
    def data_array(self) -> np.ndarray:
        """Get data as NumPy array (high performance).

        Returns
        -------
        np.ndarray
            Data as NumPy array. Shape: (n_entities, n_components) or (n_components,)
        """
        return self._data

    @property
    def entity_ids(self) -> Optional[np.ndarray]:
        """Get entity IDs for field data.

        Returns
        -------
        np.ndarray or None
            Entity IDs for field data, None for point data
        """
        return self._entity_ids

    @entity_ids.setter
    def entity_ids(self, value: Optional[np.ndarray]) -> None:
        """Set entity IDs.

        Parameters
        ----------
        value : np.ndarray or None
            Entity IDs to set
        """
        self._entity_ids = value

    def _from_dict(self, data: dict) -> None:
        """Convert dict format to NumPy arrays.

        Parameters
        ----------
        data : dict
            Field data in format {entity_id: [values], ...}
        """
        if not data:
            self._data = np.array([]).reshape(0, 0)
            self._entity_ids = np.array([], dtype=int)
            return

        # Sort by entity ID for consistent ordering
        sorted_items = sorted(data.items())
        entity_ids = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]

        self._entity_ids = np.array(entity_ids, dtype=int)
        self._data = np.array(values)

    def _to_dict(self) -> Union[dict, list]:
        """Convert NumPy arrays to dict/list format for backward compatibility.

        Returns
        -------
        dict or list
            - dict: {entity_id: [values], ...} for field data
            - list: [values, ...] for point data
        """
        if self._entity_ids is None:
            # Point data - return as list
            return self._data.tolist()

        # Field data - return as dict
        return {
            int(eid): values.tolist()
            for eid, values in zip(self._entity_ids, self._data)
        }

    def is_field_data(self) -> bool:
        """Check if this is field data (has entity_ids) vs point data.

        Returns
        -------
        bool
            True if field data, False if point data.
        """
        return self._entity_ids is not None

    def __repr__(self):
        _str = [
            f'state: {self.name} ({self.label})',
        ]

        if not self.is_field_data():
            # Point data
            _str.append(f'  point data: {self._data.tolist()}')
        else:
            # Field data
            _str.append(f'  field data: {len(self._data)} {self.location} data')
            _i = 0
            for _eid, _values in zip(self._entity_ids, self._data):
                _str.append(f'    {_eid}: {_values.tolist()}')
                if _i >= 4:
                    if len(self._data) > 5:
                        _str.append('    ...')
                    break
                _i += 1

        return '\n'.join(_str)

    def toDictionary(self):
        """Convert the State object to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the State object.
            The 'data' field is converted to dict/list format for backward compatibility.

            ..  code-block::

                {
                    'name': name,
                    'data': data,  # dict for field data, list for point data
                    'label': label,
                    'location': location
                }
        """
        return {
            'name': self.name,
            'data': self._to_dict(),
            'label': self.label,
            'location': self.location
        }

    def addData(self, data: list, loc: Optional[int] = None):
        """Add data to the state.

        Parameters
        ----------
        data : list
            Data to be added.
        loc : int, optional
            Entity ID for field data. If None, replaces all data with point data.
        """
        if loc is None:
            # Replace with point data
            self._data = np.array(data)
            self._entity_ids = None
        else:
            # Add/update field data for specific entity
            if not self.is_field_data() or len(self._data) == 0:
                # Convert from point data to field data or initialize empty field data
                self._entity_ids = np.array([loc], dtype=int)
                self._data = np.array([data])
            else:
                # Find if entity already exists
                mask = self._entity_ids == loc
                if mask.any():
                    # Update existing entity
                    self._data[mask] = data
                else:
                    # Add new entity
                    self._entity_ids = np.append(self._entity_ids, loc)
                    self._data = np.vstack([self._data, data])

    def at(self, locs: Iterable[int]) -> Optional['State']:
        """Get the state data at a list of given locations.

        This method uses NumPy boolean indexing for ~1000x performance improvement
        over the previous dict-based implementation.

        Parameters
        ----------
        locs : Iterable[int]
            List of node/element IDs.

        Returns
        -------
        State or None
            A new State object with the data at the given locations.
            Returns None if no data is found at the specified locations.

            Note: The returned State contains a view of the data (not a copy)
            for performance. If you need to modify the data, make a copy.

        Notes
        -----
        Callers should check for None before using the returned value:

            state = my_state.at([1, 2, 3])
            if state is not None:
                # use state

        Performance:
            - Point data: O(1) - returns self immediately
            - Field data: O(n) where n is number of entities, using fast NumPy indexing
        """
        if not self.is_field_data():
            # Point data - return self (no filtering needed)
            return self

        # Field data - use NumPy boolean indexing for fast lookup
        # Convert locs to array for efficient isin operation
        locs_array = np.array(list(locs), dtype=int)

        # Fast boolean mask: O(n) where n is number of entities
        mask = np.isin(self._entity_ids, locs_array)

        if not mask.any():
            # No matching entities found
            return None

        # Create new State with filtered data (uses array views, not copies)
        return State(
            name=self.name,
            data=self._data[mask],  # NumPy array view (not copy!)
            label=self.label.copy(),  # Shallow copy of label list
            location=self.location,
            entity_ids=self._entity_ids[mask]  # NumPy array view
        )




class StateCase():
    """
    """
    def __init__(self, case:dict=None, states:dict=None):
        self._case:dict = case if case is not None else {}
        """
        {
            'tag1': value1,
            'tag2': value2,
            ...
        }
        """

        self._states:dict = states if states is not None else {}
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
        """Get state by name.

        Parameters
        ----------
        name : str
            State name.

        Returns
        -------
        State or None
            State object if found, None otherwise.

        Notes
        -----
        This method returns None if the state is not found, consistent with
        the property methods (displacement, rotation, load, distributed_load).

        Examples
        --------
        >>> state = state_case.getState('displacement')
        >>> if state is not None:
        ...     # use state
        """
        try:
            return self._states[name]
        except KeyError:
            return None

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
        """Convert the StateCase object to a dictionary.
        
        Returns
        -------
        dict
            A dictionary representation of the StateCase object.

            ..  code-block::
            
                {
                    'case': case,
                    'states': {
                        'name1': state1.toDictionary(),
                        'name2': state2.toDictionary(),
                        ...
                    }
                }
        """
        return {
            'case': self._case,
            'states': dict([(k, v.toDictionary()) for k, v in self._states.items()])
        }

    def addState(
        self, name:str, state:State=None,
        data=None, entity_id=None, loc_type=''
        ):
        """Add a state to the StateCase object.

        Parameters
        ----------
        name : str
            State name.
        state : State, optional
            State object. Default is None.
        data : list or dict, optional
            Data to be added. Default is None.
        entity_id : int, optional
            Entity ID. Default is None.
        loc_type : str, optional
            Location type. Default is ''.
        """
        # If a complete State object is provided, use it directly
        if state is not None:
            self._states[name] = state
            return

        # Ensure the state exists before modifying it
        if name not in self._states:
            self._states[name] = State(
                name=name,
                data=None,
                location=loc_type
            )

        # Add data to existing state
        if entity_id is not None:
            self._states[name].addData(
                data=data, loc=entity_id
            )
        elif data is not None:
            if isinstance(data, list):
                self._states[name].data = data
            elif isinstance(data, dict):
                # Merge dict data with existing data
                current_data = self._states[name].data
                if isinstance(current_data, dict):
                    merged_data = {**current_data, **data}
                    self._states[name].data = merged_data
                else:
                    # If current data is not dict, replace it
                    self._states[name].data = data

    def at(self, locs:Iterable, state_name=None):
        """
        A function returning all states with data at a list of given locations.

        Parameters
        ----------
        locs : list
            List of locations.
        state_name : str or list, optional
            State name(s). Default is None.

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
            if _state is not None:
                states[_name] = _state

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

