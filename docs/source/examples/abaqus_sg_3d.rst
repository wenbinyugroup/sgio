Convert Abaqus 3D Solid SG to SwiftComp
========================================

Problem Description
--------------------

Given a 3D solid mesh built in Abaqus (``sg33_cube.inp``), convert it to a
SwiftComp 2.1 input file for 3D solid homogenization using the ``SD1`` model.

Solution
---------

The ``.inp`` file does not state ``sgdim`` or ``model_type``. The script
supplies them in two equivalent ways and asserts that both write the same
SwiftComp input:

1. as arguments of :func:`sgio.convert`;
2. from the SG manifest ``sg33_cube.sg.json`` (see :doc:`/ref/sg_manifest`),
   which references the ``.inp`` file:

.. literalinclude:: ../../../examples/convert_abaqus_sg3d_to_sc/sg33_cube.sg.json
   :language: json

**Python API**

.. literalinclude:: ../../../examples/convert_abaqus_sg3d_to_sc/run.py
   :language: python

**CLI**

.. code-block::

    sgio convert sg33_cube.inp sg33_cube_sc21.sg -ff abaqus -tf swiftcomp -tfv 2.1 -d 3 -m sd1
    sgio convert sg33_cube.sg.json sg33_cube_sc21.sg -ff sg_manifest -tf swiftcomp -tfv 2.1

Result
-------

A SwiftComp 2.1 input file ``sg33_cube_sc21.sg`` is written and ready for homogenization.

File List
----------

* :download:`sg33_cube.inp <../../../examples/convert_abaqus_sg3d_to_sc/sg33_cube.inp>` — Abaqus 3D cube mesh
* :download:`sg33_cube.sg.json <../../../examples/convert_abaqus_sg3d_to_sc/sg33_cube.sg.json>` — SG manifest for the Abaqus input
* :download:`run.py <../../../examples/convert_abaqus_sg3d_to_sc/run.py>` — Python script
