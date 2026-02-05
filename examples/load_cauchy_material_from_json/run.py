"""Load a Cauchy continuum material definition from JSON."""

from __future__ import annotations

import json
from pathlib import Path

from sgio.model.solid import CauchyContinuumModel


def load_material(json_path: Path) -> CauchyContinuumModel:
    """Return a `CauchyContinuumModel` instantiated from a JSON payload."""

    payload = json.loads(json_path.read_text())
    return CauchyContinuumModel(**payload)


def main() -> None:
    repo_examples_dir = Path(__file__).resolve().parent
    material = load_material(repo_examples_dir / 'material.json')

    print('Loaded material:')
    print(material)

    print('\nSelected engineering constants:')
    print(f"E1 = {material.e1:.2e} Pa")
    print(f"G12 = {material.g12:.2e} Pa")
    print(f"nu12 = {material.nu12:.3f}")

    print('\nJSON serialization (pretty printed):')
    print(material.model_dump_json(indent=2))


if __name__ == '__main__':
    main()
