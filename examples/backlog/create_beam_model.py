"""Example: Create and Validate Beam Models

This example demonstrates how to create structural models programmatically
using the Pydantic-based model classes.

Based on test patterns from tests/unit/test_models.py
"""
import sgio
from sgio.model.beam import EulerBernoulliBeamModel, TimoshenkoBeamModel

print("=" * 70)
print("Creating Structural Models")
print("=" * 70)

# Example 1: Create Euler-Bernoulli Beam Model (BM1)
print("\n[Example 1] Euler-Bernoulli Beam Model (Classical Beam Theory)")
print("-" * 70)

# Create with default values
beam_default = EulerBernoulliBeamModel()
print(f"Default model:")
print(f"  Name: {beam_default.name}")
print(f"  Label: {beam_default.label}")
print(f"  Model: {beam_default.model_name}")
print(f"  Dimension: {beam_default.dim}")

# Create with specific parameters
beam_custom = EulerBernoulliBeamModel(
    name="Composite Wing Spar",
    id=1,
    mu=2.5,           # Mass per unit length (kg/m)
    ea=1.5e8,         # Axial stiffness (N)
    gj=5.0e6,         # Torsional stiffness (N·m²)
    ei22=3.0e6,       # Bending stiffness about axis 2 (N·m²)
    ei33=8.0e6,       # Bending stiffness about axis 3 (N·m²)
)

print(f"\nCustom model:")
print(f"  Name: {beam_custom.name}")
print(f"  ID: {beam_custom.id}")
print(f"  μ (mass/length): {beam_custom.mu:.2f} kg/m")
print(f"  EA (axial stiffness): {beam_custom.ea:.2e} N")
print(f"  GJ (torsional stiffness): {beam_custom.gj:.2e} N·m²")
print(f"  EI₂₂ (bending stiffness): {beam_custom.ei22:.2e} N·m²")
print(f"  EI₃₃ (bending stiffness): {beam_custom.ei33:.2e} N·m²")

# Example 2: Create Timoshenko Beam Model (BM2)
print("\n[Example 2] Timoshenko Beam Model (Includes Shear Deformation)")
print("-" * 70)

timoshenko_beam = TimoshenkoBeamModel(
    name="Helicopter Rotor Blade",
    id=2,
    mu=3.2,           # Mass per unit length (kg/m)
    ea=2.0e8,         # Axial stiffness (N)
    gj=6.5e6,         # Torsional stiffness (N·m²)
    ei22=4.5e6,       # Bending stiffness about axis 2 (N·m²)
    ei33=1.2e7,       # Bending stiffness about axis 3 (N·m²)
    ga22=8.0e6,       # Shear stiffness in direction 2 (N)
    ga33=8.0e6,       # Shear stiffness in direction 3 (N)
)

print(f"Timoshenko model:")
print(f"  Name: {timoshenko_beam.name}")
print(f"  ID: {timoshenko_beam.id}")
print(f"  Label: {timoshenko_beam.label}")
print(f"  Model: {timoshenko_beam.model_name}")
print(f"\nStiffness properties:")
print(f"  EA: {timoshenko_beam.ea:.2e} N")
print(f"  GJ: {timoshenko_beam.gj:.2e} N·m²")
print(f"  EI₂₂: {timoshenko_beam.ei22:.2e} N·m²")
print(f"  EI₃₃: {timoshenko_beam.ei33:.2e} N·m²")
print(f"  GA₂₂: {timoshenko_beam.ga22:.2e} N (shear)")
print(f"  GA₃₃: {timoshenko_beam.ga33:.2e} N (shear)")

# Example 3: Model Validation
print("\n[Example 3] Model Validation")
print("-" * 70)

try:
    # This will succeed - valid model
    valid_model = EulerBernoulliBeamModel(
        name="Valid Beam",
        ea=1e8,
        ei22=1e6,
    )
    print("✓ Valid model created successfully")
    
except Exception as e:
    print(f"✗ Validation error: {e}")

# Example 4: Accessing Model Properties
print("\n[Example 4] Accessing Model Properties")
print("-" * 70)

# Use the .get() method to safely access properties
ea_value = beam_custom.get('ea')
gj_value = beam_custom.get('gj')
nonexistent = beam_custom.get('nonexistent_property', default=0.0)

print(f"EA value: {ea_value}")
print(f"GJ value: {gj_value}")
print(f"Nonexistent property (with default): {nonexistent}")

# Example 5: Model Comparison
print("\n[Example 5] Comparing Models")
print("-" * 70)

print(f"Euler-Bernoulli model dimension: {beam_custom.dim}")
print(f"Timoshenko model dimension: {timoshenko_beam.dim}")
print(f"Both are 1D beam models: {beam_custom.dim == timoshenko_beam.dim}")
print(f"\nEuler-Bernoulli label: {beam_custom.label}")
print(f"Timoshenko label: {timoshenko_beam.label}")
print(f"Different model types: {beam_custom.label != timoshenko_beam.label}")

print("\n" + "=" * 70)
print("Model Creation Complete")
print("=" * 70)
print("\nKey Takeaways:")
print("  • BM1 (Euler-Bernoulli): Classical beam theory, no shear deformation")
print("  • BM2 (Timoshenko): Includes shear deformation effects")
print("  • Models use Pydantic for validation and type checking")
print("  • Use .get() method for safe property access")
print("=" * 70)

