Convert Abaqus 3D Solid SG to SwiftComp
========================================

Problem Description
--------------------

Given a 3D solid mesh built in Abaqus (``sg33_cube.inp``), convert it to a
SwiftComp 2.1 input file for 3D solid homogenization using the ``SD1`` model.

Solution
---------

The ``.inp`` file does not state ``sgdim`` or ``model_type``. There are two
ways to supply them, one script each; both write the same SwiftComp input.

Method 1: API arguments
~~~~~~~~~~~~~~~~~~~~~~~~

The SG parameters are arguments of :func:`sgio.convert`.

.. literalinclude:: ../../../examples/convert_abaqus_sg3d_to_sc/run_1_api.py
   :language: python

On the command line:

.. code-block::

    sgio convert sg33_cube.inp sg33_cube_sc21.sg -ff abaqus -tf swiftcomp -tfv 2.1 -d 3 -m sd1

Method 2: SG manifest
~~~~~~~~~~~~~~~~~~~~~~

``sg33_cube.sg.json`` (see :doc:`/ref/sg_manifest`) references the ``.inp``
file and holds the same parameters, so the conversion takes no SG arguments:

.. literalinclude:: ../../../examples/convert_abaqus_sg3d_to_sc/sg33_cube.sg.json
   :language: json

.. literalinclude:: ../../../examples/convert_abaqus_sg3d_to_sc/run_2_manifest.py
   :language: python

On the command line:

.. code-block::

    sgio convert sg33_cube.sg.json sg33_cube_sc21.sg -ff sg_manifest -tf swiftcomp -tfv 2.1

Result
-------

A SwiftComp 2.1 input file ``sg33_cube_sc21.sg`` is written and ready for homogenization.

File List
----------

* :download:`sg33_cube.inp <../../../examples/convert_abaqus_sg3d_to_sc/sg33_cube.inp>` — Abaqus 3D cube mesh
* :download:`sg33_cube.sg.json <../../../examples/convert_abaqus_sg3d_to_sc/sg33_cube.sg.json>` — SG manifest for the Abaqus input
* :download:`run_1_api.py <../../../examples/convert_abaqus_sg3d_to_sc/run_1_api.py>` — conversion with SG arguments
* :download:`run_2_manifest.py <../../../examples/convert_abaqus_sg3d_to_sc/run_2_manifest.py>` — conversion through the SG manifest
