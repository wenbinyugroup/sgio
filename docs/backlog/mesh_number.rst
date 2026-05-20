
Automatic Node and Element Numbering
--------------------------------------

SGIO automatically handles node and element numbering to ensure compatibility with each file format.

How It Works
^^^^^^^^^^^^

Different formats have different numbering requirements:

- **VABS** and **SwiftComp**: Require consecutive numbering starting from 1 (1, 2, 3, ...)
- **Abaqus**: Allows arbitrary numbering (10, 50, 100, ...) but must start from 1
- **Gmsh**: Uses format-specific entity tags

SGIO automatically:

1. **Reads** files preserving original numbering
2. **Converts** between formats automatically renumbering when needed
3. **Warns** you when renumbering occurs (via Python warning)
4. **Preserves** original numbering for round-trip conversions

Format Conversion Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Abaqus → VABS** (automatic renumbering):

..  code-block:: python

    import sgio

    # Read Abaqus with arbitrary node IDs [10, 50, 100]
    sg = sgio.read('model.inp', file_format='abaqus', model_type='BM2')
    
    # Write to VABS (automatically renumbers to [1, 2, 3])
    sgio.write(sg, 'model.vab', file_format='vabs')
    # Warning: Node IDs were automatically renumbered to meet VABS format requirements

**VABS → Abaqus** (preserves sequential):

..  code-block:: python

    import sgio

    # Read VABS with sequential IDs [1, 2, 3]
    sg = sgio.read('model.vab', file_format='vabs', model_type='BM2')
    
    # Write to Abaqus (no renumbering needed)
    sgio.write(sg, 'model.inp', file_format='abaqus')
    # No warning - IDs already comply

**Abaqus → Abaqus** (round-trip preservation):

..  code-block:: python

    import sgio

    # Read Abaqus with arbitrary IDs [10, 50, 100]
    sg = sgio.read('input.inp', file_format='abaqus', model_type='SD1', sgdim=3)
    
    # Write back to Abaqus (preserves original IDs)
    sgio.write(sg, 'output.inp', file_format='abaqus')
    # No renumbering - original IDs preserved

Understanding Warnings
^^^^^^^^^^^^^^^^^^^^^^

You may see warnings like:

..  code-block:: text

    UserWarning: Node IDs were automatically renumbered to meet VABS format 
    requirements (consecutive numbering starting from 1). 
    Original IDs: [10, 50, 100] → New IDs: [1, 2, 3].

**What this means:**

- Your mesh had numbering that didn't match the target format requirements
- SGIO automatically fixed it for you
- The warning is informational — no action needed
- Output file is valid and ready to use

**When warnings appear:**

- Converting between formats with different requirements (Abaqus → VABS/SwiftComp)
- Writing programmatically-created meshes without proper IDs
- Modifying mesh numbering after reading

**No warning when:**

- IDs already comply with target format
- Round-trip within same format (VABS → VABS, Abaqus → Abaqus)
- All IDs are sequential 1-based

Migration from Old API
^^^^^^^^^^^^^^^^^^^^^^

If you used the old ``renumber_nodes`` or ``renumber_elements`` parameters:

..  code-block:: python

    # Old API (no longer supported)
    sgio.write(sg, 'output.vab', 'vabs', renumber_nodes=True)  # ERROR

    # New API (automatic)
    sgio.write(sg, 'output.vab', file_format='vabs')  # Automatic renumbering

Simply remove the ``renumber_nodes`` and ``renumber_elements`` parameters. 
Numbering is now fully automatic based on format requirements.

For more details, see :doc:`../developer/numbering` (Developer Guide).
