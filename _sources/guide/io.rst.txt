Read and Write SG Data
===========================



Read SG data
--------------

To read SG data from a file, use the :func:`sgio.read` function.

..  code-block::

    import sgio

    sg = sgio.read(
        file_name,
        file_format,
        model_type,
        sgdim,
    )

``file_name`` is the name of the SG file to be read.
``file_format`` is the format of the SG file.
It can be 'vabs' for VABS, 'sc' or 'swiftcomp' for SwiftComp.
``model_type`` is the type of the SG model.
``sgdim`` is the dimension of the SG data.
It can be 1, 2, or 3.
For VABS, the SG is a cross-section, so the dimension is 2, which can be omitted.

The function returns a :class:`sgio.StructureGene` object.


For Meshing Data Only
^^^^^^^^^^^^^^^^^^^^^

..  code-block::

    import sgio

    sg = sgio.read(
        file_name,
        file_format,
        model_type,
        sgdim,
        mesh_only=True
    )

Users can also directly use ``meshio`` functions to read mesh data:

..  code-block::

    import sgio.meshio as meshio

    mesh = meshio.read(
        ... # See meshio doc for instructions.
    )



Write SG data
----------------

Use the :func:`sgio.write` function.

..  code-block::

    import sgio

    sgio.write(
        sg,
        file_name,
        file_format,
        version,
        analysis,
    )


For Meshing Data Only
^^^^^^^^^^^^^^^^^^^^^

..  code-block::

    import sgio

    sgio.write(
        sg,
        file_name,
        file_format,
        version,
        mesh_only=True
    )

Users can also directly use ``meshio`` functions to write mesh data:

..  code-block::

    # Create an SG object first
    # either from reading a file or manually

    sg.mesh.write(
        ... # See meshio doc for instructions.
    )



Supported Data Formats
-----------------------

``mehsio`` supports a wide range of formats.
However, not all of those formats can store the complete SG data and be supported by ``sgio``.

Formats that can be used for complete SG data:

* VABS
* SwiftComp
* Abaqus

Other formats will be developed for complete SG data in the future.
