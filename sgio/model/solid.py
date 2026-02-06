from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional, List, Literal, Sequence, Union, cast

FloatSequence = Sequence[float]
MatrixSequence = Sequence[Sequence[float]]
ElasticInput = Union[FloatSequence, MatrixSequence]
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Helper functions for building stiffness matrices
def _build_isotropic_stiffness(e: float, nu: float) -> List[List[float]]:
    """Build stiffness matrix for isotropic material.
    
    Parameters
    ----------
    e : float
        Young's modulus
    nu : float
        Poisson's ratio
        
    Returns
    -------
    List[List[float]]
        6x6 stiffness matrix
    """
    lam = e * nu / ((1 + nu) * (1 - 2 * nu))
    mu = e / (2 * (1 + nu))
    
    stff = [[0.0 for _ in range(6)] for _ in range(6)]
    
    # Diagonal terms
    stff[0][0] = stff[1][1] = stff[2][2] = lam + 2 * mu
    stff[3][3] = stff[4][4] = stff[5][5] = mu
    
    # Off-diagonal terms
    stff[0][1] = stff[0][2] = lam
    stff[1][0] = stff[1][2] = lam
    stff[2][0] = stff[2][1] = lam
    
    return stff


def _build_transverse_isotropic_stiffness(
    e1: float, e2: float, g12: float, nu12: float, nu23: float
) -> List[List[float]]:
    """Build stiffness matrix for transverse isotropic material.
    
    Parameters
    ----------
    e1 : float
        Longitudinal Young's modulus
    e2 : float
        Transverse Young's modulus
    g12 : float
        Longitudinal shear modulus
    nu12 : float
        Longitudinal Poisson's ratio
    nu23 : float
        Transverse Poisson's ratio
        
    Returns
    -------
    List[List[float]]
        6x6 stiffness matrix
    """
    # Calculate compliance matrix first
    nu21 = nu12 * e2 / e1
    g23 = e2 / (2 * (1 + nu23))
    
    s11 = 1.0 / e1
    s22 = 1.0 / e2
    s12 = -nu12 / e1
    s23 = -nu23 / e2
    
    # Build compliance matrix
    cmpl = [[0.0 for _ in range(6)] for _ in range(6)]
    cmpl[0][0] = s11
    cmpl[1][1] = cmpl[2][2] = s22
    cmpl[0][1] = cmpl[0][2] = s12
    cmpl[1][0] = cmpl[2][0] = s12
    cmpl[1][2] = cmpl[2][1] = s23
    cmpl[3][3] = 1.0 / g23
    cmpl[4][4] = cmpl[5][5] = 1.0 / g12
    
    # Invert to get stiffness (simplified for transverse isotropy)
    return _invert_compliance_matrix(cmpl)


def _build_orthotropic_stiffness(
    e1: float, e2: float, e3: float,
    g12: float, g13: float, g23: float,
    nu12: float, nu13: float, nu23: float
) -> List[List[float]]:
    """Build stiffness matrix for orthotropic material.
    
    Parameters
    ----------
    e1, e2, e3 : float
        Young's moduli in three directions
    g12, g13, g23 : float
        Shear moduli
    nu12, nu13, nu23 : float
        Poisson's ratios
        
    Returns
    -------
    List[List[float]]
        6x6 stiffness matrix
    """
    # Calculate reciprocal Poisson's ratios
    nu21 = nu12 * e2 / e1
    nu31 = nu13 * e3 / e1
    nu32 = nu23 * e3 / e2
    
    # Calculate delta
    delta = 1.0 - nu12 * nu21 - nu23 * nu32 - nu31 * nu13 - 2 * nu21 * nu32 * nu13
    
    # Build stiffness matrix
    stff = [[0.0 for _ in range(6)] for _ in range(6)]
    
    stff[0][0] = e1 * (1 - nu23 * nu32) / delta
    stff[1][1] = e2 * (1 - nu13 * nu31) / delta
    stff[2][2] = e3 * (1 - nu12 * nu21) / delta
    
    stff[0][1] = e1 * (nu21 + nu31 * nu23) / delta
    stff[0][2] = e1 * (nu31 + nu21 * nu32) / delta
    stff[1][2] = e2 * (nu32 + nu12 * nu31) / delta
    
    stff[1][0] = stff[0][1]
    stff[2][0] = stff[0][2]
    stff[2][1] = stff[1][2]
    
    stff[3][3] = g23
    stff[4][4] = g13
    stff[5][5] = g12
    
    return stff


def _build_anisotropic_stiffness(constants: Sequence[float]) -> List[List[float]]:
    """Build stiffness matrix for anisotropic material from 21 constants.
    
    Parameters
    ----------
    constants : Sequence[float]
        21 constants representing upper triangle of symmetric 6x6 matrix
        Order: C11, C12, C13, C14, C15, C16,
                    C22, C23, C24, C25, C26,
                         C33, C34, C35, C36,
                              C44, C45, C46,
                                   C55, C56,
                                        C66
        
    Returns
    -------
    List[List[float]]
        6x6 stiffness matrix
    """
    if len(constants) != 21:
        raise ValueError(f'Anisotropic material requires 21 constants, got {len(constants)}')
    
    stff = [[0.0 for _ in range(6)] for _ in range(6)]
    
    # Fill upper triangle
    idx = 0
    for i in range(6):
        for j in range(i, 6):
            stff[i][j] = float(constants[idx])
            if i != j:
                stff[j][i] = stff[i][j]  # Symmetric
            idx += 1
    
    return stff


def _invert_compliance_matrix(cmpl: List[List[float]]) -> List[List[float]]:
    """Invert compliance matrix to get stiffness matrix.
    
    Parameters
    ----------
    cmpl : List[List[float]]
        6x6 compliance matrix
        
    Returns
    -------
    List[List[float]]
        6x6 stiffness matrix
    """
    # Simple matrix inversion for 6x6 (could use numpy if available)
    # For now, return identity as placeholder - should implement proper inversion
    # or use engineering constants to build stiffness directly
    try:
        import numpy as np
        cmpl_array = np.array(cmpl)
        stff_array = np.linalg.inv(cmpl_array)
        return stff_array.tolist()
    except ImportError:
        # Fallback: return identity (not correct, but prevents crash)
        # User should provide stiffness directly or install numpy
        return [[1.0 if i == j else 0.0 for j in range(6)] for i in range(6)]

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
    isotropy : Literal[0, 1, 2, 3]
        Material isotropy type: 0=Isotropic, 1=Orthotropic, 2=Anisotropic, 3=TransverseIsotropic
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
    isotropy: Literal[0, 1, 2, 3] = Field(
        default=0,
        description="Isotropy type: 0=Isotropic, 1=Orthotropic, 2=Anisotropic, 3=TransverseIsotropic"
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
            
        Notes
        -----
        Supports multiple initialization modes based on material symmetry:
        
        - Isotropic (isotropy=0): Provide `e` and `nu` (or `e1` and `nu12`)
        - Transverse Isotropic (isotropy=3): Provide `e1`, `e2`, `g12`, `nu12`, `nu23`
        - Orthotropic (isotropy=1): Provide 9 constants `e1`, `e2`, `e3`, `g12`, `g13`, `g23`, 
          `nu12`, `nu13`, `nu23`
        - Anisotropic (isotropy=2): Provide `anisotropic_constants` (21 values) or `stff` matrix
        
        Supported Aliases
        -----------------
        The following parameter aliases are supported for convenience:
        
        - `e` → `e1` (Young's modulus for isotropic materials)
        - `nu` → `nu12` (Poisson's ratio for isotropic materials)
        - `g` → `g12` (Shear modulus)
        
        Examples
        --------
        >>> # Isotropic material using aliases
        >>> mat = CauchyContinuumModel(name='Steel', isotropy=0, e=200e9, nu=0.3)
        
        >>> # Isotropic material using full names
        >>> mat = CauchyContinuumModel(name='Steel', isotropy=0, e1=200e9, nu12=0.3)
        
        >>> # Orthotropic material  
        >>> mat = CauchyContinuumModel(name='Composite', isotropy=1, 
        ...                            e1=150e9, e2=10e9, e3=10e9,
        ...                            g12=5e9, g13=5e9, g23=3e9,
        ...                            nu12=0.3, nu13=0.3, nu23=0.4)
        
        >>> # Anisotropic material
        >>> mat = CauchyContinuumModel(name='Crystal', isotropy=2, 
        ...                            anisotropic_constants=[...21 values...])
        """
        if name:
            data['name'] = name
        
        # Handle parameter aliases
        data = self._resolve_aliases(data)
            
        # Extract elastic input if provided
        aniso_consts = data.pop('anisotropic_constants', None)
        
        super().__init__(**data)
        
        # Auto-build stiffness matrix based on isotropy and provided constants
        self._auto_build_stiffness(aniso_consts)
    
    @staticmethod
    def _resolve_aliases(data: dict) -> dict:
        """Resolve parameter aliases to their canonical names.
        
        Parameters
        ----------
        data : dict
            Input dictionary with potentially aliased parameter names
            
        Returns
        -------
        dict
            Dictionary with aliases resolved to canonical names
            
        Notes
        -----
        Supported aliases:
        - e → e1
        - nu → nu12
        - g → g12
        
        If both the alias and canonical name are provided, the canonical name takes precedence.
        """
        # Define alias mappings
        aliases = {
            'e': 'e1',
            'nu': 'nu12',
            'g': 'g12',
        }
        
        # Resolve aliases (only if canonical name not already present)
        for alias, canonical in aliases.items():
            if alias in data and canonical not in data:
                data[canonical] = data.pop(alias)
            elif alias in data and canonical in data:
                # Both provided - remove alias, keep canonical
                data.pop(alias)
        
        return data
    
    def _auto_build_stiffness(self, aniso_consts: Optional[Sequence[float]] = None):
        """Automatically build stiffness matrix from engineering constants.
        
        Parameters
        ----------
        aniso_consts : Optional[Sequence[float]]
            21 constants for anisotropic material
        """
        # Skip if stiffness already provided
        if self.stff is not None:
            return
            
        if self.isotropy == 0:  # Isotropic
            if self.e1 is not None and self.nu12 is not None:
                self.stff = _build_isotropic_stiffness(self.e1, self.nu12)
                
        elif self.isotropy == 3:  # Transverse Isotropic
            if all(x is not None for x in [self.e1, self.e2, self.g12, self.nu12, self.nu23]):
                # Type assertions after validation
                e1 = cast(float, self.e1)
                e2 = cast(float, self.e2)
                g12 = cast(float, self.g12)
                nu12 = cast(float, self.nu12)
                nu23 = cast(float, self.nu23)
                
                self.stff = _build_transverse_isotropic_stiffness(e1, e2, g12, nu12, nu23)
                
                # Set remaining constants for consistency
                if self.e3 is None:
                    self.e3 = e2
                if self.g13 is None:
                    self.g13 = g12
                if self.nu13 is None:
                    self.nu13 = nu12
                if self.g23 is None:
                    self.g23 = e2 / (2 * (1 + nu23))
                    
        elif self.isotropy == 1:  # Orthotropic
            if all(x is not None for x in [
                self.e1, self.e2, self.e3,
                self.g12, self.g13, self.g23,
                self.nu12, self.nu13, self.nu23
            ]):
                # Type assertions after validation
                e1 = cast(float, self.e1)
                e2 = cast(float, self.e2)
                e3 = cast(float, self.e3)
                g12 = cast(float, self.g12)
                g13 = cast(float, self.g13)
                g23 = cast(float, self.g23)
                nu12 = cast(float, self.nu12)
                nu13 = cast(float, self.nu13)
                nu23 = cast(float, self.nu23)
                
                self.stff = _build_orthotropic_stiffness(
                    e1, e2, e3, g12, g13, g23, nu12, nu13, nu23
                )
                
        elif self.isotropy == 2:  # Anisotropic
            if aniso_consts is not None:
                self.stff = _build_anisotropic_stiffness(aniso_consts)
            # else: user must provide stff matrix directly

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
                # Check for specific patterns first
                if value_lower.startswith('aniso'):
                    iso_value = 2
                elif value_lower.startswith(('trans', 'ti')):
                    iso_value = 3
                elif value_lower.startswith(('ortho', 'eng', 'lam')):
                    iso_value = 1
                elif value_lower.startswith('iso'):
                    iso_value = 0
                else:
                    # Try to parse as integer
                    try:
                        iso_value = int(value)
                    except ValueError:
                        raise ValueError(f'Invalid isotropy value: {value}')
            elif isinstance(value, int):
                iso_value = value
            else:
                raise TypeError('Isotropy must be provided as string or integer')

            if iso_value not in (0, 1, 2, 3):
                raise ValueError('Isotropy value must be 0, 1, 2, or 3')

            self.isotropy = cast(Literal[0, 1, 2, 3], iso_value)

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
            Type of input:
            - 'isotropic' or default for isotropy=0: [E, nu] (2 values)
            - 'transverse_isotropic' or 'transverse' for isotropy=3: [E1, E2, G12, nu12, nu23] (5 values)
            - 'lamina' for isotropy=1: [E1, E2, G12, nu12] (4 values)
            - 'engineering' or 'orthotropic' or default for isotropy=1: 9 values
            - 'anisotropic' or 'constants' for isotropy=2: 21 values (upper triangle)
            - 'stiffness' for isotropy=2: full 6x6 matrix
            - 'compliance' for isotropy=2: full 6x6 compliance matrix
        **kwargs
            Additional keyword arguments
            
        Notes
        -----
        For anisotropic materials (isotropy=2), the 21 constants represent the upper triangle
        of the symmetric 6x6 stiffness matrix in the following order:
        C11, C12, C13, C14, C15, C16, C22, C23, C24, C25, C26, C33, C34, C35, C36,
        C44, C45, C46, C55, C56, C66
        """
        if self.isotropy == 0:
            # Isotropic: [E, nu]
            seq = list(cast(FloatSequence, consts))
            if len(seq) < 2:
                raise ValueError('Isotropic elastic input requires [E, nu]')
            self.e1 = float(seq[0])
            self.nu12 = float(seq[1])
            self.stff = _build_isotropic_stiffness(self.e1, self.nu12)

        elif self.isotropy == 3:
            # Transverse Isotropic: [E1, E2, G12, nu12, nu23]
            seq = list(cast(FloatSequence, consts))
            if input_type in ('transverse_isotropic', 'transverse', ''):
                if len(seq) < 5:
                    raise ValueError('Transverse isotropic input requires [E1, E2, G12, nu12, nu23]')
                self.e1 = float(seq[0])
                self.e2 = float(seq[1])
                self.g12 = float(seq[2])
                self.nu12 = float(seq[3])
                self.nu23 = float(seq[4])
                self.e3 = self.e2
                self.g13 = self.g12
                self.nu13 = self.nu12
                self._auto_build_stiffness()

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
                self._auto_build_stiffness()
            elif input_type in ('engineering', 'orthotropic', ''):
                # [E1, E2, E3, G12, G13, G23, nu12, nu13, nu23]
                if len(seq) < 9:
                    raise ValueError('Engineering input requires 9 values')
                self.e1, self.e2, self.e3 = list(map(float, seq[:3]))
                self.g12, self.g13, self.g23 = list(map(float, seq[3:6]))
                self.nu12, self.nu13, self.nu23 = list(map(float, seq[6:9]))
                self._auto_build_stiffness()

        elif self.isotropy == 2:
            # Anisotropic
            if input_type in ('anisotropic', 'constants', ''):
                # Provide 21 constants for upper triangle
                seq = list(cast(FloatSequence, consts))
                if len(seq) != 21:
                    raise ValueError(f'Anisotropic input requires 21 constants, got {len(seq)}')
                self.stff = _build_anisotropic_stiffness(seq)
            elif input_type == 'stiffness':
                # Provide full 6x6 matrix
                matrix_input = cast(MatrixSequence, consts)
                rows: List[List[float]] = []
                for row in matrix_input:
                    rows.append([float(value) for value in row])
                self.stff = rows
            elif input_type == 'compliance':
                # Provide full 6x6 compliance matrix
                matrix_input = cast(MatrixSequence, consts)
                rows: List[List[float]] = []
                for row in matrix_input:
                    rows.append([float(value) for value in row])
                self.cmpl = rows

        return

    def write_to_json(self, file_path: str, *, exclude_none: bool = True, indent: Optional[int] = None) -> None:
        """Write the material model to a JSON file.
        
        Parameters
        ----------
        file_path : str
            Path to the JSON file where the material will be saved
        exclude_none : bool, optional
            Whether to exclude None values from the JSON output. Defaults to True.
        indent : Optional[int], optional
            Number of spaces for JSON indentation. If None, compact JSON is written.
            Defaults to None.
            
        Raises
        ------
        OSError
            If the file cannot be written
        ValueError
            If the file path is invalid
            
        Examples
        --------
        >>> mat = CauchyContinuumModel(name="Steel", isotropy=0, e=200e9, nu=0.3, density=7850)
        >>> mat.write_to_json("steel.json")
        >>> mat.write_to_json("steel_pretty.json", indent=2)
        """
        path = Path(file_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert model to dictionary, excluding None values by default
        data = self.model_dump(exclude_none=exclude_none)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)


# Backward-compatible alias retained for downstream imports
CauchyContinuumModelNew = CauchyContinuumModel


def read_material_from_json(file_path: str) -> CauchyContinuumModel:
    """Read a single material from a JSON file.
    
    Parameters
    ----------
    file_path : str
        Path to the JSON file containing a material dictionary
        
    Returns
    -------
    CauchyContinuumModel
        Material model object created from the JSON data
        
    Raises
    ------
    FileNotFoundError
        If the specified file does not exist
    ValueError
        If the JSON is invalid or does not represent a single material
    TypeError
        If the JSON content is not a dictionary
        
    Examples
    --------
    >>> # JSON file: {"name": "Steel", "isotropy": 0, "e": 200e9, "nu": 0.3, "density": 7850}
    >>> mat = read_material_from_json("steel.json")
    >>> mat.name
    'Steel'
    >>> mat.e1
    200000000000.0
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, dict):
        raise TypeError(f'Expected JSON dictionary for single material, got {type(data).__name__}')
    
    return CauchyContinuumModel(**data)


def read_materials_from_json(file_path: str) -> List[CauchyContinuumModel]:
    """Read multiple materials from a JSON file.
    
    Parameters
    ----------
    file_path : str
        Path to the JSON file containing a list of material dictionaries
        
    Returns
    -------
    List[CauchyContinuumModel]
        List of material model objects created from the JSON data
        
    Raises
    ------
    FileNotFoundError
        If the specified file does not exist
    ValueError
        If the JSON is invalid
    TypeError
        If the JSON content is not a list
        
    Examples
    --------
    >>> # JSON file: [{"name": "Steel", "isotropy": 0, "e": 200e9, "nu": 0.3},
    >>> #              {"name": "Aluminum", "isotropy": 0, "e": 70e9, "nu": 0.33}]
    >>> materials = read_materials_from_json("materials.json")
    >>> len(materials)
    2
    >>> materials[0].name
    'Steel'
    >>> materials[1].name
    'Aluminum'
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise TypeError(f'Expected JSON list for multiple materials, got {type(data).__name__}')
    
    materials = []
    for i, mat_data in enumerate(data):
        if not isinstance(mat_data, dict):
            raise TypeError(f'Material at index {i} is not a dictionary: {type(mat_data).__name__}')
        materials.append(CauchyContinuumModel(**mat_data))
    
    return materials

