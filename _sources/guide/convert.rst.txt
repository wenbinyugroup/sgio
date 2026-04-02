Convert SG Data
=============================

One of the main capabilities of SGIO is to convert SG data between different formats.
This can be done using the :func:`sgio.convert` function (API) or the ``sgio convert`` command (CLI).

Overview
--------

SGIO supports conversion between:

- **VABS** ↔ **SwiftComp** ↔ **Abaqus** ↔ **Gmsh**
- Mesh-only conversions for visualization
- Format version conversions (e.g., VABS 4.0 → 4.1)

Basic Usage
-----------

API Method
^^^^^^^^^^

..  code-block:: python

    import sgio

    sgio.convert(
        file_name_in='input.inp',
        file_name_out='output.sg',
        file_format_in='abaqus',
        file_format_out='vabs',
        model_type='BM2'
    )

CLI Method
^^^^^^^^^^

..  code-block:: bash

    sgio convert input.inp output.sg -ff abaqus -tf vabs -m BM2

Common Parameters
^^^^^^^^^^^^^^^^^

- ``file_name_in``: Input file path
- ``file_name_out``: Output file path
- ``file_format_in``: Input format (vabs, swiftcomp, abaqus, gmsh)
- ``file_format_out``: Output format
- ``model_type``: Structural model (BM1, BM2, PL1, PL2, SD1)
- ``mesh_only``: Convert mesh data only (default: False)
- ``renum_node``: Renumber nodes (default: False)
- ``renum_elem``: Renumber elements (default: False)



Common Conversion Scenarios
---------------------------

Scenario 1: VABS to Gmsh for Visualization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert a VABS cross-section to Gmsh format for visualization.

**API:**

..  literalinclude:: ../../../examples/convert_mesh_data_vabs2gmsh.py
    :language: python
    :lines: 1-30

**CLI:**

..  code-block:: bash

    sgio convert cs_box_t_vabs41.sg cs_box_t_vabs41.msh \
        -ff vabs -tf gmsh -m BM2 --mesh-only

**Result:**

..  figure:: ../../../examples/files/cs_box_t_vabs41.msh.png
    :alt: Visualization of the box cross-section in Gmsh
    :align: center
    :width: 80%

    Box cross-section visualized in Gmsh

Scenario 2: Abaqus to VABS
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert an Abaqus cross-section model to VABS input format.

**API:**

..  code-block:: python

    import sgio

    sgio.convert(
        'airfoil.inp',      # Abaqus input file
        'airfoil.sg',       # VABS output file
        'abaqus',           # Input format
        'vabs',             # Output format
        model_type='BM2'    # Timoshenko beam
    )

**CLI:**

..  code-block:: bash

    sgio convert airfoil.inp airfoil.sg -ff abaqus -tf vabs -m BM2

See ``examples/convert_abaqus_cs_to_vabs/`` for a complete example.

Scenario 3: Abaqus to SwiftComp (3D)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert a 3D Abaqus model to SwiftComp format.

**API:**

..  code-block:: python

    import sgio

    sgio.convert(
        'cube.inp',         # Abaqus 3D model
        'cube.sg',          # SwiftComp output
        'abaqus',           # Input format
        'swiftcomp',        # Output format
        model_type='SD1',   # 3D solid model
        sgdim=3             # 3D structure gene
    )

**CLI:**

..  code-block:: bash

    sgio convert cube.inp cube.sg \
        -ff abaqus -tf swiftcomp -m SD1 --sgdim 3

See ``examples/convert_abaqus_sg3d_to_sc/`` for a complete example.

Scenario 4: Format Version Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert between different versions of the same format.

**VABS 4.0 to 4.1:**

..  code-block:: python

    import sgio

    sgio.convert(
        'old_format.sg',
        'new_format.sg',
        'vabs',
        'vabs',
        file_version_in='4.0',
        file_version_out='4.1',
        model_type='BM2'
    )

Scenario 5: Two-Step Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For more control, use separate read and write operations:

..  code-block:: python

    import sgio

    # Step 1: Read from Abaqus
    sg = sgio.read('model.inp', 'abaqus', model_type='BM2')

    # Inspect or modify the data
    print(f"Nodes: {len(sg.mesh.points)}")
    print(f"Elements: {len(sg.mesh.cells)}")

    # Step 2: Write to VABS
    sgio.write(sg, 'model.sg', 'vabs')

    # Step 3: Also export for visualization
    sgio.write(sg, 'model.msh', 'gmsh', mesh_only=True)


See Also
--------

- :doc:`io` - Detailed I/O documentation
- :doc:`io_model` - Reading analysis output
- `Examples <../../../examples/>`_ - Working code examples
- `Test Suite <../../../tests/>`_ - Comprehensive test cases
