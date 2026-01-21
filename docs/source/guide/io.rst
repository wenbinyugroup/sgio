Read and Write SG Data
===========================

This guide covers reading and writing Structure Gene (SG) data in various formats.


Read SG data
--------------

To read SG data from a file, use the :func:`sgio.read` function.

Basic Usage
^^^^^^^^^^^

..  code-block:: python

    import sgio

    sg = sgio.read(
        filename='cross_section.sg',
        file_format='vabs',
        model_type='BM2',
    )

Parameters
^^^^^^^^^^

- ``filename`` (str): Path to the SG file to be read
- ``file_format`` (str): Format of the SG file

  - ``'vabs'`` - VABS format
  - ``'sc'`` or ``'swiftcomp'`` - SwiftComp format
  - ``'abaqus'`` - Abaqus .inp format
  - ``'gmsh'`` - Gmsh mesh format

- ``model_type`` (str, optional): Type of structural model

  - ``'BM1'`` - Euler-Bernoulli beam (classical beam theory)
  - ``'BM2'`` - Timoshenko beam (includes shear deformation)
  - ``'PL1'`` - Kirchhoff-Love plate
  - ``'PL2'`` - Reissner-Mindlin plate
  - ``'SD1'`` - Cauchy continuum (3D solid)

- ``sgdim`` (int, optional): Dimension of the SG data (1, 2, or 3)

  - For VABS cross-sections, dimension is 2 (can be omitted)
  - For 3D structure genes, dimension is 3

- ``format_version`` (str, optional): Version of the file format (e.g., '4.0', '4.1' for VABS)

Returns
^^^^^^^

The function returns a :class:`sgio.StructureGene` object containing:

- ``mesh``: Mesh data (nodes, elements)
- ``materials``: Material properties
- ``model``: Structural model information
- ``layups``: Composite layup definitions (if applicable)

Examples
^^^^^^^^

**Read VABS input file:**

..  code-block:: python

    import sgio

    # Read VABS 4.1 format file for Timoshenko beam
    sg = sgio.read(
        filename='airfoil.sg',
        file_format='vabs',
        model_type='BM2',
        format_version='4.1'
    )

    print(f"Nodes: {len(sg.mesh.points)}")
    print(f"Elements: {len(sg.mesh.cells)}")

**Read Abaqus input file:**

..  code-block:: python

    import sgio

    # Read Abaqus .inp file for 3D solid
    sg = sgio.read(
        filename='cube.inp',
        file_format='abaqus',
        model_type='SD1',
        sgdim=3
    )

**Read with error handling:**

..  code-block:: python

    import sgio
    from pathlib import Path

    input_file = Path('cross_section.sg')

    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        exit(1)

    sg = sgio.read(str(input_file), 'vabs', model_type='BM2')


Read Mesh Data Only
^^^^^^^^^^^^^^^^^^^

To read only the mesh data without material properties:

..  code-block:: python

    import sgio

    sg = sgio.read(
        filename='cross_section.sg',
        file_format='vabs',
        mesh_only=True
    )

    # Access mesh data
    nodes = sg.mesh.points
    elements = sg.mesh.cells

**Note:** When ``mesh_only=True``, material properties and layup information are not loaded.

Alternative: Direct meshio Usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For advanced mesh operations, you can use ``meshio`` directly:

..  code-block:: python

    import meshio

    mesh = meshio.read('mesh_file.msh')
    # See meshio documentation for more options



Write SG data
----------------

Use the :func:`sgio.write` function to write Structure Gene data to a file.

Basic Usage
^^^^^^^^^^^

..  code-block:: python

    import sgio

    sgio.write(
        sg=sg,
        fn='output.sg',
        file_format='vabs',
    )

Parameters
^^^^^^^^^^

- ``sg`` (StructureGene): Structure Gene object to write
- ``fn`` (str): Output file path
- ``file_format`` (str): Output format ('vabs', 'swiftcomp', 'gmsh', etc.)
- ``format_version`` (str, optional): Version of the output format
- ``analysis`` (str, optional): Analysis type for VABS/SwiftComp
- ``mesh_only`` (bool, optional): Write only mesh data (default: False)
- ``renumber_nodes`` (bool, optional): Renumber nodes sequentially
- ``renumber_elements`` (bool, optional): Renumber elements sequentially

Examples
^^^^^^^^

**Write VABS input file:**

..  code-block:: python

    import sgio

    # Write to VABS 4.1 format
    sgio.write(
        sg=sg,
        fn='cross_section.sg',
        file_format='vabs',
        format_version='4.1'
    )

**Write to Gmsh for visualization:**

..  code-block:: python

    import sgio

    # Write mesh to Gmsh format
    sgio.write(
        sg=sg,
        fn='visualization.msh',
        file_format='gmsh',
        mesh_only=True
    )

**Write with node/element renumbering:**

..  code-block:: python

    import sgio

    # Renumber nodes and elements for clean output
    sgio.write(
        sg=sg,
        fn='output.sg',
        file_format='vabs',
        renumber_nodes=True,
        renumber_elements=True
    )

Write Mesh Data Only
^^^^^^^^^^^^^^^^^^^^

To write only mesh data without material properties:

..  code-block:: python

    import sgio

    sgio.write(
        sg=sg,
        fn='mesh_only.msh',
        file_format='gmsh',
        mesh_only=True
    )

Alternative: Direct meshio Usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For advanced mesh writing, use ``meshio`` directly:

..  code-block:: python

    # Assuming sg is a StructureGene object
    sg.mesh.write('output.msh')
    # See meshio documentation for format-specific options



Supported Data Formats
-----------------------

SGIO supports multiple file formats for Structure Gene data.

Complete SG Data Support
^^^^^^^^^^^^^^^^^^^^^^^^^

These formats support full Structure Gene data (mesh + materials + properties):

**VABS**
  - Format identifier: ``'vabs'``
  - Versions: 4.0, 4.1
  - Use for: Cross-sectional analysis (2D)
  - Models: BM1 (Euler-Bernoulli), BM2 (Timoshenko)

**SwiftComp**
  - Format identifier: ``'swiftcomp'`` or ``'sc'``
  - Versions: 2.1, 2.2
  - Use for: General structure gene analysis (1D, 2D, 3D)
  - Models: BM1, BM2, PL1, PL2, SD1

**Abaqus**
  - Format identifier: ``'abaqus'``
  - File extension: ``.inp``
  - Use for: Import from Abaqus CAE
  - Supports: Material properties, element sets, node sets

Mesh-Only Support
^^^^^^^^^^^^^^^^^

These formats support mesh data only (no materials):

**Gmsh**
  - Format identifier: ``'gmsh'``
  - File extension: ``.msh``
  - Use for: Visualization, mesh generation
  - Note: Best for visualization with ParaView or Gmsh

**Other meshio formats**
  - Various formats supported through meshio
  - See `meshio documentation <https://github.com/nschloe/meshio>`_ for details

Format Conversion Matrix
^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - From \\ To
     - VABS
     - SwiftComp
     - Abaqus
     - Gmsh
   * - VABS
     - ✓
     - ✓
     - ✓
     - ✓
   * - SwiftComp
     - ✓
     - ✓
     - ✓
     - ✓
   * - Abaqus
     - ✓
     - ✓
     - ✓
     - ✓
   * - Gmsh
     - ✓*
     - ✓*
     - ✓*
     - ✓

\* Mesh data only (materials must be added separately)

Best Practices
^^^^^^^^^^^^^^

1. **Use VABS/SwiftComp for analysis**: These formats preserve all SG data
2. **Use Gmsh for visualization**: Convert to .msh for easy visualization
3. **Use Abaqus for CAD integration**: Import complex geometries from Abaqus
4. **Check file existence**: Always verify input files exist before reading
5. **Handle errors gracefully**: Use try-except blocks for robust code

Example: Multi-Format Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

..  code-block:: python

    import sgio
    from pathlib import Path

    # 1. Import from Abaqus
    sg = sgio.read('model.inp', 'abaqus', model_type='BM2')

    # 2. Write to VABS for analysis
    sgio.write(sg, 'model.sg', 'vabs')

    # 3. Export to Gmsh for visualization
    sgio.write(sg, 'model.msh', 'gmsh', mesh_only=True)

    print("Conversion complete!")

See Also
^^^^^^^^

- :doc:`convert` - Detailed guide on format conversion
- :doc:`io_model` - Reading analysis output (beam properties)
- :doc:`io_state` - Reading state data (stress/strain fields)
- `Examples <../../../examples/>`_ - Working code examples
