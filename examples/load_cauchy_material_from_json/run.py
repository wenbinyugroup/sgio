"""Load a Cauchy continuum material definition from JSON."""

from __future__ import annotations

from pathlib import Path

from sgio.iofunc.common.material_json import read_material_from_json, write_material_to_json
from sgio.model.solid import CauchyContinuumModel


def load_material(json_path: Path) -> CauchyContinuumModel:
    """Return a `CauchyContinuumModel` instantiated from one standard JSON record."""

    materials = read_material_from_json(str(json_path))
    return next(iter(materials.values()))


def main() -> None:
    repo_examples_dir = Path(__file__).resolve().parent
    material = load_material(repo_examples_dir / 'sections.json')

    print('Loaded material:')
    print(material)

    print('\nSelected engineering constants:')
    print(f"E1 = {material.e1:.2e} Pa")
    print(f"G12 = {material.g12:.2e} Pa")
    print(f"nu12 = {material.nu12:.3f}")

    print('\nJSON serialization (pretty printed):')
    output_path = repo_examples_dir / 'material_out.json'
    write_material_to_json(material, str(output_path), indent=2)
    print(output_path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
