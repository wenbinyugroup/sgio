"""Test different material symmetries for CauchyContinuumModel."""

import pytest
from sgio.model.solid import CauchyContinuumModel


class TestIsotropicMaterial:
    """Test isotropic material initialization."""
    
    def test_init_with_e_and_nu(self):
        """Test initialization with E and nu."""
        mat = CauchyContinuumModel(
            name='Steel',
            isotropy=0,
            e1=200e9,
            nu12=0.3
        )
        assert mat.e1 == 200e9
        assert mat.nu12 == 0.3
        assert mat.stff is not None
        assert len(mat.stff) == 6
        
    def test_init_using_e_nu_properties(self):
        """Test initialization using e and nu property aliases."""
        mat = CauchyContinuumModel(
            name='Steel',
            isotropy=0
        )
        mat.e = 200e9
        mat.nu = 0.3
        mat._auto_build_stiffness()
        
        assert mat.e == 200e9
        assert mat.nu == 0.3
        assert mat.stff is not None
        
    def test_setElastic_isotropic(self):
        """Test setElastic with isotropic constants."""
        mat = CauchyContinuumModel(name='Aluminum', isotropy=0)
        mat.setElastic([70e9, 0.33])
        
        assert mat.e1 == 70e9
        assert mat.nu12 == 0.33
        assert mat.stff is not None
        
    def test_stiffness_matrix_symmetry(self):
        """Test that stiffness matrix is symmetric."""
        mat = CauchyContinuumModel(name='Steel', isotropy=0, e1=200e9, nu12=0.3)
        
        for i in range(6):
            for j in range(6):
                assert abs(mat.stff[i][j] - mat.stff[j][i]) < 1e-6


class TestTransverseIsotropicMaterial:
    """Test transverse isotropic material initialization."""
    
    def test_init_with_5_constants(self):
        """Test initialization with 5 constants."""
        mat = CauchyContinuumModel(
            name='Fiber',
            isotropy=3,
            e1=150e9,
            e2=10e9,
            g12=5e9,
            nu12=0.3,
            nu23=0.4
        )
        
        assert mat.e1 == 150e9
        assert mat.e2 == 10e9
        assert mat.e3 == 10e9  # Should be set equal to e2
        assert mat.g12 == 5e9
        assert mat.g13 == 5e9  # Should be set equal to g12
        assert mat.nu12 == 0.3
        assert mat.nu13 == 0.3  # Should be set equal to nu12
        assert mat.nu23 == 0.4
        assert mat.stff is not None
        
    def test_setElastic_transverse(self):
        """Test setElastic with transverse isotropic constants."""
        mat = CauchyContinuumModel(name='Composite', isotropy=3)
        mat.setElastic([150e9, 10e9, 5e9, 0.3, 0.4], input_type='transverse_isotropic')
        
        assert mat.e1 == 150e9
        assert mat.e2 == 10e9
        assert mat.stff is not None


class TestOrthotropicMaterial:
    """Test orthotropic material initialization."""
    
    def test_init_with_9_constants(self):
        """Test initialization with 9 engineering constants."""
        mat = CauchyContinuumModel(
            name='Composite',
            isotropy=1,
            e1=150e9,
            e2=10e9,
            e3=10e9,
            g12=5e9,
            g13=5e9,
            g23=3e9,
            nu12=0.3,
            nu13=0.3,
            nu23=0.4
        )
        
        assert mat.e1 == 150e9
        assert mat.e2 == 10e9
        assert mat.e3 == 10e9
        assert mat.stff is not None
        
    def test_setElastic_engineering(self):
        """Test setElastic with engineering constants."""
        mat = CauchyContinuumModel(name='Wood', isotropy=1)
        mat.setElastic(
            [150e9, 10e9, 10e9, 5e9, 5e9, 3e9, 0.3, 0.3, 0.4],
            input_type='engineering'
        )
        
        assert mat.e1 == 150e9
        assert mat.e2 == 10e9
        assert mat.e3 == 10e9
        assert mat.stff is not None
        
    def test_setElastic_lamina(self):
        """Test setElastic with lamina input (4 constants)."""
        mat = CauchyContinuumModel(name='Lamina', isotropy=1)
        mat.setElastic([150e9, 10e9, 5e9, 0.3], input_type='lamina')
        
        assert mat.e1 == 150e9
        assert mat.e2 == 10e9
        assert mat.g12 == 5e9
        assert mat.nu12 == 0.3
        assert mat.e3 == mat.e2
        assert mat.stff is not None


class TestAnisotropicMaterial:
    """Test anisotropic material initialization."""
    
    def test_init_with_21_constants(self):
        """Test initialization with 21 constants (upper triangle)."""
        # Example constants (not physically meaningful, just for testing)
        constants = [
            # Row 0: C11, C12, C13, C14, C15, C16
            100e9, 50e9, 50e9, 0, 0, 0,
            # Row 1: C22, C23, C24, C25, C26
            100e9, 50e9, 0, 0, 0,
            # Row 2: C33, C34, C35, C36
            100e9, 0, 0, 0,
            # Row 3: C44, C45, C46
            25e9, 0, 0,
            # Row 4: C55, C56
            25e9, 0,
            # Row 5: C66
            25e9
        ]
        
        mat = CauchyContinuumModel(
            name='Crystal',
            isotropy=2,
            anisotropic_constants=constants
        )
        
        assert mat.stff is not None
        assert mat.stff[0][0] == 100e9
        assert mat.stff[0][1] == 50e9
        assert mat.stff[1][0] == 50e9  # Symmetry
        assert mat.stff[5][5] == 25e9
        
    def test_setElastic_anisotropic_constants(self):
        """Test setElastic with 21 anisotropic constants."""
        constants = [
            100e9, 50e9, 50e9, 0, 0, 0,
            100e9, 50e9, 0, 0, 0,
            100e9, 0, 0, 0,
            25e9, 0, 0,
            25e9, 0,
            25e9
        ]
        
        mat = CauchyContinuumModel(name='Crystal', isotropy=2)
        mat.setElastic(constants, input_type='anisotropic')
        
        assert mat.stff is not None
        assert mat.stff[0][0] == 100e9
        
    def test_setElastic_stiffness_matrix(self):
        """Test setElastic with full 6x6 stiffness matrix."""
        stiff_matrix = [
            [100e9, 50e9, 50e9, 0, 0, 0],
            [50e9, 100e9, 50e9, 0, 0, 0],
            [50e9, 50e9, 100e9, 0, 0, 0],
            [0, 0, 0, 25e9, 0, 0],
            [0, 0, 0, 0, 25e9, 0],
            [0, 0, 0, 0, 0, 25e9]
        ]
        
        mat = CauchyContinuumModel(name='Custom', isotropy=2)
        mat.setElastic(stiff_matrix, input_type='stiffness')
        
        assert mat.stff is not None
        assert mat.stff[0][0] == 100e9
        assert mat.stff[3][3] == 25e9
        
    def test_anisotropic_symmetry(self):
        """Test that anisotropic stiffness matrix is symmetric."""
        constants = [
            100e9, 50e9, 50e9, 1e9, 2e9, 3e9,
            100e9, 50e9, 4e9, 5e9, 6e9,
            100e9, 7e9, 8e9, 9e9,
            25e9, 10e9, 11e9,
            25e9, 12e9,
            25e9
        ]
        
        mat = CauchyContinuumModel(
            name='General',
            isotropy=2,
            anisotropic_constants=constants
        )
        
        # Check symmetry
        for i in range(6):
            for j in range(6):
                assert abs(mat.stff[i][j] - mat.stff[j][i]) < 1e-6


class TestInputValidation:
    """Test input validation for different material types."""
    
    def test_isotropic_missing_constants(self):
        """Test error when isotropic constants are missing."""
        mat = CauchyContinuumModel(name='Test', isotropy=0)
        with pytest.raises(ValueError):
            mat.setElastic([200e9])  # Missing nu
            
    def test_orthotropic_missing_constants(self):
        """Test error when orthotropic constants are missing."""
        mat = CauchyContinuumModel(name='Test', isotropy=1)
        with pytest.raises(ValueError):
            mat.setElastic([150e9, 10e9, 10e9])  # Only 3 values
            
    def test_anisotropic_wrong_count(self):
        """Test error when anisotropic constants have wrong count."""
        mat = CauchyContinuumModel(name='Test', isotropy=2)
        with pytest.raises(ValueError):
            mat.setElastic([100e9] * 20, input_type='anisotropic')  # Need 21
            
    def test_transverse_missing_constants(self):
        """Test error when transverse isotropic constants are missing."""
        mat = CauchyContinuumModel(name='Test', isotropy=3)
        with pytest.raises(ValueError):
            mat.setElastic([150e9, 10e9, 5e9])  # Only 3 values, need 5


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""
    
    def test_legacy_get_set(self):
        """Test legacy get/set methods."""
        mat = CauchyContinuumModel(name='Legacy', isotropy=0)
        mat.set('elastic', [200e9, 0.3])
        
        assert mat.get('e') == 200e9
        assert mat.get('nu') == 0.3
        
    def test_legacy_isotropy_setting(self):
        """Test legacy isotropy setting with strings."""
        mat = CauchyContinuumModel(name='Test')
        
        mat.set('isotropy', 'isotropic')
        assert mat.isotropy == 0
        
        mat.set('isotropy', 'orthotropic')
        assert mat.isotropy == 1
        
        mat.set('isotropy', 'anisotropic')
        assert mat.isotropy == 2
        
        mat.set('isotropy', 'transverse')
        assert mat.isotropy == 3


class TestParameterAliases:
    """Test parameter alias functionality."""
    
    def test_e_alias_for_e1(self):
        """Test that 'e' is aliased to 'e1'."""
        mat = CauchyContinuumModel(name='Steel', isotropy=0, e=200e9, nu=0.3)
        
        assert mat.e1 == 200e9
        assert mat.e == 200e9  # Property alias should also work
        
    def test_nu_alias_for_nu12(self):
        """Test that 'nu' is aliased to 'nu12'."""
        mat = CauchyContinuumModel(name='Steel', isotropy=0, e=200e9, nu=0.3)
        
        assert mat.nu12 == 0.3
        assert mat.nu == 0.3  # Property alias should also work
        
    def test_g_alias_for_g12(self):
        """Test that 'g' is aliased to 'g12'."""
        mat = CauchyContinuumModel(name='Material', isotropy=1, 
                                   e1=100e9, e2=100e9, e3=100e9,
                                   g=38.5e9, g13=38.5e9, g23=38.5e9,
                                   nu12=0.3, nu13=0.3, nu23=0.3)
        
        assert mat.g12 == 38.5e9
        
    def test_canonical_name_takes_precedence(self):
        """Test that canonical name takes precedence over alias."""
        mat = CauchyContinuumModel(name='Test', isotropy=0, 
                                   e=100e9, e1=200e9,  # Both provided
                                   nu=0.2, nu12=0.3)    # Both provided
        
        # Canonical names should win
        assert mat.e1 == 200e9
        assert mat.nu12 == 0.3
        
    def test_aliases_build_stiffness_matrix(self):
        """Test that aliases work for auto-building stiffness matrix."""
        mat = CauchyContinuumModel(name='Aluminum', isotropy=0, e=70e9, nu=0.33)
        
        assert mat.stff is not None
        assert len(mat.stff) == 6
        assert mat.stff[0][0] > 0  # Should have computed values
        
    def test_mixed_aliases_and_canonical(self):
        """Test mixing aliases and canonical names."""
        mat = CauchyContinuumModel(name='Composite', isotropy=1,
                                   e=150e9,      # Alias for e1
                                   e2=10e9,      # Canonical
                                   e3=10e9,      # Canonical
                                   g=5e9,        # Alias for g12
                                   g13=5e9,      # Canonical
                                   g23=3e9,      # Canonical
                                   nu=0.3,       # Alias for nu12
                                   nu13=0.3,     # Canonical
                                   nu23=0.4)     # Canonical
        
        assert mat.e1 == 150e9
        assert mat.e2 == 10e9
        assert mat.g12 == 5e9
        assert mat.nu12 == 0.3
        assert mat.stff is not None
