Migration Guide: Automatic Numbering
=====================================

This guide helps you update code that used the old manual numbering parameters.

What Changed
------------

**Old behavior (deprecated)**:
- You had to manually specify ``renumber_nodes=True`` or ``renumber_elements=True``
- Writers would fail with validation errors if numbering was wrong
- You needed to understand format requirements

**New behavior (automatic)**:
- Node and element numbering is handled automatically based on format requirements
- Writers automatically renumber when needed (with informational warning)
- No user intervention required — it "just works"

Removed Parameters
------------------

The following parameters have been **removed** from all read/write functions:

- ``renumber_nodes``
- ``renumber_elements``
- ``use_sequential_node_ids``
- ``use_sequential_element_ids``

Migration Steps
---------------

1. Remove Deprecated Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Before (old API)**:

..  code-block:: python

    import sgio

    # Old code with manual renumbering
    sg = sgio.read('input.inp', file_format='abaqus', model_type='BM2')
    sgio.write(
        sg=sg,
        fn='output.vab',
        file_format='vabs',
        renumber_nodes=True,      # ← Remove this
        renumber_elements=True    # ← Remove this
    )

**After (new API)**:

..  code-block:: python

    import sgio

    # New code with automatic renumbering
    sg = sgio.read('input.inp', file_format='abaqus', model_type='BM2')
    sgio.write(
        sg=sg,
        fn='output.vab',
        file_format='vabs'
        # Automatic renumbering — no parameters needed!
    )

2. Handle Warnings (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to **suppress** renumbering warnings:

..  code-block:: python

    import warnings
    import sgio

    sg = sgio.read('input.inp', file_format='abaqus', model_type='BM2')

    # Suppress UserWarning about renumbering
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        sgio.write(sg, 'output.vab', file_format='vabs')

If you want to **capture** warnings programmatically:

..  code-block:: python

    import warnings
    import sgio

    sg = sgio.read('input.inp', file_format='abaqus', model_type='BM2')

    # Capture warnings to check if renumbering occurred
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        sgio.write(sg, 'output.vab', file_format='vabs')
        
        if w:
            print(f"Warning: {w[0].message}")
            # Proceed knowing renumbering occurred

3. Update Validation Code
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you manually validated numbering, **remove validation calls**:

**Before (old API)**:

..  code-block:: python

    from sgio.core.numbering import validate_node_ids

    # Old code with manual validation
    sg = sgio.read('input.inp', file_format='abaqus', model_type='BM2')
    
    # Manual validation (no longer needed)
    validate_node_ids(sg.mesh.point_data['node_id'], format='vabs')
    
    sgio.write(sg, 'output.vab', file_format='vabs')

**After (new API)**:

..  code-block:: python

    import sgio

    # New code — validation and renumbering automatic
    sg = sgio.read('input.inp', file_format='abaqus', model_type='BM2')
    sgio.write(sg, 'output.vab', file_format='vabs')
    # Validation happens automatically inside write()

Common Migration Scenarios
---------------------------

Scenario 1: Abaqus → VABS Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Before**:

..  code-block:: python

    sg = sgio.read('model.inp', file_format='abaqus', model_type='BM2')
    
    # Manual check and renumber
    from sgio.core.numbering import validate_node_ids
    try:
        validate_node_ids(sg.mesh.point_data['node_id'], format='vabs')
    except ValueError:
        # Force renumbering
        sgio.write(sg, 'model.vab', file_format='vabs', renumber_nodes=True)

**After**:

..  code-block:: python

    sg = sgio.read('model.inp', file_format='abaqus', model_type='BM2')
    sgio.write(sg, 'model.vab', file_format='vabs')
    # Automatic renumbering with warning if needed

Scenario 2: Programmatic Mesh Creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Before**:

..  code-block:: python

    import numpy as np
    from sgio.core.mesh import SGMesh

    mesh = SGMesh(
        points=np.array([[0,0,0], [1,0,0], [0,1,0]]),
        cells=[("triangle", np.array([[0, 1, 2]]))]
    )
    
    # Manually add IDs
    mesh.point_data['node_id'] = np.array([1, 2, 3])
    mesh.cell_data['element_id'] = [np.array([1])]
    
    sgio.write(sg, 'model.vab', file_format='vabs', renumber_nodes=False)

**After**:

..  code-block:: python

    import numpy as np
    from sgio.core.mesh import SGMesh

    mesh = SGMesh(
        points=np.array([[0,0,0], [1,0,0], [0,1,0]]),
        cells=[("triangle", np.array([[0, 1, 2]]))]
    )
    
    # IDs are automatically generated if missing
    sgio.write(sg, 'model.vab', file_format='vabs')

Scenario 3: Round-Trip Preservation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Before**:

..  code-block:: python

    # Read with arbitrary IDs
    sg1 = sgio.read('model.inp', file_format='abaqus', model_type='SD1', sgdim=3)
    original_ids = sg1.mesh.point_data['node_id'].copy()
    
    # Write back preserving IDs
    sgio.write(sg1, 'output.inp', file_format='abaqus', renumber_nodes=False)
    
    # Verify preservation
    sg2 = sgio.read('output.inp', file_format='abaqus', model_type='SD1', sgdim=3)
    assert (sg2.mesh.point_data['node_id'] == original_ids).all()

**After**:

..  code-block:: python

    # Read with arbitrary IDs
    sg1 = sgio.read('model.inp', file_format='abaqus', model_type='SD1', sgdim=3)
    original_ids = sg1.mesh.point_data['node_id'].copy()
    
    # Write back — automatic preservation (Abaqus allows arbitrary IDs)
    sgio.write(sg1, 'output.inp', file_format='abaqus')
    
    # Verify preservation (still works)
    sg2 = sgio.read('output.inp', file_format='abaqus', model_type='SD1', sgdim=3)
    assert (sg2.mesh.point_data['node_id'] == original_ids).all()

Troubleshooting
---------------

Error: "TypeError: write() got an unexpected keyword argument 'renumber_nodes'"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause**: You're still using the old parameter names.

**Solution**: Remove ``renumber_nodes`` and ``renumber_elements`` from your `write()` calls.

Warning: "UserWarning: Node IDs were automatically renumbered..."
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause**: Your mesh had numbering that didn't comply with the target format requirements.

**Solution**: This is informational — no action needed. The output file is valid.

If you want to suppress the warning:

..  code-block:: python

    import warnings
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        sgio.write(sg, 'output.vab', file_format='vabs')

Mesh IDs Changed After Writing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause**: Writers modify the mesh in-place when renumbering.

**Solution**: Make a copy if you need to preserve original IDs:

..  code-block:: python

    import copy

    sg_copy = copy.deepcopy(sg)
    sgio.write(sg_copy, 'output.vab', file_format='vabs')
    
    # Original sg unchanged, can write with original IDs
    sgio.write(sg, 'output.inp', file_format='abaqus')

Benefits of Automatic Numbering
--------------------------------

1. **Less Code**: No manual validation or renumbering logic
2. **Fewer Errors**: Format requirements enforced automatically
3. **Better DX**: "Just works" for common use cases
4. **Informative**: Warnings tell you when renumbering occurs
5. **Round-Trip Safe**: Preserves IDs when format allows

Further Reading
---------------

- :doc:`io` — Updated I/O guide with automatic numbering examples
- :doc:`../developer/numbering` — Developer guide for implementing readers/writers
- API Reference: :func:`sgio.read`, :func:`sgio.write`
