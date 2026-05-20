"""Load different types of Cauchy continuum materials from JSON files.

This example demonstrates how to load materials with different symmetries:
- Isotropic
- Transverse Isotropic  
- Orthotropic
- Anisotropic

Each material type is loaded from a separate JSON file and their properties
are displayed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from sgio.model.solid import CauchyContinuumModel


def load_material(json_path: Path) -> CauchyContinuumModel:
    """Load a CauchyContinuumModel from a JSON file.
    
    Parameters
    ----------
    json_path : Path
        Path to the JSON file containing material definition
        
    Returns
    -------
    CauchyContinuumModel
        Instantiated material model
    """
    payload = json.loads(json_path.read_text())
    return CauchyContinuumModel(**payload)


def display_material_info(material: CauchyContinuumModel) -> None:
    """Display key information about a material.
    
    Parameters
    ----------
    material : CauchyContinuumModel
        Material to display
    """
    isotropy_names = {
        0: "Isotropic",
        1: "Orthotropic", 
        2: "Anisotropic",
        3: "Transverse Isotropic"
    }
    
    print(f"\n{'='*70}")
    print(f"Material: {material.name}")
    print(f"Symmetry: {isotropy_names.get(material.isotropy, 'Unknown')}")
    print(f"{'='*70}")
    
    print(f"\nPhysical Properties:")
    print(f"  Density: {material.density:.1f} kg/m³")
    print(f"  Temperature: {material.temperature:.1f} °C")
    print(f"  Specific Heat: {material.specific_heat:.1f} J/(kg·K)")
    
    # Display elastic constants based on material type
    if material.isotropy == 0:
        # Isotropic
        print(f"\nElastic Constants (Isotropic):")
        print(f"  E   = {material.e1/1e9:.2f} GPa")
        print(f"  nu  = {material.nu12:.3f}")
        if material.stff:
            print(f"\nStiffness Matrix Components:")
            print(f"  C11 = {material.stff[0][0]/1e9:.2f} GPa")
            print(f"  C12 = {material.stff[0][1]/1e9:.2f} GPa")
            print(f"  C44 = {material.stff[3][3]/1e9:.2f} GPa")
            
    elif material.isotropy == 3:
        # Transverse Isotropic
        print(f"\nElastic Constants (Transverse Isotropic):")
        print(f"  E1  = {material.e1/1e9:.2f} GPa  (longitudinal)")
        print(f"  E2  = {material.e2/1e9:.2f} GPa  (transverse)")
        print(f"  G12 = {material.g12/1e9:.2f} GPa")
        print(f"  nu12 = {material.nu12:.3f}")
        print(f"  nu23 = {material.nu23:.3f}")
        if material.stff:
            print(f"\nKey Stiffness Components:")
            print(f"  C11 = {material.stff[0][0]/1e9:.2f} GPa")
            print(f"  C22 = {material.stff[1][1]/1e9:.2f} GPa")
            print(f"  C12 = {material.stff[0][1]/1e9:.2f} GPa")
            
    elif material.isotropy == 1:
        # Orthotropic
        print(f"\nElastic Constants (Orthotropic):")
        print(f"  E1  = {material.e1/1e9:.2f} GPa")
        print(f"  E2  = {material.e2/1e9:.2f} GPa")
        print(f"  E3  = {material.e3/1e9:.2f} GPa")
        print(f"  G12 = {material.g12/1e9:.2f} GPa")
        print(f"  G13 = {material.g13/1e9:.2f} GPa")
        print(f"  G23 = {material.g23/1e9:.2f} GPa")
        print(f"  nu12 = {material.nu12:.3f}")
        print(f"  nu13 = {material.nu13:.3f}")
        print(f"  nu23 = {material.nu23:.3f}")
        if material.stff:
            print(f"\nKey Stiffness Components:")
            print(f"  C11 = {material.stff[0][0]/1e9:.2f} GPa")
            print(f"  C22 = {material.stff[1][1]/1e9:.2f} GPa")
            print(f"  C33 = {material.stff[2][2]/1e9:.2f} GPa")
            
    elif material.isotropy == 2:
        # Anisotropic
        print(f"\nElastic Constants (Anisotropic):")
        print(f"  Defined by 21 independent constants")
        if material.stff:
            print(f"\nDiagonal Stiffness Components:")
            for i in range(6):
                comp_names = ['C11', 'C22', 'C33', 'C44', 'C55', 'C66']
                print(f"  {comp_names[i]} = {material.stff[i][i]/1e9:.2f} GPa")
            print(f"\nSelected Off-Diagonal Components:")
            print(f"  C12 = {material.stff[0][1]/1e9:.2f} GPa")
            print(f"  C13 = {material.stff[0][2]/1e9:.2f} GPa")
            print(f"  C23 = {material.stff[1][2]/1e9:.2f} GPa")
    
    # Display strength properties
    print(f"\nStrength Properties:")
    print(f"  Tensile:     X1t={material.x1t/1e6:.1f} MPa, "
          f"X2t={material.x2t/1e6:.1f} MPa, X3t={material.x3t/1e6:.1f} MPa")
    print(f"  Compressive: X1c={material.x1c/1e6:.1f} MPa, "
          f"X2c={material.x2c/1e6:.1f} MPa, X3c={material.x3c/1e6:.1f} MPa")
    print(f"  Shear:       X12={material.x12/1e6:.1f} MPa, "
          f"X13={material.x13/1e6:.1f} MPa, X23={material.x23/1e6:.1f} MPa")
    
    # Display thermal properties
    if material.cte:
        print(f"\nThermal Expansion Coefficients (1/K):")
        cte_labels = ['a11', 'a22', 'a33', 'a23', 'a13', 'a12']
        for i, (label, value) in enumerate(zip(cte_labels, material.cte)):
            if abs(value) > 1e-10:  # Only show non-zero values
                print(f"  {label} = {value:.2e}")


def compare_materials(materials: Dict[str, CauchyContinuumModel]) -> None:
    """Compare key properties across different material types.
    
    Parameters
    ----------
    materials : Dict[str, CauchyContinuumModel]
        Dictionary of materials to compare
    """
    print(f"\n{'='*70}")
    print("MATERIAL COMPARISON")
    print(f"{'='*70}")
    
    print(f"\n{'Material':<30} {'Symmetry':<20} {'Density':<15} {'C11 (GPa)':<10}")
    print("-" * 70)
    
    isotropy_names = {
        0: "Isotropic",
        1: "Orthotropic",
        2: "Anisotropic",
        3: "Transverse Isotropic"
    }
    
    for name, mat in materials.items():
        symmetry = isotropy_names.get(mat.isotropy, "Unknown")
        density = f"{mat.density:.0f} kg/m³"
        c11 = f"{mat.stff[0][0]/1e9:.2f}" if mat.stff else "N/A"
        print(f"{mat.name:<30} {symmetry:<20} {density:<15} {c11:<10}")


def export_to_json(material: CauchyContinuumModel, output_path: Path) -> None:
    """Export a material to a JSON file.
    
    Parameters
    ----------
    material : CauchyContinuumModel
        Material to export
    output_path : Path
        Path for the output JSON file
    """
    json_data = material.model_dump_json(indent=2)
    output_path.write_text(json_data)
    print(f"\nExported {material.name} to: {output_path}")


def main() -> None:
    """Main function to demonstrate loading different material types."""
    
    # Get the directory containing this script
    example_dir = Path(__file__).resolve().parent
    
    # Define material files
    material_files = {
        'isotropic': 'isotropic_steel.json',
        'transverse': 'transverse_isotropic_fiber.json',
        'orthotropic': 'orthotropic_composite.json',
        'anisotropic': 'anisotropic_crystal.json'
    }
    
    # Load all materials
    materials: Dict[str, CauchyContinuumModel] = {}
    
    print("Loading materials from JSON files...")
    print("=" * 70)
    
    for key, filename in material_files.items():
        filepath = example_dir / filename
        if filepath.exists():
            try:
                materials[key] = load_material(filepath)
                print(f"[OK] Loaded {key}: {filepath.name}")
            except Exception as e:
                print(f"[ERROR] Failed to load {key}: {e}")
        else:
            print(f"[ERROR] File not found: {filename}")
    
    # Display detailed information for each material
    for key, material in materials.items():
        display_material_info(material)
    
    # Compare materials
    if materials:
        compare_materials(materials)
    
    # Demonstrate JSON export
    print(f"\n{'='*70}")
    print("JSON SERIALIZATION EXAMPLE")
    print(f"{'='*70}")
    
    if 'transverse' in materials:
        mat = materials['transverse']
        print(f"\nSerializing {mat.name} to JSON:")
        print("\n" + mat.model_dump_json(indent=2)[:500] + "\n...")
        
        # Optionally export to file
        # output_file = example_dir / 'exported_material.json'
        # export_to_json(mat, output_file)
    
    print(f"\n{'='*70}")
    print("ALL MATERIALS LOADED SUCCESSFULLY!")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
