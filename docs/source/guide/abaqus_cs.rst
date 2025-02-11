Build Cross-section in Abaqus and Export to VABS
================================================

Brief Instruction
--------------------------

Overall, the process is similar to creating a plane strain or meshed beam cross-section part.

* Part:

  * Modeling space: 2D planar
  * Type: Deformable
  * Base feature: Shell

* Property:

  * Material: Any
  * Section: Composite layup (Solid, Homogeneous)

* Mesh: Any

Write the Abaqus model to an INP file.

Convert the INP file to a VABS input file using the command:

..  code-block:: bash

    sgio convert <filename>.inp <filename>.sg -ff abaqus -tf vabs


Detailed Instruction
--------------------------

Part module
^^^^^^^^^^^

As a cross-section of a slender structure, it is natural to create a "Deformable" "Shell" part in the "2D Planar" modeling space.

.. (See Figure :ref:`fig-abaqus-cs-part`)

..  figure:: /images/abaqus_cs_create_part.png
    :name: fig-abaqus-cs-part
    :align: center
    :width: 200

Composite structures can have different materials in different regions.
A useful tip is to create a base shape, such as a circle, large enough to cover the entire cross-section.
Then, use the "Partition Face" tool to divide the base shape into regions.

..  figure:: /images/abaqus_cs_partition_face.png
    :align: center
    :width: 500


Property
^^^^^^^^

Any type of material can be used for the cross-section, such as isotropic, engineering constants, or orthotropic.
VABS requires local orientation data and allows additional in-plane rotations (fiber angle) for each layer.
Hence, it is needed to use the "Composite Layup" section type.
However, each section is only used for one ply.
The layer orientation is defined by assigning the local :math:`y` axis, while the local :math:`x` axis is always normal to the cross-sectional plane.
For a composite layer, it is usually set to be tangent to a base line.
To set the fiber angle for each layer, use the column "Rotation Angle".

..  figure:: /images/abaqus_cs_comp_section.png
    :align: center
    :width: 800

It is okay to use the "Composite Layup" section for all materials.
However, if a material is isotropic and no local orientation and fiber angle are needed, then it is acceptable to use the "Solid" section.

..  figure:: /images/abaqus_cs_solid_section.png
    :align: center
    :width: 500


Mesh
^^^^

There is no restriction on meshing.

..  figure:: /images/abaqus_cs_mesh.png
    :align: center
    :width: 700


