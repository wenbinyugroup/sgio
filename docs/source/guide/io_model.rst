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



Examples
--------


Get Euler-Bernoulli beam properties from a VABS output file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Consider the following VABS output file (``sgio/examples/read_vabs_output_k/sg21eb_tri3_vabs40.sg.K``):

..  literalinclude:: ../../../examples/read_vabs_output_k/sg21eb_tri3_vabs40.sg.K
    :language: text

The following code shows how to read the output file and get some Euler-Bernoulli beam properties:

..  code-block::

    import sgio

    model = sgio.readOutputModel(
        'sg21eb_tri3_vabs40.sg.K',  # Name of the output file.
        'vabs',           # Format of the output file.
        'BM1',     # Type of the structural model.
    )

    ea = model.get('ea')

Checkout :func:`sgio.model.EulerBernoulliBeamModel.get` for more information on the properties that can be retrieved.
