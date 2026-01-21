# Gmsh 4.15.0

The MSH file format version 4 (current revision: version 4.1) contains one mandatory section giving information about the file (`$MeshFormat`), followed by several optional sections defining the physical group names (`$PhysicalName`), the elementary model entities (`$Entities`), the partitioned entities (`$PartitionedEntities`), the nodes (`$Nodes`), the elements (`$Elements`), the periodicity relations (`$Periodic`), the ghost elements (`$GhostElements`), the parametrizations (`$Parametrizations`) and the post-processing datasets (`$NodeData`, `$ElementData`, `$ElementNodeData`). The sections reflect the underlying Gmsh data model: `$Entities` store the boundary representation of the model geometrical entities, `$Nodes` and `$Elements` store mesh data classified on these entities, and `$NodeData`, `$ElementData`, `$ElementNodeData` store post-processing data (views). (See [Gmsh application programming interface](https://gmsh.info/doc/texinfo/#Gmsh-application-programming-interface) and [Source code structure](https://gmsh.info/doc/texinfo/#Source-code-structure) for a more detailed description of the internal Gmsh data model.)

To represent a simple mesh, the minimal sections that should be present in the file are `$MeshFormat`, `$Nodes` and `$Elements`. Nodes are assumed to be defined before elements. To represent a mesh with the full topology (BRep) of the model and associated physical groups, an `$Entities` section should be present before the `$Nodes` section. Sections can be repeated in the same file, and post-processing sections can be put into separate files (e.g. one file per time step). Any section with an unrecognized header is stored by default as a model attribute: you can thus e.g. add comments in a .msh file by putting them inside a `$Comments`/`$EndComments` section. Unrocognized sections can be ignored altogether if the `Mesh.IgnoreUnknownSections` option is set.

All the node, element, entity and physical group tags (their global identification numbers) should be strictly positive. (Tag `0` is reserved for internal use.) Important note about efficiency: tags can be "sparse", i.e., do not have to constitute a continuous list of numbers (the format even allows them to not be ordered). However, using sparse node or element tags can lead to performance degradation. For meshes, sparse indexing can[<sup>15</sup>](https://gmsh.info/doc/texinfo/#FOOT15) force Gmsh to use a map instead of a vector to access nodes and elements. The performance hit is on speed. For post-processing datasets, which always use vectors to access data, the performance hit is on memory. A `$NodeData` with two nodes, tagged 1 and 1000000, will allocate a (mostly empty) vector of 1000000 elements. By default, for non-partitioned, single file meshes, Gmsh will create files with a continuous ordering of node and element tags, starting at 1. Detecting if the numbering is continuous can be done easily when reading a file by inspecting `numNodes`, `minNodeTag` and `maxNodeTag` in the `$Nodes` section; and `numElements`, `minElementTag` and `maxElementTag` in the `$Elements` section.

In binary mode (`Mesh.Binary=1` or `-bin` on the command line), all the numerical values (integer and floating point) not marked as ASCII in the format description below are written in binary form, using the type given between parentheses. The block structure of the `$Nodes` and `$Elements` sections allows to read integer and floating point data in each block in a single step (e.g. using `fread` in C).

The format is defined as follows:
```
$MeshFormat // same as MSH version 2
  version(ASCII double; currently 4.1)
    file-type(ASCII int; 0 for ASCII mode, 1 for binary mode)
    data-size(ASCII int; sizeof(size\_t))
  < int with value one; only in binary mode, to detect endianness >
$EndMeshFormat

$PhysicalNames // same as MSH version 2
  numPhysicalNames(ASCII int)
  dimension(ASCII int) physicalTag(ASCII int) "name"(127 characters max)
  ...
$EndPhysicalNames

$Entities
  numPoints(size\_t) numCurves(size\_t)
    numSurfaces(size\_t) numVolumes(size\_t)
  pointTag(int) X(double) Y(double) Z(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
  ...
  curveTag(int) minX(double) minY(double) minZ(double)
    maxX(double) maxY(double) maxZ(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
    numBoundingPoints(size\_t) pointTag(int; sign encodes orientation) ...
  ...
  surfaceTag(int) minX(double) minY(double) minZ(double)
    maxX(double) maxY(double) maxZ(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
    numBoundingCurves(size\_t) curveTag(int; sign encodes orientation) ...
  ...
  volumeTag(int) minX(double) minY(double) minZ(double)
    maxX(double) maxY(double) maxZ(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
    numBoundngSurfaces(size\_t) surfaceTag(int; sign encodes orientation) ...
  ...
$EndEntities

$PartitionedEntities
  numPartitions(size\_t)
  numGhostEntities(size\_t)
    ghostEntityTag(int) partition(int)
    ...
  numPoints(size\_t) numCurves(size\_t)
    numSurfaces(size\_t) numVolumes(size\_t)
  pointTag(int) parentDim(int) parentTag(int)
    numPartitions(size\_t) partitionTag(int) ...
    X(double) Y(double) Z(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
  ...
  curveTag(int) parentDim(int) parentTag(int)
    numPartitions(size\_t) partitionTag(int) ...
    minX(double) minY(double) minZ(double)
    maxX(double) maxY(double) maxZ(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
    numBoundingPoints(size\_t) pointTag(int) ...
  ...
  surfaceTag(int) parentDim(int) parentTag(int)
    numPartitions(size\_t) partitionTag(int) ...
    minX(double) minY(double) minZ(double)
    maxX(double) maxY(double) maxZ(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
    numBoundingCurves(size\_t) curveTag(int) ...
  ...
  volumeTag(int) parentDim(int) parentTag(int)
    numPartitions(size\_t) partitionTag(int) ...
    minX(double) minY(double) minZ(double)
    maxX(double) maxY(double) maxZ(double)
    numPhysicalTags(size\_t) physicalTag(int) ...
    numBoundingSurfaces(size\_t) surfaceTag(int) ...
  ...
$EndPartitionedEntities

$Nodes
  numEntityBlocks(size\_t) numNodes(size\_t)
    minNodeTag(size\_t) maxNodeTag(size\_t)
  entityDim(int) entityTag(int) parametric(int; 0 or 1)
    numNodesInBlock(size\_t)
    nodeTag(size\_t)
    ...
    x(double) y(double) z(double)
       < u(double; if parametric and entityDim >= 1) >
       < v(double; if parametric and entityDim >= 2) >
       < w(double; if parametric and entityDim == 3) >
    ...
  ...
$EndNodes

$Elements
  numEntityBlocks(size\_t) numElements(size\_t)
    minElementTag(size\_t) maxElementTag(size\_t)
  entityDim(int) entityTag(int) elementType(int; see below)
    numElementsInBlock(size\_t)
    elementTag(size\_t) nodeTag(size\_t) ...
    ...
  ...
$EndElements

$Periodic
  numPeriodicLinks(size\_t)
  entityDim(int) entityTag(int) entityTagMaster(int)
  numAffine(size\_t) value(double) ...
  numCorrespondingNodes(size\_t)
    nodeTag(size\_t) nodeTagMaster(size\_t)
    ...
  ...
$EndPeriodic

$GhostElements
  numGhostElements(size\_t)
  elementTag(size\_t) partitionTag(int)
    numGhostPartitions(size\_t) ghostPartitionTag(int) ...
  ...
$EndGhostElements

$Parametrizations
  numCurveParam(size\_t) numSurfaceParam(size\_t)
  curveTag(int) numNodes(size\_t)
    nodeX(double) nodeY(double) nodeZ(double) nodeU(double)
    ...
  ...
  surfaceTag(int) numNodes(size\_t) numTriangles(size\_t)
    nodeX(double) nodeY(double) nodeZ(double)
      nodeU(double) nodeV(double)
      curvMaxX(double) curvMaxY(double) curvMaxZ(double)
      curvMinX(double) curvMinY(double) curvMinZ(double)
    ...
    nodeIndex1(int) nodeIndex2(int) nodeIndex3(int)
    ...
  ...
$EndParametrizations

$NodeData
  numStringTags(ASCII int)
  stringTag(string) ...
  numRealTags(ASCII int)
  realTag(ASCII double) ...
  numIntegerTags(ASCII int)
  integerTag(ASCII int) ...
  nodeTag(int) value(double) ...
  ...
$EndNodeData

$ElementData
  numStringTags(ASCII int)
  stringTag(string) ...
  numRealTags(ASCII int)
  realTag(ASCII double) ...
  numIntegerTags(ASCII int)
  integerTag(ASCII int) ...
  elementTag(int) value(double) ...
  ...
$EndElementData

$ElementNodeData
  numStringTags(ASCII int)
  stringTag(string) ...
  numRealTags(ASCII int)
  realTag(ASCII double) ...
  numIntegerTags(ASCII int)
  integerTag(ASCII int) ...
  elementTag(int) numNodesPerElement(int) value(double) ...
  ...
$EndElementNodeData

$InterpolationScheme
  name(string)
  numElementTopologies(ASCII int)
  elementTopology
  numInterpolationMatrices(ASCII int)
  numRows(ASCII int) numColumns(ASCII int) value(ASCII double) ...
$EndInterpolationScheme
```

In the format description above, `elementType` is e.g.:

- `1`: 2-node line.
- `2`: 3-node triangle.
- `3`: 4-node quadrangle.
- `4`: 4-node tetrahedron.
- `5`: 8-node hexahedron.
- `6`: 6-node prism.
- `7`: 5-node pyramid.
- `8`: 3-node second order line (2 nodes associated with the vertices and 1 with the edge).
- `9`: 6-node second order triangle (3 nodes associated with the vertices and 3 with the edges).
- `10`: 9-node second order quadrangle (4 nodes associated with the vertices, 4 with the edges and 1 with the face).
- `11`: 10-node second order tetrahedron (4 nodes associated with the vertices and 6 with the edges).
- `12`: 27-node second order hexahedron (8 nodes associated with the vertices, 12 with the edges, 6 with the faces and 1 with the volume).
- `13`: 18-node second order prism (6 nodes associated with the vertices, 9 with the edges and 3 with the quadrangular faces).
- `14`: 14-node second order pyramid (5 nodes associated with the vertices, 8 with the edges and 1 with the quadrangular face).
- `15`: 1-node point.
- `16`: 8-node second order quadrangle (4 nodes associated with the vertices and 4 with the edges).
- `17`: 20-node second order hexahedron (8 nodes associated with the vertices and 12 with the edges).
- `18`: 15-node second order prism (6 nodes associated with the vertices and 9 with the edges).
- `19`: 13-node second order pyramid (5 nodes associated with the vertices and 8 with the edges).
- `20`: 9-node third order incomplete triangle (3 nodes associated with the vertices, 6 with the edges)
- `21`: 10-node third order triangle (3 nodes associated with the vertices, 6 with the edges, 1 with the face)
- `22`: 12-node fourth order incomplete triangle (3 nodes associated with the vertices, 9 with the edges)
- `23`: 15-node fourth order triangle (3 nodes associated with the vertices, 9 with the edges, 3 with the face)
- `24`: 15-node fifth order incomplete triangle (3 nodes associated with the vertices, 12 with the edges)
- `25`: 21-node fifth order complete triangle (3 nodes associated with the vertices, 12 with the edges, 6 with the face)
- `26`: 4-node third order edge (2 nodes associated with the vertices, 2 internal to the edge)
- `27`: 5-node fourth order edge (2 nodes associated with the vertices, 3 internal to the edge)
- `28`: 6-node fifth order edge (2 nodes associated with the vertices, 4 internal to the edge)
- `29`: 20-node third order tetrahedron (4 nodes associated with the vertices, 12 with the edges, 4 with the faces)
- `30`: 35-node fourth order tetrahedron (4 nodes associated with the vertices, 18 with the edges, 12 with the faces, 1 in the volume)
- `31`: 56-node fifth order tetrahedron (4 nodes associated with the vertices, 24 with the edges, 24 with the faces, 4 in the volume)
- `92`: 64-node third order hexahedron (8 nodes associated with the vertices, 24 with the edges, 24 with the faces, 8 in the volume)
- `93`: 125-node fourth order hexahedron (8 nodes associated with the vertices, 36 with the edges, 54 with the faces, 27 in the volume)


All the currently supported elements in the format are defined in [GmshDefines.h](https://gitlab.onelab.info/gmsh/gmsh/blob/master/src/common/GmshDefines.h). See [Node ordering](https://gmsh.info/doc/texinfo/#Node-ordering) for the ordering of the nodes.

The post-processing sections (`$NodeData`, `$ElementData`, `$ElementNodeData`) can contain `numStringTags` string tags, `numRealTags` real value tags and `numIntegerTags` integer tags. The default set of tags understood by Gmsh is as follows:

`stringTag`
    The first is interpreted as the name of the post-processing view and the second as the name of the interpolation scheme, as provided in the `$InterpolationScheme` section.

`realTag`
    The first is interpreted as a time value associated with the dataset.

`integerTag`
    The first is interpreted as a time step index (starting at 0), the second as the number of field components of the data in the view (1, 3 or 9), the third as the number of entities (nodes or elements) in the view, and the fourth as the partition index for the view data (0 for no partition).

In the `$InterpolationScheme` section:

`numElementTopologies`
    is the number of element topologies for which interpolation matrices are provided.

`elementTopology`
    is the id tag of a given element topology: 1 for points, 2 for lines, 3 for triangles, 4 for quadrangles, 5 for tetrahedra, 6 for pyramids, 7 for prisms, 8 for hexahedra, 9 for polygons and 10 for polyhedra.

`numInterpolationMatrices`
    is the number of interpolation matrices provided for the given element topology. Currently you should provide 2 matrices, i.e., the matrices that specify how to interpolate the data (they have the same meaning as in [Post-processing scripting commands](https://gmsh.info/doc/texinfo/#Post_002dprocessing-scripting-commands)). The matrices are specified by 2 integers (`numRows` and `numColumns`) followed by the values, by row.

Here is a small example of a minimal ASCII MSH4.1 file, with a mesh consisting of two quadrangles and an associated nodal scalar dataset (the comments are not part of the actual file):
```
$MeshFormat
4.1 0 8     *MSH4.1, ASCII*
$EndMeshFormat
$Nodes
1 6 1 6     *1 entity bloc, 6 nodes total, min/max node tags: 1 and 6*
2 1 0 6     *2D entity (surface) 1, no parametric coordinates, 6 nodes*
1           *  node tag #1*
2           *  node tag #2*
3           *  etc.*
4
5
6
0. 0. 0.    *  node #1 coordinates (0., 0., 0.)*
1. 0. 0.    *  node #2 coordinates (1., 0., 0.)*
1. 1. 0.    *  etc.*
0. 1. 0.
2. 0. 0.
2. 1. 0.
$EndNodes
$Elements
1 2 1 2     *1 entity bloc, 2 elements total, min/max element tags: 1 and 2*
2 1 3 2     *2D entity (surface) 1, element type 3 (4-node quad), 2 elements*
1 1 2 3 4   *  quad tag #1, nodes 1 2 3 4*
2 2 5 6 3   *  quad tag #2, nodes 2 5 6 3*
$EndElements
$NodeData
1           *1 string tag:*
"My view"   *  the name of the view ("My view")*
1           *1 real tag:*
0.0         *  the time value (0.0)*
3           *3 integer tags:*
0           *  the time step (0; time steps always start at 0)*
1           *  1-component (scalar) field*
6           *  6 associated nodal values*
1 0.0       *value associated with node #1 (0.0)*
2 0.1       *value associated with node #2 (0.1)*
3 0.2       *etc.*
4 0.0
5 0.2
6 0.4
$EndNodeData
```