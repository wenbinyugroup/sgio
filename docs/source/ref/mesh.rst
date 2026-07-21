.. _ref_mesh:

Mesh Utilities
==============

Mesh Class
----------

.. currentmodule:: sgio

.. autosummary::
   :toctree: _temp

   SGMesh


Node and Element Numbering
---------------------------

The numbering module provides validation and utilities for node and element numbering.

Validation Functions
~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: sgio

.. autosummary::
   :toctree: _temp

   validate_node_ids
   validate_element_ids


Utility Functions
~~~~~~~~~~~~~~~~~

.. currentmodule:: sgio

.. autosummary::
   :toctree: _temp

   get_node_id_mapping
   ensure_node_ids
   ensure_element_ids
   check_duplicate_ids
   check_forbidden_ids
   renumber_elements
   auto_renumber_for_format


Format Numbering Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each target format declares its node/element numbering constraints. The writers
consult this registry and adjust numbering automatically, so explicit
renumbering is normally unnecessary.

.. currentmodule:: sgio

.. autosummary::
   :toctree: _temp

   FormatNumberingRequirements
   normalize_format_name
   get_numbering_requirements

Two module-level tables back these functions:

``sgio.FORMAT_ALIASES``
   Maps format aliases to their canonical name (for example ``'sc'`` to
   ``'swiftcomp'``). :func:`normalize_format_name` applies this mapping.

``sgio.FORMAT_REQUIREMENTS``
   Maps each canonical format name to its
   :class:`FormatNumberingRequirements`. :func:`get_numbering_requirements`
   looks up this table, resolving aliases first.


Mesh Validation Functions
--------------------------

.. currentmodule:: sgio.core.mesh

.. autosummary::
   :toctree: _temp

   check_cell_ordering
   fix_cell_ordering
   check_isolated_nodes
