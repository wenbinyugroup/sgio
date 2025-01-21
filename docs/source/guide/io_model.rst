Read Structural Model Data (.k file)
=====================================

To get the data (effective properties) from the output file (.k), use the `readOutput` function.

..  code-block::

    import sgio

    model = sgio.readOutput()

The function returns a beam model (:ref:`ref_model_beam`).
