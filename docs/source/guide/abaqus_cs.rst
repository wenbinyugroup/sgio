Build Cross-section in Abaqus and Export to VABS
================================================

Brief Instruction
--------------------------

Overall, the process is similar to create a plane strain or meshed beam cross-section part.

* Part:

  * Modeling space: 2D planar
  * Type: Deformable
  * Base feature: Shell

* Material: Any
* Section: Composite layup (Solid, Homogeneous)
* Mesh: Any


Detailed Instruction
--------------------------

Part
^^^^^^

..  figure:: /images/abaqus_cs_create_part.png
    :align: center
    :width: 200

..  figure:: /images/abaqus_cs_partition_face.png
    :align: center
    :width: 500


Property
^^^^^^^^

..  figure:: /images/abaqus_cs_comp_section.png
    :align: center
    :width: 800

..  figure:: /images/abaqus_cs_solid_section.png
    :align: center
    :width: 500


Mesh
^^^^

..  figure:: /images/abaqus_cs_mesh.png
    :align: center
    :width: 700


Generate INP file and Convert to VABS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
