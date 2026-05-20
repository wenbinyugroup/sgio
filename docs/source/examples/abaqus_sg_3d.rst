Convert Abaqus 3D Solid SG to SwiftComp
========================================

Problem Description
--------------------

Given a 3D solid mesh built in Abaqus (``sg33_cube.inp``), convert it to a
SwiftComp 2.1 input file for 3D solid homogenization using the ``sd1`` model.

Solution
---------

**Python API**

.. code-block:: python

   import sgio

   sg = sgio.read(
       'sg33_cube.inp',
       'abaqus',
       model_type='sd1',
       sgdim=3,
   )

   sgio.write(
       sg=sg,
       fn='sg33_cube_sc21.sg',
       file_format='sc',
       format_version='2.1',
       model_type='sd1',
   )

**CLI**

.. code-block::

    sgio convert sg33_cube.inp sg33_cube.sg -ff abaqus -tf swiftcomp -tfv 2.1 -m sd1

Result
-------

A SwiftComp 2.1 input file ``sg33_cube_sc21.sg`` is written and ready for homogenization.

File List
----------

* :download:`sg33_cube.inp <../../../examples/convert_abaqus_sg3d_to_sc/sg33_cube.inp>` — Abaqus 3D cube mesh
* :download:`run.py <../../../examples/convert_abaqus_sg3d_to_sc/run.py>` — Python script

