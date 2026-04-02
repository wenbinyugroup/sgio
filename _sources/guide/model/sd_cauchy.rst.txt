.. _guide_model_sd_cauchy:

Cauchy Continuum Model
======================

The solid material model in SGIO is implemented by
``sgio.model.CauchyContinuumModel``. The legacy dataclass-based
``CauchyContinuumModel`` has been removed; the Pydantic implementation that
was previously exposed as ``CauchyContinuumModelNew`` now owns the canonical
name. A temporary import alias ``CauchyContinuumModelNew`` is still provided to
ease migration, but it will be deprecated in a future release.

The model captures the standard Cauchy continuum kinematics with three
displacements (:math:`u_1`, :math:`u_2`, :math:`u_3`) and six strain
components (:math:`\varepsilon_{11}`, :math:`\varepsilon_{22}`,
:math:`\varepsilon_{33}`, :math:`\varepsilon_{23}`, :math:`\varepsilon_{13}`,
:math:`\varepsilon_{12}`).

Key Features
------------

* Pydantic validation on construction and assignment (`validate_assignment=True`)
* Explicit support for isotropic, orthotropic, and fully anisotropic materials
* Backward-compatible ``get``/``set`` helpers mirroring the legacy API
* First-class JSON serialization via :py:meth:`model_dump` and
  :py:meth:`model_dump_json`

Creating a Material
-------------------

The constructor accepts keyword arguments for all engineering constants. Pydantic
validators enforce units and admissible ranges (e.g., Poisson ratios).

.. code-block:: python

   from sgio.model.solid import CauchyContinuumModel

   carbon_ud = CauchyContinuumModel(
       name="UD Carbon/Epoxy",
       isotropy=1,
       density=1570.0,
       e1=138e9,
       e2=9e9,
       e3=9e9,
       g12=5.2e9,
       g13=5.2e9,
       g23=3.5e9,
       nu12=0.32,
       nu13=0.32,
       nu23=0.45,
       strength_constants=[
           1500.0, 1200.0, 800.0,
           900.0, 700.0, 600.0,
           120.0, 110.0, 95.0,
       ],
       cte=[2.5e-6, 2.5e-6, 2.4e-5, 0.0, 0.0, 0.0],
   )

Legacy setter helpers remain available and run through the same validators:

.. code-block:: python

   carbon_ud.set('isotropy', 'orthotropic')
   carbon_ud.set('elastic', [210e9, 0.29])  # switches to isotropic input

Loading from JSON
-----------------

The example at ``examples/load_cauchy_material_from_json/`` demonstrates a
complete JSON round-trip. The core logic is straightforward:

.. code-block:: python

   import json
   from pathlib import Path

   from sgio.model.solid import CauchyContinuumModel

   payload = json.loads(Path('material.json').read_text())
   material = CauchyContinuumModel(**payload)
   print(material.model_dump_json(indent=2))

This pattern works equally well when the JSON document comes from a database or
an API response, making it easy to integrate SGIO materials into external
pipelines.
