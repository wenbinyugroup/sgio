"""
Example usage of CauchyContinuumModel with different material symmetries.

This example demonstrates how to initialize materials with different 
symmetry types: isotropic, transverse isotropic, orthotropic, and anisotropic.
"""

from sgio.model.solid import CauchyContinuumModel
import numpy as np


def example_isotropic():
    """Example: Isotropic material (e.g., steel, aluminum)."""
    print("=" * 60)
    print("ISOTROPIC MATERIAL EXAMPLE")
    print("=" * 60)
    
    # Method 1: Direct initialization with e and nu
    steel = CauchyContinuumModel(
        name='Steel',
        isotropy=0,  # 0 = isotropic
        e1=200e9,    # Young's modulus (Pa)
        nu12=0.3,    # Poisson's ratio
        density=7850  # kg/m^3
    )
    
    print(f"\nMaterial: {steel.name}")
    print(f"E = {steel.e1/1e9:.1f} GPa")
    print(f"nu = {steel.nu12}")
    print(f"Stiffness matrix C11 = {steel.stff[0][0]/1e9:.2f} GPa")
    print(f"Stiffness matrix C12 = {steel.stff[0][1]/1e9:.2f} GPa")
    print(f"Stiffness matrix C44 = {steel.stff[3][3]/1e9:.2f} GPa")
    
    # Method 2: Using setElastic
    aluminum = CauchyContinuumModel(name='Aluminum', isotropy=0)
    aluminum.setElastic([70e9, 0.33])
    print(f"\n{aluminum.name}: E = {aluminum.e1/1e9:.1f} GPa, nu = {aluminum.nu12}")


def example_transverse_isotropic():
    """Example: Transverse isotropic material (e.g., unidirectional fiber)."""
    print("\n" + "=" * 60)
    print("TRANSVERSE ISOTROPIC MATERIAL EXAMPLE")
    print("=" * 60)
    
    # Unidirectional carbon fiber composite
    fiber = CauchyContinuumModel(
        name='UD Carbon Fiber',
        isotropy=3,  # 3 = transverse isotropic
        e1=150e9,    # Longitudinal Young's modulus (Pa)
        e2=10e9,     # Transverse Young's modulus (Pa)
        g12=5e9,     # Longitudinal shear modulus (Pa)
        nu12=0.3,    # Longitudinal Poisson's ratio
        nu23=0.4,    # Transverse Poisson's ratio
        density=1600
    )
    
    print(f"\nMaterial: {fiber.name}")
    print(f"E1 (longitudinal) = {fiber.e1/1e9:.1f} GPa")
    print(f"E2 (transverse)   = {fiber.e2/1e9:.1f} GPa")
    print(f"E3 (transverse)   = {fiber.e3/1e9:.1f} GPa (auto-set = E2)")
    print(f"G12 = {fiber.g12/1e9:.1f} GPa")
    print(f"nu12 = {fiber.nu12}")
    print(f"nu23 = {fiber.nu23}")
    print(f"Stiffness matrix C11 = {fiber.stff[0][0]/1e9:.2f} GPa")
    print(f"Stiffness matrix C22 = {fiber.stff[1][1]/1e9:.2f} GPa")


def example_orthotropic():
    """Example: Orthotropic material (e.g., woven composite, wood)."""
    print("\n" + "=" * 60)
    print("ORTHOTROPIC MATERIAL EXAMPLE")
    print("=" * 60)
    
    # Method 1: Full initialization with 9 engineering constants
    composite = CauchyContinuumModel(
        name='Woven Composite',
        isotropy=1,  # 1 = orthotropic
        e1=60e9,     # Pa
        e2=58e9,     # Pa
        e3=10e9,     # Pa
        g12=4.5e9,   # Pa
        g13=4e9,     # Pa
        g23=3.5e9,   # Pa
        nu12=0.05,
        nu13=0.3,
        nu23=0.3,
        density=1500
    )
    
    print(f"\nMaterial: {composite.name}")
    print(f"E1 = {composite.e1/1e9:.1f} GPa")
    print(f"E2 = {composite.e2/1e9:.1f} GPa")
    print(f"E3 = {composite.e3/1e9:.1f} GPa")
    print(f"Stiffness matrix shape: {len(composite.stff)}x{len(composite.stff[0])}")
    
    # Method 2: Using setElastic with 'lamina' input (4 constants)
    # This assumes plane stress state
    lamina = CauchyContinuumModel(name='Lamina', isotropy=1)
    lamina.setElastic([150e9, 10e9, 5e9, 0.3], input_type='lamina')
    print(f"\n{lamina.name}: E1={lamina.e1/1e9:.0f} GPa, E2={lamina.e2/1e9:.0f} GPa")
    
    # Method 3: Using setElastic with 'engineering' input (9 constants)
    wood = CauchyContinuumModel(name='Wood', isotropy=1)
    wood.setElastic(
        [15e9, 1e9, 0.8e9, 1.2e9, 1e9, 0.08e9, 0.4, 0.45, 0.4],
        input_type='engineering'
    )
    print(f"{wood.name}: E1={wood.e1/1e9:.1f} GPa, E2={wood.e2/1e9:.1f} GPa, E3={wood.e3/1e9:.1f} GPa")


def example_anisotropic():
    """Example: Anisotropic material (e.g., triclinic crystal)."""
    print("\n" + "=" * 60)
    print("ANISOTROPIC MATERIAL EXAMPLE")
    print("=" * 60)
    
    # Method 1: Using 21 constants (upper triangle of stiffness matrix)
    # Order: C11, C12, C13, C14, C15, C16,
    #             C22, C23, C24, C25, C26,
    #                  C33, C34, C35, C36,
    #                       C44, C45, C46,
    #                            C55, C56,
    #                                 C66
    
    constants_21 = [
        # Row 0: C11, C12, C13, C14, C15, C16
        166e9, 64e9, 64e9, 0, 0, 0,
        # Row 1: C22, C23, C24, C25, C26
        166e9, 64e9, 0, 0, 0,
        # Row 2: C33, C34, C35, C36
        166e9, 0, 0, 0,
        # Row 3: C44, C45, C46
        79e9, 0, 0,
        # Row 4: C55, C56
        79e9, 0,
        # Row 5: C66
        79e9
    ]
    
    crystal = CauchyContinuumModel(
        name='Crystal (Cubic)',
        isotropy=2,  # 2 = anisotropic
        anisotropic_constants=constants_21,
        density=3500
    )
    
    print(f"\nMaterial: {crystal.name}")
    print(f"Number of independent constants: 21")
    print(f"Stiffness matrix C11 = {crystal.stff[0][0]/1e9:.1f} GPa")
    print(f"Stiffness matrix C12 = {crystal.stff[0][1]/1e9:.1f} GPa")
    print(f"Stiffness matrix C44 = {crystal.stff[3][3]/1e9:.1f} GPa")
    
    # Verify symmetry
    is_symmetric = True
    for i in range(6):
        for j in range(6):
            if abs(crystal.stff[i][j] - crystal.stff[j][i]) > 1e-6:
                is_symmetric = False
                break
    print(f"Stiffness matrix is symmetric: {is_symmetric}")
    
    # Method 2: Using setElastic with 21 constants
    monoclinic = CauchyContinuumModel(name='Monoclinic Crystal', isotropy=2)
    monoclinic.setElastic(constants_21, input_type='anisotropic')
    print(f"\n{monoclinic.name} initialized with 21 constants")
    
    # Method 3: Using full 6x6 stiffness matrix
    stiff_matrix = [
        [180e9, 60e9, 60e9, 0, 0, 0],
        [60e9, 180e9, 60e9, 0, 0, 0],
        [60e9, 60e9, 180e9, 0, 0, 0],
        [0, 0, 0, 60e9, 0, 0],
        [0, 0, 0, 0, 60e9, 0],
        [0, 0, 0, 0, 0, 60e9]
    ]
    
    custom = CauchyContinuumModel(name='Custom Material', isotropy=2)
    custom.setElastic(stiff_matrix, input_type='stiffness')
    print(f"{custom.name} initialized with full 6x6 matrix")


def example_comparison():
    """Compare different material types."""
    print("\n" + "=" * 60)
    print("MATERIAL COMPARISON")
    print("=" * 60)
    
    # Create materials with similar properties
    iso = CauchyContinuumModel(name='Isotropic', isotropy=0, e1=100e9, nu12=0.3)
    
    trans = CauchyContinuumModel(
        name='Transverse Iso',
        isotropy=3,
        e1=100e9, e2=100e9, g12=38.5e9, nu12=0.3, nu23=0.3
    )
    
    ortho = CauchyContinuumModel(
        name='Orthotropic',
        isotropy=1,
        e1=100e9, e2=100e9, e3=100e9,
        g12=38.5e9, g13=38.5e9, g23=38.5e9,
        nu12=0.3, nu13=0.3, nu23=0.3
    )
    
    print("\nComparison of C11 (first stiffness component):")
    print(f"  Isotropic:         {iso.stff[0][0]/1e9:.2f} GPa")
    print(f"  Transverse Iso:    {trans.stff[0][0]/1e9:.2f} GPa")
    print(f"  Orthotropic:       {ortho.stff[0][0]/1e9:.2f} GPa")
    
    print("\nNumber of independent elastic constants:")
    print(f"  Isotropic:         2 (E, nu)")
    print(f"  Transverse Iso:    5 (E1, E2, G12, nu12, nu23)")
    print(f"  Orthotropic:       9 (E1, E2, E3, G12, G13, G23, nu12, nu13, nu23)")
    print(f"  Anisotropic:       21 (upper triangle of C)")


if __name__ == '__main__':
    # Run all examples
    example_isotropic()
    example_transverse_isotropic()
    example_orthotropic()
    example_anisotropic()
    example_comparison()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
