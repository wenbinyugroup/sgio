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
   ensure_element_ids
   check_duplicate_ids
   check_forbidden_ids


Mesh Validation Functions
--------------------------

.. currentmodule:: sgio.core.mesh

.. autosummary::
   :toctree: _temp

   check_cell_ordering
   fix_cell_ordering
   check_isolated_nodes
   renumber_elements
