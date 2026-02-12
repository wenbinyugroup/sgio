.. _custom_mesh_troubleshooting:

Troubleshooting Common Issues
==============================

This page covers common problems and their solutions when creating StructureGene from custom mesh data.

Connectivity Issues
-------------------

Error: "Element connectivity out of bounds"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

.. code-block:: text

    IndexError: index 100 is out of bounds for axis 0 with size 5

**Cause:** 

Connectivity array uses original node IDs instead of 0-based array indices.

**Solution:**

Create a mapping from original node IDs to array indices:

.. code-block:: python

    # ✗ WRONG: Using original IDs directly
    points = np.array([
        [0, 0, 0],  # This is index 0
        [1, 0, 0],  # This is index 1
    ])
    cells = [CellBlock(type='line', data=np.array([[100, 200]]))]  # Wrong!
    
    # ✓ CORRECT: Map original IDs to indices
    original_node_ids = [100, 200, 300, 400]
    node_id_to_index = {nid: idx for idx, nid in enumerate(original_node_ids)}
    
    # Apply mapping
    original_connectivity = [100, 200]
    correct_connectivity = [node_id_to_index[nid] for nid in original_connectivity]
    # Result: [0, 1]
    
    cells = [CellBlock(type='line', data=np.array([correct_connectivity]))]

**Best Practice:**

Always build the mapping at the start of your conversion:

.. code-block:: python

    # Sort node IDs to get consistent ordering
    node_ids = sorted(mesh_data['nodes'].keys())
    node_id_to_index = {nid: idx for idx, nid in enumerate(node_ids)}
    
    # Create points array in the same order
    points = np.array([mesh_data['nodes'][nid] for nid in node_ids])
    
    # Apply to all connectivity
    for elem in mesh_data['elements']:
        conn_indices = [node_id_to_index[nid] for nid in elem['connectivity']]
        # Use conn_indices in CellBlock

Error: "Node ID not found in mapping"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

.. code-block:: text

    KeyError: 999

**Cause:**

An element references a node ID that doesn't exist in your nodes dictionary.

**Solution:**

Add validation and helpful error messages:

.. code-block:: python

    for elem in mesh_data['elements']:
        try:
            conn = [node_id_to_index[nid] for nid in elem['connectivity']]
        except KeyError as e:
            missing_node_id = int(str(e))
            raise ValueError(
                f"Element {elem['id']} references undefined node ID {missing_node_id}. "
                f"Available node IDs: {min(node_ids)}-{max(node_ids)}"
            )

Property and Material Issues
----------------------------

Error: "Property ID not found in mocombos"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

.. code-block:: text

    KeyError: 5

**Cause:**

Property IDs in ``cell_data['property_id']`` don't match keys in ``sg.mocombos``.

**Solution:**

Ensure all property IDs used by elements are defined in mocombos:

.. code-block:: python

    # Check which property IDs are actually used
    used_prop_ids = set()
    for prop_array in sg.mesh.cell_data['property_id']:
        used_prop_ids.update(prop_array)
    
    print(f"Property IDs used: {sorted(used_prop_ids)}")
    print(f"Property IDs defined: {sorted(sg.mocombos.keys())}")
    
    # Find missing definitions
    for prop_id in used_prop_ids:
        if prop_id not in sg.mocombos:
            print(f"ERROR: Missing mocombo for property_id {prop_id}")

**Prevention:**

When building mocombos, ensure every unique (material, angle) combination gets an entry:

.. code-block:: python

    mocombo_map = {}
    next_property_id = 1
    
    for elem in mesh_data['elements']:
        key = (elem['material'], elem['angle'])
        if key not in mocombo_map:
            mocombo_map[key] = next_property_id
            sg.mocombos[next_property_id] = key
            next_property_id += 1

Error: "Material name not found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

.. code-block:: text

    KeyError: 'steel'

**Cause:**

Material name in mocombos doesn't exactly match a key in ``sg.materials``. Often due to:
- Case sensitivity (``'Steel'`` vs ``'steel'``)
- Whitespace (``'Steel'`` vs ``'Steel '``)
- Typos

**Solution:**

Verify material names match exactly:

.. code-block:: python

    # Check what's defined
    print("Defined materials:", list(sg.materials.keys()))
    
    # Check what's referenced
    for prop_id, (mat_name, angle) in sg.mocombos.items():
        if mat_name not in sg.materials:
            print(f"ERROR: Property {prop_id} references undefined material '{mat_name}'")
            # Show similar names
            from difflib import get_close_matches
            similar = get_close_matches(mat_name, sg.materials.keys())
            if similar:
                print(f"  Did you mean: {similar[0]}?")

**Prevention:**

Normalize material names during conversion:

.. code-block:: python

    def normalize_name(name):
        """Normalize material name (strip whitespace, consistent case)."""
        return name.strip()
    
    # Use when adding materials
    for mat_name, props in mesh_data['materials'].items():
        normalized_name = normalize_name(mat_name)
        material = CauchyContinuumModel(name=normalized_name, ...)
        sg.materials[normalized_name] = material
    
    # Use when creating mocombos
    key = (normalize_name(elem['material']), elem['angle'])

Mesh Structure Issues
---------------------

Error: "Mixed element types in one cell block"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

Elements with different numbers of nodes in the same CellBlock, or validation errors.

**Cause:**

Trying to put different element types (e.g., triangles and quads) in one CellBlock.

**Solution:**

Group elements by type before creating CellBlocks:

.. code-block:: python

    # ✗ WRONG: Mixed types
    cells = [CellBlock(type='triangle', data=np.array([
        [0, 1, 2],     # 3 nodes (triangle)
        [3, 4, 5, 6],  # 4 nodes (quad) - ERROR!
    ]))]
    
    # ✓ CORRECT: Separate by type
    elements_by_type = {}
    for elem in mesh_data['elements']:
        elem_type = elem['type']
        if elem_type not in elements_by_type:
            elements_by_type[elem_type] = []
        elements_by_type[elem_type].append(elem)
    
    cells = []
    for elem_type, elems in elements_by_type.items():
        connectivity = [...]  # Build connectivity for this type
        cells.append(CellBlock(type=elem_type, data=np.array(connectivity)))

Error: "Unsupported element type"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

.. code-block:: text

    ValueError: Unsupported element type: TRIA6

**Cause:**

Your custom format uses element type names that need mapping to meshio names.

**Solution:**

Create a type mapping dictionary:

.. code-block:: python

    TYPE_MAP = {
        # Custom format -> meshio format
        'TRIA3': 'triangle',
        'TRIA6': 'triangle6',
        'QUAD4': 'quad',
        'QUAD8': 'quad8',
        'QUAD9': 'quad9',
        'TETRA4': 'tetra',
        'TETRA10': 'tetra10',
        'HEXA8': 'hexahedron',
        'HEXA20': 'hexahedron20',
        'HEXA27': 'hexahedron27',
        'WEDGE6': 'wedge',
        'PYRA5': 'pyramid',
    }
    
    for elem in mesh_data['elements']:
        if elem['type'] not in TYPE_MAP:
            raise ValueError(
                f"Unsupported element type: {elem['type']}. "
                f"Supported types: {list(TYPE_MAP.keys())}"
            )
        meshio_type = TYPE_MAP[elem['type']]

Dimension and Configuration Issues
-----------------------------------

Error: "Invalid model type for dimension"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

.. code-block:: text

    ValueError: Model type 'PL1' requires sgdim=2, but got sgdim=3

**Cause:**

Mismatch between StructureGene dimension and model type.

**Solution:**

Match model type to dimension:

.. code-block:: python

    # Dimension 1 (Beam)
    sg = StructureGene(sgdim=1, smdim=1)
    sgio.write(..., model_type='BM1')  # or BM2, BM3, BM4
    
    # Dimension 2 (Plate/Shell)
    sg = StructureGene(sgdim=2, smdim=2)
    sgio.write(..., model_type='PL1')  # or PL2
    
    # Dimension 3 (Solid)
    sg = StructureGene(sgdim=3, smdim=3)
    sgio.write(..., model_type='SD1')  # or SD2

**Auto-select model type:**

.. code-block:: python

    MODEL_TYPES = {
        1: 'BM1',  # Default for beams
        2: 'PL1',  # Default for plates
        3: 'SD1',  # Default for solids
    }
    
    model_type = MODEL_TYPES[sg.sgdim]
    sgio.write(sg=sg, fn='output.sc', model_type=model_type, ...)

Validation and Debugging
-------------------------

Empty or Missing Mesh
^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**

.. code-block:: text

    AttributeError: 'NoneType' object has no attribute 'points'

**Solution:**

Check mesh exists before accessing:

.. code-block:: python

    if sg.mesh is None:
        raise ValueError("Mesh not created. Did you assign sg.mesh?")
    
    if sg.nnodes == 0:
        raise ValueError("Mesh has no nodes")
    
    if sg.nelems == 0:
        raise ValueError("Mesh has no elements")

Pre-write Validation Checklist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use this validation function before writing:

.. code-block:: python

    def validate_sg(sg):
        """Comprehensive validation with helpful messages."""
        errors = []
        
        # Configuration
        if sg.sgdim not in [1, 2, 3]:
            errors.append(f"Invalid sgdim: {sg.sgdim}")
        if not sg.name:
            errors.append("Name is empty")
        
        # Mesh
        if sg.mesh is None:
            errors.append("Mesh is None")
        elif sg.nnodes == 0:
            errors.append("Mesh has no nodes")
        elif sg.nelems == 0:
            errors.append("Mesh has no elements")
        
        # Materials
        if not sg.materials:
            errors.append("No materials defined")
        
        # Mocombos
        if not sg.mocombos:
            errors.append("No mocombos defined")
        
        # Property IDs
        if sg.mesh is not None:
            for i, prop_array in enumerate(sg.mesh.cell_data.get('property_id', [])):
                for prop_id in np.unique(prop_array):
                    if prop_id not in sg.mocombos:
                        errors.append(
                            f"Block {i}: property_id {prop_id} not in mocombos"
                        )
        
        # Material references
        for prop_id, (mat_name, angle) in sg.mocombos.items():
            if mat_name not in sg.materials:
                errors.append(
                    f"Mocombo {prop_id} references undefined material '{mat_name}'"
                )
        
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  ✗ {error}")
            return False
        else:
            print("✓ Validation passed")
            return True

Performance Issues
------------------

Slow conversion for large meshes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Converting millions of nodes/elements is slow.

**Solutions:**

1. **Pre-allocate arrays:**

.. code-block:: python

    # Slow: Appending to lists
    connectivity = []
    for elem in elems:
        connectivity.append([...])
    
    # Fast: Pre-allocate numpy array
    n_elems = len(elems)
    nodes_per_elem = 4
    connectivity = np.zeros((n_elems, nodes_per_elem), dtype=int)
    for i, elem in enumerate(elems):
        connectivity[i] = [...]

2. **Vectorize operations:**

.. code-block:: python

    # Slow: Loop over mapping
    conn_indices = [node_id_to_index[nid] for nid in elem['connectivity']]
    
    # Fast: Use numpy vectorized operations
    conn_array = np.array(elem['connectivity'])
    conn_indices = np.vectorize(node_id_to_index.get)(conn_array)

3. **Process in chunks:**

.. code-block:: python

    CHUNK_SIZE = 10000
    for i in range(0, len(elements), CHUNK_SIZE):
        chunk = elements[i:i+CHUNK_SIZE]
        # Process chunk

Getting More Help
-----------------

If you're still having issues:

1. **Check data structure documentation**: :ref:`custom_mesh_data_structures`
2. **Review working examples**: :ref:`custom_mesh_quickstart` and :ref:`custom_mesh_conversion`
3. **Verify with minimal example**: Strip down to smallest failing case
4. **Check sgio version**: Ensure you're using the latest version

**Debug output template:**

.. code-block:: python

    print("Debug info:")
    print(f"  sgio version: {sgio.__version__}")
    print(f"  sgdim: {sg.sgdim}")
    print(f"  Nodes: {sg.nnodes if sg.mesh else 'No mesh'}")
    print(f"  Elements: {sg.nelems if sg.mesh else 'No mesh'}")
    print(f"  Materials: {list(sg.materials.keys())}")
    print(f"  Mocombos: {dict(sg.mocombos)}")
    if sg.mesh and 'property_id' in sg.mesh.cell_data:
        all_props = []
        for pa in sg.mesh.cell_data['property_id']:
            all_props.extend(pa)
        print(f"  Property IDs used: {sorted(set(all_props))}")
