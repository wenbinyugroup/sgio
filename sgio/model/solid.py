from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional, List, Literal
from pydantic import BaseModel, Field, field_validator

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
    stff: Iterable[Iterable[float]] = field(default=None)
    cmpl: Iterable[Iterable[float]] = field(default=None)

    constant_name: Iterable[str] = field(default_factory=initConstantName)
    constant_label: Iterable[str] = field(default_factory=initConstantLabel)

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

    strength_measure: int = 0  # 0: stress, 1: strain

    strength_constants: Iterable[float] = field(default=None)

    char_len: float = 0

    cte: Iterable[float] = field(default=None)
    specific_heat: float = 0

    def __repr__(self) -> str:
        s = [
            f'density = {self.density}',
            f'isotropy = {self.isotropy}'
        ]

        s.append('-'*20)
        s.append('stiffness matrix')
        if self.stff is not None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.stff[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('compliance matrix')
        if self.cmpl is not None:
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
            _value = getattr(self, _name)
            s.append(f'{_label} = {_value}')

        s.append('-'*20)
        s.append('strength')
        for _label, _name in zip(self.strength_label, self.strength_name):
            _value = getattr(self, _name)
            s.append(f'{_label} = {_value}')

        s.append('-'*20)
        s.append('cte')
        if self.cte is not None:
            s.append('  '.join(list(map(str, self.cte))))
        else:
            s.append('NONE')

        return '\n'.join(s)




# ============================================================================
# OLD MODEL (Maintained for backward compatibility)
# ============================================================================
# NOTE: This is the old implementation using dataclass + plain class pattern.
# For new code, use CauchyContinuumModelNew (Pydantic-based) instead.
# This old model will be deprecated in a future release.
# ============================================================================

class CauchyContinuumModel:
    """Cauchy continuum model (OLD - use CauchyContinuumModelNew for new code)

    .. deprecated::
        This class uses the old two-class pattern (Model + Property dataclass).
        Use :class:`CauchyContinuumModelNew` for new code, which provides:
        - Built-in validation with Pydantic
        - Cleaner API (direct property access)
        - Better type safety
        - JSON serialization
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
            v = getattr(self.property, name)

        elif name == 'c':
            v = self.property.stff
        elif name == 's':
            v = self.property.cmpl

        # Strength
        elif name == 'x':
            v = self.property.x1t
        elif name in ['x1t', 'x2t', 'x3t', 'x1c', 'x2c', 'x3c', 'x23', 'x13', 'x12']:
            v = getattr(self.property, name)
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
            setattr(self.property, name, value)

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


# ============================================================================
# NEW PYDANTIC MODEL (Recommended Pattern)
# ============================================================================

class CauchyContinuumModelNew(BaseModel):
    """Cauchy continuum model with Pydantic validation.

    This is the new recommended implementation following the beam model pattern.
    All material properties are direct fields with built-in validation.

    Attributes
    ----------
    dim : int
        Dimension of the model (always 3 for 3D continuum)
    label : str
        Model label identifier
    model_name : str
        Human-readable model name
    strain_name : List[str]
        Names of strain components
    stress_name : List[str]
        Names of stress components
    name : str
        Material name
    id : Optional[int]
        Material ID
    isotropy : Literal[0, 1, 2]
        Material isotropy type: 0=Isotropic, 1=Orthotropic, 2=Anisotropic
    density : float
        Material density (must be >= 0)
    temperature : float
        Temperature
    e1, e2, e3 : Optional[float]
        Young's moduli in material directions 1, 2, 3 (must be > 0 if set)
    g12, g13, g23 : Optional[float]
        Shear moduli in material planes 12, 13, 23 (must be > 0 if set)
    nu12, nu13, nu23 : Optional[float]
        Poisson's ratios in material planes 12, 13, 23 (must be in range (-1, 0.5))
    stff : Optional[List[List[float]]]
        6x6 stiffness matrix
    cmpl : Optional[List[List[float]]]
        6x6 compliance matrix
    x1t, x2t, x3t : Optional[float]
        Tensile strengths in directions 1, 2, 3
    x1c, x2c, x3c : Optional[float]
        Compressive strengths in directions 1, 2, 3
    x23, x13, x12 : Optional[float]
        Shear strengths in planes 23, 13, 12
    strength_measure : int
        Strength measure type: 0=stress, 1=strain
    strength_constants : Optional[List[float]]
        Array of strength constants
    char_len : float
        Characteristic length
    cte : Optional[List[float]]
        Thermal expansion coefficients (6 components)
    specific_heat : float
        Specific heat capacity
    failure_criterion : int
        Failure criterion identifier
    d_thetatheta : float
        Thermal property
    f_eff : float
        Effective property
    """

    # Class attributes (model metadata)
    dim: int = 3
    label: str = 'sd1'
    model_name: str = 'Cauchy continuum model'
    strain_name: List[str] = ['e11', 'e22', 'e33', 'e23', 'e13', 'e12']
    stress_name: List[str] = ['s11', 's22', 's33', 's23', 's13', 's12']

    # Basic properties
    name: str = Field(default='', description="Material name")
    id: Optional[int] = Field(default=None, description="Material ID")

    # Material type
    isotropy: Literal[0, 1, 2] = Field(
        default=0,
        description="Isotropy type: 0=Isotropic, 1=Orthotropic, 2=Anisotropic"
    )

    # Inertial properties
    density: float = Field(default=0, ge=0, description="Material density")
    temperature: float = Field(default=0, description="Temperature")

    # Elastic constants (orthotropic)
    e1: Optional[float] = Field(default=None, gt=0, description="Young's modulus E1")
    e2: Optional[float] = Field(default=None, gt=0, description="Young's modulus E2")
    e3: Optional[float] = Field(default=None, gt=0, description="Young's modulus E3")
    g12: Optional[float] = Field(default=None, gt=0, description="Shear modulus G12")
    g13: Optional[float] = Field(default=None, gt=0, description="Shear modulus G13")
    g23: Optional[float] = Field(default=None, gt=0, description="Shear modulus G23")
    nu12: Optional[float] = Field(default=None, description="Poisson's ratio nu12")
    nu13: Optional[float] = Field(default=None, description="Poisson's ratio nu13")
    nu23: Optional[float] = Field(default=None, description="Poisson's ratio nu23")

    # Stiffness/compliance matrices
    stff: Optional[List[List[float]]] = Field(
        default=None,
        description="6x6 stiffness matrix"
    )
    cmpl: Optional[List[List[float]]] = Field(
        default=None,
        description="6x6 compliance matrix"
    )

    # Strength properties
    x1t: Optional[float] = Field(default=None, ge=0, description="Tensile strength X1t")
    x2t: Optional[float] = Field(default=None, ge=0, description="Tensile strength X2t")
    x3t: Optional[float] = Field(default=None, ge=0, description="Tensile strength X3t")
    x1c: Optional[float] = Field(default=None, ge=0, description="Compressive strength X1c")
    x2c: Optional[float] = Field(default=None, ge=0, description="Compressive strength X2c")
    x3c: Optional[float] = Field(default=None, ge=0, description="Compressive strength X3c")
    x23: Optional[float] = Field(default=None, ge=0, description="Shear strength X23")
    x13: Optional[float] = Field(default=None, ge=0, description="Shear strength X13")
    x12: Optional[float] = Field(default=None, ge=0, description="Shear strength X12")

    strength_measure: int = Field(
        default=0,
        description="Strength measure: 0=stress, 1=strain"
    )
    strength_constants: Optional[List[float]] = Field(
        default=None,
        description="Strength constants array"
    )
    char_len: float = Field(default=0, ge=0, description="Characteristic length")

    # Thermal properties
    cte: Optional[List[float]] = Field(
        default=None,
        description="Thermal expansion coefficients (6 components)"
    )
    specific_heat: float = Field(default=0, ge=0, description="Specific heat capacity")

    # Failure properties
    failure_criterion: int = Field(default=0, description="Failure criterion ID")
    d_thetatheta: float = Field(default=0, description="Thermal property")
    f_eff: float = Field(default=0, description="Effective property")

    # Pydantic configuration
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str = '', **data):
        """Initialize model with optional positional name argument for backward compatibility.

        Parameters
        ----------
        name : str, optional
            Material name (can be positional for backward compatibility)
        **data
            Additional keyword arguments for other fields
        """
        if name:
            data['name'] = name
        super().__init__(**data)

    # Field validators
    @field_validator('stff', 'cmpl')
    @classmethod
    def validate_6x6_matrix(cls, v):
        """Validate that stiffness/compliance matrices are 6x6."""
        if v is not None:
            if not isinstance(v, list) or len(v) != 6:
                raise ValueError('Matrix must be 6x6 (6 rows)')
            for i, row in enumerate(v):
                if not isinstance(row, list) or len(row) != 6:
                    raise ValueError(f'Row {i} must have 6 columns')
        return v

    @field_validator('nu12', 'nu13', 'nu23')
    @classmethod
    def validate_poisson_ratio(cls, v):
        """Validate that Poisson's ratios are in valid range."""
        if v is not None and not (-1 < v < 0.5):
            raise ValueError('Poisson ratio must be in range (-1, 0.5)')
        return v

    @field_validator('cte')
    @classmethod
    def validate_cte(cls, v):
        """Validate that CTE has 6 components if provided."""
        if v is not None:
            if not isinstance(v, list) or len(v) != 6:
                raise ValueError('CTE must have 6 components')
        return v

    def __repr__(self) -> str:
        """String representation of the model."""
        constant_name = ['e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu12', 'nu13', 'nu23']
        constant_label = ['E1', 'E2', 'E3', 'G12', 'G13', 'G23', 'nu12', 'nu13', 'nu23']
        strength_name = ['x1t', 'x2t', 'x3t', 'x1c', 'x2c', 'x3c', 'x23', 'x13', 'x12']
        strength_label = ['X1t', 'X2t', 'X3t', 'X1c', 'X2c', 'X3c', 'X23', 'X13', 'X12']

        s = [
            self.model_name,
            '-' * len(self.model_name),
            f'density = {self.density}',
            f'isotropy = {self.isotropy}'
        ]

        s.append('-' * 20)
        s.append('stiffness matrix')
        if self.stff is not None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.stff[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('compliance matrix')
        if self.cmpl is not None:
            for i in range(6):
                _row = []
                for j in range(6):
                    _row.append(f'{self.cmpl[i][j]:14e}')
                s.append(', '.join(_row))
        else:
            s.append('NONE')

        s.append('-' * 20)
        s.append('engineering constants')
        for _label, _name in zip(constant_label, constant_name):
            _value = getattr(self, _name)
            s.append(f'{_label} = {_value}')

        s.append('-' * 20)
        s.append('strength')
        for _label, _name in zip(strength_label, strength_name):
            _value = getattr(self, _name)
            s.append(f'{_label} = {_value}')

        s.append('-' * 20)
        s.append('cte')
        if self.cte is not None:
            s.append('  '.join(list(map(str, self.cte))))
        else:
            s.append('NONE')

        s.append(f'failure criterion = {self.failure_criterion}')

        return '\n'.join(s)

    def __eq__(self, other):
        """Check equality based on all material properties."""
        if not isinstance(other, CauchyContinuumModelNew):
            return False
        return self.model_dump() == other.model_dump()

    def __call__(self, x):
        """Placeholder for model evaluation."""
        return

    # Backward compatibility methods
    def get(self, name: str):
        """Get material properties (backward compatibility with old API).

        Parameters
        ----------
        name : str
            Name of the property to retrieve

        Returns
        -------
        int or float or List
            Value of the specified property

        Notes
        -----
        Supported property names:
        - density, temperature, isotropy
        - e, nu (isotropic shortcuts for e1, nu12)
        - e1, e2, e3, g12, g13, g23, nu12, nu13, nu23
        - c, s (stiffness/compliance matrices)
        - cij, sij (matrix components, i,j=1..6)
        - x (shortcut for x1t)
        - x1t, x2t, x3t, x1c, x2c, x3c, x23, x13, x12
        - strength, char_len, failure_criterion
        - cte, alpha, alphaij (thermal expansion)
        - specific_heat
        """
        v = None

        if name == 'density':
            v = self.density
        elif name == 'temperature':
            v = self.temperature
        elif name == 'isotropy':
            v = self.isotropy

        # Stiffness
        elif name == 'e':
            v = self.e1
        elif name == 'nu':
            v = self.nu12
        elif name in ['e1', 'e2', 'e3', 'g12', 'g13', 'g23', 'nu12', 'nu13', 'nu23']:
            v = getattr(self, name)

        elif name == 'c':
            v = self.stff
        elif name == 's':
            v = self.cmpl

        # Strength
        elif name == 'x':
            v = self.x1t
        elif name in ['x1t', 'x2t', 'x3t', 'x1c', 'x2c', 'x3c', 'x23', 'x13', 'x12']:
            v = getattr(self, name)
        elif name == 'strength':
            v = self.strength_constants
        elif name == 'char_len':
            v = self.char_len
        elif name == 'failure_criterion':
            v = self.failure_criterion

        # Thermal
        elif name == 'cte':
            v = self.cte
        elif name == 'specific_heat':
            v = self.specific_heat

        elif name.startswith('alpha'):
            if name == 'alpha':
                v = self.cte[0] if self.cte is not None else None
            else:
                _ij = name[-2:]
                for _k, __ij in enumerate(['11', '22', '33', '23', '13', '12']):
                    if _ij == __ij:
                        v = self.cte[_k] if self.cte is not None else None
                        break
        elif name.startswith('c') and len(name) == 3:
            _i = int(name[1]) - 1
            _j = int(name[2]) - 1
            v = self.stff[_i][_j] if self.stff is not None else None
        elif name.startswith('s') and len(name) == 3:
            _i = int(name[1]) - 1
            _j = int(name[2]) - 1
            v = self.cmpl[_i][_j] if self.cmpl is not None else None

        return v

    def set(self, name: str, value, **kwargs):
        """Set material properties (backward compatibility with old API).

        Parameters
        ----------
        name : str
            Name of the property to set
        value : str or int or float or List
            Value to set
        **kwargs
            Additional keyword arguments (e.g., input_type for elastic)
        """
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
            self.setElastic(value, **kwargs)

        elif name == 'strength_constants':
            if len(value) == 9:
                self.x1t = value[0]
                self.x2t = value[1]
                self.x3t = value[2]
                self.x1c = value[3]
                self.x2c = value[4]
                self.x3c = value[5]
                self.x23 = value[6]
                self.x13 = value[7]
                self.x12 = value[8]

            self.strength_constants = value

        else:
            # Direct attribute setting
            setattr(self, name, value)

        return

    def setElastic(self, consts: Iterable, input_type='', **kwargs):
        """Set elastic properties based on isotropy type.

        Parameters
        ----------
        consts : Iterable
            Elastic constants (format depends on isotropy and input_type)
        input_type : str, optional
            Type of input: 'lamina', 'engineering', 'orthotropic', 'stiffness', 'compliance'
        **kwargs
            Additional keyword arguments
        """
        if self.isotropy == 0:
            # Isotropic: [E, nu]
            self.e1 = float(consts[0])
            self.nu12 = float(consts[1])

        elif self.isotropy == 1:
            # Orthotropic
            if input_type == 'lamina':
                # [E1, E2, G12, nu12]
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
                # [E1, E2, E3, G12, G13, G23, nu12, nu13, nu23]
                self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
                self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
                self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))
            elif input_type == 'orthotropic':
                # TODO: implement orthotropic input
                pass
            else:
                # Default: same as engineering
                self.e1, self.e2, self.e3 = list(map(float, consts[:3]))
                self.g12, self.g13, self.g23 = list(map(float, consts[3:6]))
                self.nu12, self.nu13, self.nu23 = list(map(float, consts[6:]))

        elif self.isotropy == 2:
            # Anisotropic: provide full matrices
            if input_type == 'stiffness':
                self.stff = consts
            elif input_type == 'compliance':
                self.cmpl = consts

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


