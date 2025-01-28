Read Structural Model Data (.k file)
=====================================

To get the data (effective properties) from the output file (.k), use the :func:`sgio.readOutputModel` function.

..  code-block::

    import sgio

    model = sgio.readOutputModel(
        file_name,    # Name of the output file.
        file_format,  # Format of the output file.
        model_type,   # Type of the structural model.
    )

``file_name`` includes the ``.k`` extension.
``file_format`` can be 'vabs' for VABS output or 'sc'/'swiftcomp' for SwiftComp output.
``model_type`` should be chosen from a list of built-in keywords indicating the type of the structural model.
See Section :ref:`guide_model` for more details.

The function returns a structural model (:ref:`ref_model`).



Get Timoshenko Beam Properties from a VABS Output File
-----------------------------------------------------------

Consider the following VABS output file (``sgio/examples/files/cs_box_t_vabs41.sg.K``):

..  literalinclude:: ../../../examples/files/sg21eb_tri3_vabs40.sg.K
    :language: text

The following code (``sgio/examples/read_vabs_output_h.py``) shows how to read the output file and get some Timoshenko beam properties:

..  literalinclude:: ../../../examples/read_vabs_output_h.py
    :language: python

The output should be:

..  code-block:: text

    EA = 1653700.125
    GJ = 6322.4210975
    EI22 = 79466.796504
    EI33 = 200742.66655

Checkout :func:`sgio.model.TimoshenkoBeamModel.get` for more information on the properties that can be retrieved.
