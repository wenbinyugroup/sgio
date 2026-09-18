(guide_model_sd_cauchy)=
# Cauchy Continuum Model

`sgio.model.solid.CauchyContinuumModel` is the solid material model: three
displacements ({math}`u_1`, {math}`u_2`, {math}`u_3`) and six strain components
({math}`\varepsilon_{11}`, {math}`\varepsilon_{22}`, {math}`\varepsilon_{33}`,
{math}`\varepsilon_{23}`, {math}`\varepsilon_{13}`, {math}`\varepsilon_{12}`).

It supports isotropic, orthotropic, and fully anisotropic materials, validates
on construction and assignment, and serializes through Pydantic's
{py:meth}`model_dump` / {py:meth}`model_dump_json`.

## Create a Material

The constructor takes engineering constants as keyword arguments; validators
enforce units and admissible ranges.

```python
from sgio.model.solid import CauchyContinuumModel

carbon_ud = CauchyContinuumModel(
    name='UD Carbon/Epoxy',
    isotropy=1,
    density=1570.0,
    e1=138e9, e2=9e9, e3=9e9,
    g12=5.2e9, g13=5.2e9, g23=3.5e9,
    nu12=0.32, nu13=0.32, nu23=0.45,
    cte=[2.5e-6, 2.5e-6, 2.4e-5, 0.0, 0.0, 0.0],
)
```

## Query and Update

Typed setters and queries are the supported path:

```python
from sgio.model import ElasticInputType, MatrixKind, TensorComponent

carbon_ud.set_isotropy('orthotropic')
carbon_ud.set_elastic([210e9, 0.29], input_type=ElasticInputType.ISOTROPIC)

c11 = carbon_ud.get_matrix_component(MatrixKind.STIFFNESS, TensorComponent(1, 1))
```

`set_strength_constants()` sets the strength values, and
`get_thermal_expansion()` reads the CTE components.

## Load from JSON

Because the model is a Pydantic model, a JSON document maps onto it directly —
whether it comes from a file, a database, or an API response:

```python
import json
from pathlib import Path

material = CauchyContinuumModel(**json.loads(Path('material.json').read_text()))
```

See {doc}`/examples/load_cauchy_material_from_json`.
