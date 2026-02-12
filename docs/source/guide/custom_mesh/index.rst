.. _guide_custom_mesh:

Creating StructureGene from Custom Mesh Data
=============================================

This guide explains how to create a :class:`~sgio.StructureGene` object from your own mesh data when your format is not directly supported by sgio.

.. note::
   If you just want to get started quickly, skip to :ref:`custom_mesh_quickstart`.

Overview
--------

When you have mesh data from custom software or proprietary formats that you want to analyze with VABS or SwiftComp, you need to:

1. **Create a StructureGene object** with basic configuration (name, dimensions)
2. **Build the mesh** with nodes, elements, and connectivity
3. **Define materials** and their properties
4. **Assign materials to elements** using property IDs and mocombos
5. **Write to VABS/SwiftComp format**

What You Need
-------------

**Required Data:**
  * Nodal coordinates (x, y, z for each node)
  * Element connectivity (which nodes form each element)
  * Element types (triangle, quad, tetrahedron, etc.)
  * Material properties (elastic moduli, density, etc.)

**Optional Data:**
  * Original node/element IDs (to preserve your numbering)
  * Material orientations (for composites)
  * Node/element sets (for boundary conditions)

Guide Contents
--------------

..  toctree::
    :maxdepth: 1

    quickstart
    data_structures
    conversion_example
    troubleshooting

Quick Links
-----------

* **New to sgio?** Start with :ref:`custom_mesh_quickstart`
* **Need data structure details?** See :ref:`custom_mesh_data_structures`
* **Converting from existing format?** See :ref:`custom_mesh_conversion`
* **Having problems?** Check :ref:`custom_mesh_troubleshooting`

Key Concepts
------------

**StructureGene**
  The main container for your mesh and material data. Think of it as your complete finite element model ready for homogenization analysis.

**Mesh (using meshio format)**
  Contains nodes (points), elements (cells), and associated data. Uses 0-based indexing for connectivity.

**Materials**
  Stored by name in a dictionary. Can be isotropic, transversely isotropic, or orthotropic.

**Mocombos (Material-Orientation Combinations)**
  Maps property IDs to (material_name, orientation_angle) pairs. This allows using the same material at different angles.

**Property IDs**
  Integer IDs assigned to each element that reference a mocombo, which then references a material and orientation.

Workflow Diagram
----------------

.. code-block:: text

    Your Mesh Data
         |
         v
    Parse nodes, elements, materials
         |
         v
    Create StructureGene
         |
         +-- Set dimensions (sgdim, smdim)
         +-- Add materials to sg.materials{}
         +-- Create mocombos mapping
         +-- Build mesh with 0-based connectivity
         |
         v
    Write to VABS/SwiftComp
         |
         v
    Run homogenization analysis

Next Steps
----------

* **Quickstart**: :ref:`custom_mesh_quickstart` - Simple working example
* **Details**: :ref:`custom_mesh_data_structures` - Complete data structure reference
* **Advanced**: :ref:`custom_mesh_conversion` - Full conversion example with validation
