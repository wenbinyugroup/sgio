Read and Write SG Data
===========================


Read SG data
--------------

..  code-block::

    import sgio

    sg = sgio.read(
        filename,  # Name of the SG file.
        format, # Format of the SG data. See doc for more info.
        version, # Version of the data format. See doc for more info.
        sgdim, # Dimension of the SG.
        smdim, # Dimension of the structural model.
    )



Write SG data
----------------

..  code-block::

    import sgio

    sgio.write(
        sg,  # SG data
        filename,  # Name of the SG file.
        format, # Format of the SG data. See doc for more info.
        version, # Version of the data format. See doc for more info.
        analysis, # Type of SG analysis. See doc for more info.
    )



Read mesh data
------------------

..  code-block::

    import sgio

    sg = sgio.read(
        filename,  # Name of the SG file.
        format, # Format of the SG data. See doc for more info.
        version, # Version of the data format. See doc for more info.
        sgdim, # Dimension of the SG.
        smdim, # Dimension of the structural model.
        mesh_only=True
    )

Users can also directly use `meshio` functions to read mesh data:

..  code-block::

    import sgio.meshio as meshio

    mesh = meshio.read(
        ... # See meshio doc for instructions.
    )


Write mesh data
-------------------

..  code-block::

    import sgio

    sgio.write(
        sg,  # SG data
        filename,  # Name of the SG file.
        format, # Format of the SG data. See doc for more info.
        version, # Version of the data format. See doc for more info.
        mesh_only=True
    )

Users can also directly use `meshio` functions to write mesh data:

..  code-block::

    # Create an SG object first
    # either from reading a file or manually

    sg.mesh.write(
        ... # See meshio doc for instructions.
    )


Supported formats and data
-----------------------------

All formats supported by meshio are also supported by sgio.
However, not all of those formats can store the complete SG data.

Formats that can be used for complete SG data:

* VABS
* SwiftComp
* Abaqus

Formats that could be used for complete SG data:

* ANSYS

These formats will be developed for complete SG data in the future.
