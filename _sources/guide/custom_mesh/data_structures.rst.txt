.. _custom_mesh_data_structures:

Data Structure Reference
=========================

This page provides detailed information about the data structures used in StructureGene.

StructureGene Configuration
----------------------------

.. code-block:: python

    from sgio import StructureGene
    
    sg = StructureGene(
        name='my_structure',    # Name of the structure
        sgdim=3,                 # Dimension: 1=beam, 2=plate/shell, 3=solid
        smdim=3,                 # Structural model dimension (usually same as sgdim)
        spdim=3                  # Space dimension (defaults to sgdim if not specified)
    )

Parameters
^^^^^^^^^^

* **name** (str, optional): Name of your structure. Used for file naming. Default: ``''``

* **sgdim** (int, optional): Dimension of the structure gene
  
  - ``1``: 1D beam analysis
  - ``2``: 2D plate/shell analysis
  - ``3``: 3D solid analysis

* **smdim** (int, optional): Dimension of the structural model. Usually matches ``sgdim``.

* **spdim** (int, optional): Dimension of the space containing the structure. Defaults to ``sgdim`` if not specified. For example, a curved beam in 3D space would have ``sgdim=1`` and ``spdim=3``.

Mesh Structure
--------------

The mesh uses the `meshio <https://github.com/nschloe/meshio>`_ format:

.. code-block:: python

    import numpy as np
    from meshio import Mesh, CellBlock
    
    mesh = Mesh(
        points=np.array([[x1, y1, z1], [x2, y2, z2], ...]),
        cells=[...],
        cell_data={...},
        point_data={...}  # Optional
    )
    
    sg.mesh = mesh

Points (Nodes)
^^^^^^^^^^^^^^

``points`` is a NumPy array of shape ``(n_nodes, 3)`` containing node coordinates:

.. code-block:: python

    points = np.array([
        [0.0, 0.0, 0.0],  # Node 0
        [1.0, 0.0, 0.0],  # Node 1
        [1.0, 1.0, 0.0],  # Node 2
    ])

.. important::
   Always use 3 columns even for 2D or 1D problems. Set unused dimensions to 0.

Cells (Elements)
^^^^^^^^^^^^^^^^

``cells`` is a list of ``CellBlock`` objects. Each block contains elements of the same type:

.. code-block:: python

    cells = [
        CellBlock(
            type='triangle',
            data=np.array([
                [0, 1, 2],
                [1, 3, 2],
            ])
        ),
        CellBlock(
            type='quad',
            data=np.array([
                [4, 5, 6, 7],
            ])
        )
    ]

Supported Element Types
"""""""""""""""""""""""

* **1D elements**: ``'line'`` (2 nodes), ``'line3'`` (3 nodes)
* **2D elements**: ``'triangle'`` (3), ``'triangle6'`` (6), ``'quad'`` (4), ``'quad8'`` (8), ``'quad9'`` (9)
* **3D elements**: ``'tetra'`` (4), ``'tetra10'`` (10), ``'hexahedron'`` (8), ``'hexahedron20'`` (20), ``'hexahedron27'`` (27), ``'wedge'`` (6), ``'pyramid'`` (5)

Connectivity: Critical Note
""""""""""""""""""""""""""""

The connectivity array **must use 0-based indices** referencing the ``points`` array, not original node IDs!

.. code-block:: python

    # ✓ CORRECT: Use 0-based array indices
    points = np.array([
        [0, 0, 0],  # Index 0 (original ID might be 100)
        [1, 0, 0],  # Index 1 (original ID might be 200)
        [0, 1, 0],  # Index 2 (original ID might be 300)
    ])
    cells = [CellBlock(type='triangle', data=np.array([[0, 1, 2]]))]
    
    # ✗ WRONG: Don't use original IDs in connectivity!
    # cells = [CellBlock(type='triangle', data=np.array([[100, 200, 300]]))]

Cell Data (Per-Element Data)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``cell_data`` is a dictionary with one entry per cell block:

.. code-block:: python

    cell_data = {
        'property_id': [
            np.array([1, 1]),     # Property IDs for first cell block
            np.array([2]),        # Property IDs for second cell block
        ],
        'element_id': [          # Optional: original element IDs
            np.array([1000, 1001]),
            np.array([2000]),
        ]
    }

**Required:**
  * ``'property_id'``: List of arrays assigning property IDs to elements

**Optional:**
  * ``'element_id'``: Original element IDs from your format
  * ``'property_ref_csys'``: Element local coordinate systems

Point Data (Per-Node Data)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``point_data`` is optional and stores per-node information:

.. code-block:: python

    point_data = {
        'node_id': [100, 200, 300, 400],  # Original node IDs
    }

Materials
---------

Materials are stored in a dictionary indexed by name:

.. code-block:: python

    from sgio.model import CauchyContinuumModel
    
    # Create material
    steel = CauchyContinuumModel(
        name='Steel',
        isotropy=2,    # 0=orthotropic, 1=transverse, 2=isotropic
        e=200e9,
        nu=0.3,
        density=7850
    )
    
    # Add to StructureGene
    sg.materials['Steel'] = steel

Isotropy Types
^^^^^^^^^^^^^^

The ``isotropy`` parameter determines material symmetry:

**Isotropic (isotropy=2)**

.. code-block:: python

    mat = CauchyContinuumModel(
        name='Aluminum',
        isotropy=2,
        e=70e9,           # Single Young's modulus
        nu=0.33,          # Single Poisson's ratio
        density=2700
    )

**Transversely Isotropic (isotropy=1)**

.. code-block:: python

    mat = CauchyContinuumModel(
        name='Fiber',
        isotropy=1,
        e=[135e9, 10e9],      # [E_axial, E_transverse]
        g=[5e9, 5e9],         # [G_axial, G_transverse]
        nu=[0.3, 0.45],       # [nu_axial, nu_transverse]
        density=1600
    )

**Orthotropic (isotropy=0)**

.. code-block:: python

    mat = CauchyContinuumModel(
        name='CarbonFiber',
        isotropy=0,
        e=[135e9, 10e9, 10e9],    # [E1, E2, E3]
        g=[5e9, 5e9, 5e9],        # [G12, G13, G23]
        nu=[0.3, 0.3, 0.45],      # [nu12, nu13, nu23]
        density=1600
    )

For more material types, see :ref:`guide_model`.

Material-Orientation Combinations (mocombos)
---------------------------------------------

The ``mocombos`` dictionary maps property IDs to (material_name, angle) pairs:

.. code-block:: python

    sg.mocombos = {
        1: ('Steel', 0.0),           # Property 1: Steel at 0°
        2: ('CarbonFiber', 45.0),    # Property 2: Carbon at 45°
        3: ('CarbonFiber', -45.0),   # Property 3: Carbon at -45°
    }

**Why separate from materials?**

This separation allows you to reuse the same material at different orientations without creating duplicate material definitions.

Relationship Chain
^^^^^^^^^^^^^^^^^^

.. code-block:: text

    Element → property_id → mocombo → (material_name, angle) → Material object
    
    Example:
    Element 5 → property_id=2 → mocombo[2]=('CarbonFiber', 45.0) → sg.materials['CarbonFiber']

Complete Example: Composite Laminate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import numpy as np
    from meshio import Mesh, CellBlock
    from sgio import StructureGene
    from sgio.model import CauchyContinuumModel
    import sgio
    
    # Create StructureGene
    sg = StructureGene(name='laminate', sgdim=2, smdim=2)
    
    # Define one material
    carbon = CauchyContinuumModel(
        name='CarbonFiber',
        isotropy=0,
        e=[135e9, 10e9, 10e9],
        g=[5e9, 5e9, 5e9],
        nu=[0.3, 0.3, 0.45],
        density=1600
    )
    sg.materials['CarbonFiber'] = carbon
    
    # Create [0/45/-45/90] layup using mocombos
    sg.mocombos = {
        1: ('CarbonFiber', 0.0),
        2: ('CarbonFiber', 45.0),
        3: ('CarbonFiber', -45.0),
        4: ('CarbonFiber', 90.0),
    }
    
    # Create 2x2 mesh (4 quad elements)
    points = np.array([
        [0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [1.0, 0.0, 0.0],
        [0.0, 0.5, 0.0], [0.5, 0.5, 0.0], [1.0, 0.5, 0.0],
        [0.0, 1.0, 0.0], [0.5, 1.0, 0.0], [1.0, 1.0, 0.0],
    ])
    
    cells = [
        CellBlock(type='quad', data=np.array([
            [0, 1, 4, 3],  # Element 0
            [1, 2, 5, 4],  # Element 1
            [3, 4, 7, 6],  # Element 2
            [4, 5, 8, 7],  # Element 3
        ]))
    ]
    
    # Assign different orientations to different elements
    cell_data = {
        'property_id': [np.array([1, 2, 3, 4])]
    }
    
    sg.mesh = Mesh(points=points, cells=cells, cell_data=cell_data)
    
    # Write to file
    sgio.write(sg=sg, fn='laminate.sc', file_format='swiftcomp',
               format_version='2.1', model_type='PL1')

Material Name-ID Mapping
-------------------------

VABS/SwiftComp use numeric material IDs. Sgio handles this automatically, but you can control it explicitly:

.. code-block:: python

    # Automatic (recommended)
    sg.add_material(steel)      # Gets ID 1
    sg.add_material(aluminum)   # Gets ID 2
    
    # Manual control
    sg.material_name_id_pairs = [
        ['Steel', 1],
        ['Aluminum', 2],
        ['CarbonFiber', 3]
    ]

Model Type Selection
--------------------

When writing to VABS/SwiftComp, specify the analysis model:

**1D Beam** (sgdim=1)
  * ``'BM1'``: Classical (Euler-Bernoulli)
  * ``'BM2'``: Refined (Timoshenko)
  * ``'BM3'``: Vlasov
  * ``'BM4'``: Trapeze effect

**2D Plate/Shell** (sgdim=2)
  * ``'PL1'``: Classical (Kirchhoff-Love)
  * ``'PL2'``: Refined (Reissner-Mindlin)

**3D Solid** (sgdim=3)
  * ``'SD1'``: Classical continuum
  * ``'SD2'``: Refined continuum

See :ref:`guide_model` for details on each model.

Summary Checklist
-----------------

Before writing your StructureGene to file, verify:

.. code-block:: python

    # ✓ StructureGene configured
    assert sg.sgdim in [1, 2, 3]
    assert sg.name != ''
    
    # ✓ Mesh created
    assert sg.mesh is not None
    assert sg.nnodes > 0
    assert sg.nelems > 0
    
    # ✓ Materials defined
    assert len(sg.materials) > 0
    
    # ✓ Mocombos created
    assert len(sg.mocombos) > 0
    
    # ✓ All property IDs reference valid mocombos
    for prop_array in sg.mesh.cell_data['property_id']:
        for prop_id in prop_array:
            assert prop_id in sg.mocombos
    
    # ✓ All mocombos reference valid materials
    for prop_id, (mat_name, angle) in sg.mocombos.items():
        assert mat_name in sg.materials

Next Steps
----------

* See :ref:`custom_mesh_conversion` for a complete conversion example
* Check :ref:`custom_mesh_troubleshooting` if you encounter issues
