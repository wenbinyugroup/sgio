"""
Example usage of parameter aliases in CauchyContinuumModel.

This example demonstrates how to use convenient aliases for material parameters,
making it easier and more intuitive to define isotropic materials.
"""

from sgio.model.solid import CauchyContinuumModel


def example_isotropic_with_aliases():
    """Example: Using aliases for isotropic materials."""
    print("=" * 70)
    print("ISOTROPIC MATERIAL WITH ALIASES")
    print("=" * 70)
    
    # Using convenient aliases 'e' and 'nu' instead of 'e1' and 'nu12'
    steel = CauchyContinuumModel(
        name='Steel (using aliases)',
        isotropy=0,
        e=200e9,     # Alias for e1
        nu=0.3,      # Alias for nu12
        density=7850
    )
    
    print(f"\nMaterial: {steel.name}")
    print(f"Young's modulus (E): {steel.e/1e9:.1f} GPa")
    print(f"Poisson's ratio (nu): {steel.nu:.3f}")
    print(f"Stiffness matrix C11: {steel.stff[0][0]/1e9:.2f} GPa")
    
    # Compare with canonical parameter names
    aluminum = CauchyContinuumModel(
        name='Aluminum (canonical names)',
        isotropy=0,
        e1=70e9,     # Canonical name
        nu12=0.33,   # Canonical name
        density=2700
    )
    
    print(f"\nMaterial: {aluminum.name}")
    print(f"Young's modulus (E): {aluminum.e1/1e9:.1f} GPa")
    print(f"Poisson's ratio (nu): {aluminum.nu12:.3f}")
    print(f"Stiffness matrix C11: {aluminum.stff[0][0]/1e9:.2f} GPa")
    
    print("\nBoth methods produce the same result!")


def example_shear_modulus_alias():
    """Example: Using 'g' alias for shear modulus."""
    print("\n" + "=" * 70)
    print("SHEAR MODULUS ALIAS")
    print("=" * 70)
    
    # Using 'g' as an alias for 'g12'
    composite = CauchyContinuumModel(
        name='Composite with g alias',
        isotropy=1,
        e1=150e9,
        e2=10e9,
        e3=10e9,
        g=5e9,       # Alias for g12
        g13=5e9,
        g23=3e9,
        nu12=0.3,
        nu13=0.3,
        nu23=0.4,
        density=1600
    )
    
    print(f"\nMaterial: {composite.name}")
    print(f"G12 (set via 'g' alias): {composite.g12/1e9:.1f} GPa")
    print(f"G13: {composite.g13/1e9:.1f} GPa")
    print(f"G23: {composite.g23/1e9:.1f} GPa")


def example_mixed_usage():
    """Example: Mixing aliases and canonical names."""
    print("\n" + "=" * 70)
    print("MIXING ALIASES AND CANONICAL NAMES")
    print("=" * 70)
    
    # You can mix aliases and canonical names
    material = CauchyContinuumModel(
        name='Mixed naming',
        isotropy=1,
        e=100e9,      # Alias for e1
        e2=90e9,      # Canonical name
        e3=80e9,      # Canonical name
        g=35e9,       # Alias for g12
        g13=33e9,     # Canonical name
        g23=30e9,     # Canonical name
        nu=0.25,      # Alias for nu12
        nu13=0.28,    # Canonical name
        nu23=0.3,     # Canonical name
        density=1800
    )
    
    print(f"\nMaterial: {material.name}")
    print(f"E1 (set via 'e'): {material.e1/1e9:.1f} GPa")
    print(f"E2: {material.e2/1e9:.1f} GPa")
    print(f"E3: {material.e3/1e9:.1f} GPa")
    print(f"G12 (set via 'g'): {material.g12/1e9:.1f} GPa")
    print(f"G13: {material.g13/1e9:.1f} GPa")
    print(f"G23: {material.g23/1e9:.1f} GPa")
    print(f"nu12 (set via 'nu'): {material.nu12:.3f}")
    print(f"nu13: {material.nu13:.3f}")
    print(f"nu23: {material.nu23:.3f}")


def example_canonical_precedence():
    """Example: Canonical names take precedence over aliases."""
    print("\n" + "=" * 70)
    print("CANONICAL NAME PRECEDENCE")
    print("=" * 70)
    
    # If both alias and canonical name are provided, canonical takes precedence
    material = CauchyContinuumModel(
        name='Precedence test',
        isotropy=0,
        e=100e9,     # Alias
        e1=200e9,    # Canonical - this value will be used
        nu=0.2,      # Alias
        nu12=0.3,    # Canonical - this value will be used
        density=5000
    )
    
    print(f"\nWhen both 'e' (100 GPa) and 'e1' (200 GPa) are provided:")
    print(f"  Actual E value: {material.e1/1e9:.1f} GPa (canonical wins)")
    
    print(f"\nWhen both 'nu' (0.2) and 'nu12' (0.3) are provided:")
    print(f"  Actual nu value: {material.nu12:.1f} (canonical wins)")


def example_property_aliases():
    """Example: Using property aliases for getting values."""
    print("\n" + "=" * 70)
    print("PROPERTY ALIASES FOR READING VALUES")
    print("=" * 70)
    
    material = CauchyContinuumModel(
        name='Titanium',
        isotropy=0,
        e1=116e9,
        nu12=0.32,
        density=4500
    )
    
    print(f"\nMaterial: {material.name}")
    print("\nReading values using different methods:")
    print(f"  material.e1:   {material.e1/1e9:.1f} GPa")
    print(f"  material.e:    {material.e/1e9:.1f} GPa (property alias)")
    print(f"  material.get('e'): {material.get('e')/1e9:.1f} GPa (legacy method)")
    
    print(f"\n  material.nu12: {material.nu12:.3f}")
    print(f"  material.nu:   {material.nu:.3f} (property alias)")
    print(f"  material.get('nu'): {material.get('nu'):.3f} (legacy method)")
    
    print("\nAll three methods return the same value!")


def example_json_with_aliases():
    """Example: JSON compatibility with aliases."""
    print("\n" + "=" * 70)
    print("JSON COMPATIBILITY")
    print("=" * 70)
    
    # Create material using aliases
    mat1 = CauchyContinuumModel(
        name='Material via aliases',
        isotropy=0,
        e=150e9,
        nu=0.28,
        density=3000
    )
    
    # Export to JSON
    json_str = mat1.model_dump_json(indent=2)
    print("\nJSON representation (created with aliases):")
    print(json_str[:300] + "...")
    
    # JSON will use canonical names (e1, nu12)
    print("\nNote: JSON uses canonical names 'e1' and 'nu12', not aliases")
    
    # When loading from JSON, canonical names are used
    import json
    json_dict = json.loads(json_str)
    print(f"\nJSON keys: e1={json_dict.get('e1')}, nu12={json_dict.get('nu12')}")
    print(f"Aliases 'e' and 'nu' are not in JSON: e={json_dict.get('e')}, nu={json_dict.get('nu')}")


def example_comparison():
    """Compare different ways to create the same material."""
    print("\n" + "=" * 70)
    print("COMPARISON: ALIASES VS CANONICAL NAMES")
    print("=" * 70)
    
    # Method 1: Using aliases
    mat1 = CauchyContinuumModel(
        name='Steel',
        isotropy=0,
        e=200e9,
        nu=0.3,
        density=7850
    )
    
    # Method 2: Using canonical names
    mat2 = CauchyContinuumModel(
        name='Steel',
        isotropy=0,
        e1=200e9,
        nu12=0.3,
        density=7850
    )
    
    print("\nMethod 1 (aliases):     e=200e9, nu=0.3")
    print("Method 2 (canonical):   e1=200e9, nu12=0.3")
    
    print(f"\nBoth produce identical materials:")
    print(f"  mat1.e1 == mat2.e1: {mat1.e1 == mat2.e1}")
    print(f"  mat1.nu12 == mat2.nu12: {mat1.nu12 == mat2.nu12}")
    print(f"  mat1.stff[0][0] == mat2.stff[0][0]: {abs(mat1.stff[0][0] - mat2.stff[0][0]) < 1e-6}")
    
    print("\nUse whichever naming convention you prefer!")


if __name__ == '__main__':
    # Run all examples
    example_isotropic_with_aliases()
    example_shear_modulus_alias()
    example_mixed_usage()
    example_canonical_precedence()
    example_property_aliases()
    example_json_with_aliases()
    example_comparison()
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print("\nSummary of Available Aliases:")
    print("  e   -> e1   (Young's modulus)")
    print("  nu  -> nu12 (Poisson's ratio)")
    print("  g   -> g12  (Shear modulus)")
    print("=" * 70)
