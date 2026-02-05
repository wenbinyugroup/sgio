from __future__ import annotations

from typing import Iterable, Optional, List, Literal, Sequence, Union, cast

FloatSequence = Sequence[float]
MatrixSequence = Sequence[Sequence[float]]
ElasticInput = Union[FloatSequence, MatrixSequence]
from pydantic import BaseModel, Field, field_validator, ConfigDict

class CauchyContinuumModel(BaseModel):
    """Cauchy continuum model with Pydantic validation.

    This implementation follows the beam model pattern and provides
    built-in validation for all material properties.

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
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

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
        if not isinstance(other, CauchyContinuumModel):
            return False
        return self.model_dump() == other.model_dump()

    def __call__(self, x):
        """Placeholder for model evaluation."""
        return

    # Property aliases -----------------------------------------------------

    @property
    def e(self) -> Optional[float]:
        """Legacy alias for the isotropic Young's modulus."""

        return self.e1

    @e.setter
    def e(self, value: float) -> None:
        self.e1 = float(value)

    @property
    def nu(self) -> Optional[float]:
        """Legacy alias for the isotropic Poisson ratio."""

        return self.nu12

    @nu.setter
    def nu(self, value: float) -> None:
        self.nu12 = float(value)

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
            iso_value: Optional[int] = None
            if isinstance(value, str):
                value_lower = value.lower()
                if value_lower.startswith('iso'):
                    iso_value = 0
                elif value_lower.startswith(('ortho', 'eng', 'lam')):
                    iso_value = 1
                elif value_lower.startswith('aniso'):
                    iso_value = 2
                else:
                    iso_value = int(value)
            elif isinstance(value, int):
                iso_value = value
            else:
                raise TypeError('Isotropy must be provided as string or integer')

            if iso_value not in (0, 1, 2):
                raise ValueError('Isotropy value must be 0, 1, or 2')

            self.isotropy = cast(Literal[0, 1, 2], iso_value)

        elif name == 'elastic':
            self.setElastic(value, **kwargs)

        elif name == 'strength_constants':
            values = list(value)
            if len(values) == 9:
                self.x1t = values[0]
                self.x2t = values[1]
                self.x3t = values[2]
                self.x1c = values[3]
                self.x2c = values[4]
                self.x3c = values[5]
                self.x23 = values[6]
                self.x13 = values[7]
                self.x12 = values[8]

            self.strength_constants = values

        else:
            # Direct attribute setting
            setattr(self, name, value)

        return

    def setElastic(
        self,
        consts: ElasticInput,
        input_type: str = '',
        **kwargs,
    ):
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
            seq = list(cast(FloatSequence, consts))
            if len(seq) < 2:
                raise ValueError('Isotropic elastic input requires [E, nu]')
            self.e1 = float(seq[0])
            self.nu12 = float(seq[1])

        elif self.isotropy == 1:
            # Orthotropic
            seq = list(cast(FloatSequence, consts))
            if input_type == 'lamina':
                # [E1, E2, G12, nu12]
                if len(seq) < 4:
                    raise ValueError('Lamina input requires 4 values [E1, E2, G12, nu12]')
                self.e1 = float(seq[0])
                self.e2 = float(seq[1])
                self.g12 = float(seq[2])
                self.nu12 = float(seq[3])
                self.e3 = self.e2
                self.g13 = self.g12
                self.nu13 = self.nu12
                self.nu23 = 0.3
                self.g23 = self.e3 / (2.0 * (1 + self.nu23))
            elif input_type == 'engineering':
                # [E1, E2, E3, G12, G13, G23, nu12, nu13, nu23]
                if len(seq) < 9:
                    raise ValueError('Engineering input requires 9 values')
                self.e1, self.e2, self.e3 = list(map(float, seq[:3]))
                self.g12, self.g13, self.g23 = list(map(float, seq[3:6]))
                self.nu12, self.nu13, self.nu23 = list(map(float, seq[6:9]))
            elif input_type == 'orthotropic':
                # TODO: implement orthotropic input
                pass
            else:
                # Default: same as engineering
                if len(seq) < 9:
                    raise ValueError('Orthotropic input requires 9 values')
                self.e1, self.e2, self.e3 = list(map(float, seq[:3]))
                self.g12, self.g13, self.g23 = list(map(float, seq[3:6]))
                self.nu12, self.nu13, self.nu23 = list(map(float, seq[6:9]))

        elif self.isotropy == 2:
            # Anisotropic: provide full matrices
            matrix_input = cast(MatrixSequence, consts)
            rows: List[List[float]] = []
            for row in matrix_input:
                rows.append([float(value) for value in row])
            if input_type == 'stiffness':
                self.stff = rows
            elif input_type == 'compliance':
                self.cmpl = rows

        return


# Backward-compatible alias retained for downstream imports
CauchyContinuumModelNew = CauchyContinuumModel

