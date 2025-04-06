# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2023 replay file
# Internal Version: 2022_09_28-14.11.55 183150
# Run by tian50 on Sun Feb  9 18:04:22 2025
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=320.866119384766, 
    height=204.733337402344)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=5.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.ConstructionLine(point1=(-0.15, 0.0), point2=(0.125, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
s.ConstructionLine(point1=(0.0, -0.125), point2=(0.0, 0.125))
s.VerticalConstraint(entity=g[3], addUndoState=False)
s.FixedConstraint(entity=g[2])
s.FixedConstraint(entity=g[3])
s.rectangle(point1=(-0.575, 0.35), point2=(0.65, -0.45))
s.rectangle(point1=(-0.35, 0.175), point2=(0.35, -0.25))
s.SymmetryConstraint(entity1=g[4], entity2=g[6], symmetryAxis=g[3])
s.SymmetryConstraint(entity1=g[8], entity2=g[10], symmetryAxis=g[3])
s.SymmetryConstraint(entity1=g[5], entity2=g[7], symmetryAxis=g[2])
#: Warning: Axis of symmetry was selected.
s.SymmetryConstraint(entity1=g[9], entity2=g[11], symmetryAxis=g[2])
s.DistanceDimension(entity1=g[10], entity2=g[6], textPoint=(0.459094643592834, 
    -0.183035671710968), value=0.03)
s.DistanceDimension(entity1=g[11], entity2=g[7], textPoint=(0.318350434303284, 
    0.499999940395355), value=0.03)
s.ObliqueDimension(vertex1=v[1], vertex2=v[2], textPoint=(0.146329402923584, 
    -0.43303570151329), value=0.953)
s.ObliqueDimension(vertex1=v[2], vertex2=v[3], textPoint=(0.655689835548401, 
    0.151785671710968), value=0.53)
session.viewports['Viewport: 1'].view.setValues(width=3.34319, height=1.645, 
    cameraPosition=(-0.0439264, 0.0170089, 4.71405), cameraTarget=(-0.0439264, 
    0.0170089, 0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=2.06185, 
    farPlane=2.3, width=1.28734, height=0.633429, viewOffsetX=0.0327123, 
    viewOffsetY=-0.0048838)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
v1, e, d1 = p.vertices, p.edges, p.datums
p.PartitionFaceByShortestPath(point1=v1[5], point2=v1[0], faces=pickedFaces)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
v2, e1, d2 = p.vertices, p.edges, p.datums
p.PartitionFaceByShortestPath(point1=v2[5], point2=v2[3], faces=pickedFaces)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#2 ]', ), )
v1, e, d1 = p.vertices, p.edges, p.datums
p.PartitionFaceByShortestPath(point1=v1[5], point2=v1[6], faces=pickedFaces)
session.viewports['Viewport: 1'].view.setValues(width=1.374, height=0.67607, 
    viewOffsetX=0.00465724, viewOffsetY=0.0110361)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
v2, e1, d2 = p.vertices, p.edges, p.datums
p.PartitionFaceByShortestPath(point1=v2[5], point2=v2[2], faces=pickedFaces)
session.viewports['Viewport: 1'].view.setValues(nearPlane=2.06105, 
    farPlane=2.3008, width=1.28684, height=0.633183, viewOffsetX=0.0227047, 
    viewOffsetY=0.00545244)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.saveAs(
    pathName='C:/Users/tian50/work/dev/sgio/tests/old/abaqus_cs/box_cus/box_cus')
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\old\abaqus_cs\box_cus\box_cus.cae".
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(
    type=ENGINEERING_CONSTANTS, table=((20590000.0, 1420000.0, 1420000.0, 0.3, 
    0.3, 0.34, 870000.0, 870000.0, 696000.0), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-1', thickness=None)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#f ]', ), )
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#f ]', ), )
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#618 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-2')
mdb.models['Model-1'].parts['Part-1'].MaterialOrientation(region=region, 
    orientationType=DISCRETE, axis=AXIS_3, normalAxisDefinition=VECTOR, 
    normalAxisVector=(0.0, 0.0, 1.0), flipNormalDirection=False, 
    normalAxisDirection=AXIS_3, primaryAxisDefinition=EDGE, 
    primaryAxisRegion=primaryAxisRegion, primaryAxisDirection=AXIS_1, 
    flipPrimaryDirection=True, additionalRotationType=ROTATION_NONE, angle=0.0, 
    additionalRotationField='', stackDirection=STACK_3)
#: Specified material orientation has been assigned to the selected regions.
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\old\abaqus_cs\box_cus\box_cus.cae".
session.viewports['Viewport: 1'].view.setValues(width=1.37403, height=0.676084, 
    viewOffsetX=0.0303279, viewOffsetY=0.00433425)
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=2.06793, 
    farPlane=2.29392, width=1.37355, height=0.675846, viewOffsetX=0.0462801, 
    viewOffsetY=-0.0300518)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    adaptiveMeshConstraints=ON)
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON, 
    adaptiveMeshConstraints=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=ON)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF, mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedRegions = f.getSequenceFromMask(mask=('[#f ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
pickedEdges = e.getSequenceFromMask(mask=('[#c0a ]', ), )
p.seedEdgeByNumber(edges=pickedEdges, number=20, constraint=FINER)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
pickedEdges = e.getSequenceFromMask(mask=('[#c0a ]', ), )
p.seedEdgeByNumber(edges=pickedEdges, number=40, constraint=FINER)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
pickedEdges = e.getSequenceFromMask(mask=('[#c0a ]', ), )
p.seedEdgeByNumber(edges=pickedEdges, number=100, constraint=FINER)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
pickedEdges = e.getSequenceFromMask(mask=('[#2d0 ]', ), )
p.seedEdgeByNumber(edges=pickedEdges, number=50, constraint=FINER)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
pickedEdges = e.getSequenceFromMask(mask=('[#125 ]', ), )
p.seedEdgeByNumber(edges=pickedEdges, number=6, constraint=FINER)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
elemType1 = mesh.ElemType(elemCode=WARP2D4, elemLibrary=STANDARD, 
    secondOrderAccuracy=OFF)
elemType2 = mesh.ElemType(elemCode=WARP2D3, elemLibrary=STANDARD)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#f ]', ), )
pickedRegions =(faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\old\abaqus_cs\box_cus\box_cus.cae".
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='box_cus', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1, 
    multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
mdb.jobs['box_cus'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "box_cus.inp".
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON, mesh=OFF)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=OFF)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p1 = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
mdb.Model(name='Model-2', objectToCopy=mdb.models['Model-1'])
#: The model "Model-2" has been created.
p = mdb.models['Model-2'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-2'].parts['Part-1'].sectionAssignments[0]
del mdb.models['Model-2'].parts['Part-1'].materialOrientations[0]
session.viewports['Viewport: 1'].view.setValues(nearPlane=2.06064, 
    farPlane=2.30121, width=1.46203, height=0.719382, viewOffsetX=0.0698545, 
    viewOffsetY=-0.0120985)
session.viewports['Viewport: 1'].view.setValues(nearPlane=1.8437, 
    farPlane=2.538, width=1.30811, height=0.64365, cameraPosition=(0.463104, 
    0.97425, 1.90692), cameraUpVector=(-0.160532, 0.892126, -0.422304), 
    cameraTarget=(0.000607342, -0.00506214, 0.0139091), viewOffsetX=0.0625006, 
    viewOffsetY=-0.0108248)
session.viewports['Viewport: 1'].view.setValues(nearPlane=1.83381, 
    farPlane=2.55591, width=1.30109, height=0.640196, cameraPosition=(0.582254, 
    0.978417, 1.8765), cameraUpVector=(-0.172725, 0.892058, -0.41761), 
    cameraTarget=(0.00214495, -0.00403417, 0.0178101), viewOffsetX=0.0621652, 
    viewOffsetY=-0.0107667)
session.viewports['Viewport: 1'].view.setValues(nearPlane=1.748, 
    farPlane=2.66485, width=1.24021, height=0.610238, cameraPosition=(0.945413, 
    1.15371, 1.62599), cameraUpVector=(-0.279399, 0.848078, -0.450223), 
    cameraTarget=(0.00969288, -0.00164581, 0.0303515), viewOffsetX=0.0592562, 
    viewOffsetY=-0.0102629)
session.viewports['Viewport: 1'].view.setValues(nearPlane=1.80522, 
    farPlane=2.59639, width=1.28081, height=0.630213, cameraPosition=(0.757917, 
    1.00106, 1.80758), cameraUpVector=(-0.242536, 0.884789, -0.397901), 
    cameraTarget=(0.00448214, -0.00659132, 0.0261584), viewOffsetX=0.0611958, 
    viewOffsetY=-0.0105988)
layupOrientation = None
p = mdb.models['Model-2'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#f ]', ), )
region1 = regionToolset.Region(faces=faces)
p = mdb.models['Model-2'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#618 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-10')
compositeLayup = mdb.models['Model-2'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-1', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='Material-1', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=15.0, 
    additionalRotationType=ROTATION_NONE, additionalRotationField='', 
    axis=AXIS_3, angle=0.0, numIntPoints=1)
compositeLayup.ReferenceOrientation(orientationType=DISCRETE, localCsys=None, 
    additionalRotationType=ROTATION_NONE, angle=0.0, 
    additionalRotationField='', axis=AXIS_2, stackDirection=STACK_3, 
    normalAxisDefinition=VECTOR, normalAxisVector=(0.0, 0.0, 1.0), 
    normalAxisDirection=AXIS_3, flipNormalDirection=False, 
    primaryAxisDefinition=EDGE, primaryAxisRegion=primaryAxisRegion, 
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=True)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\old\abaqus_cs\box_cus\box_cus.cae".
a = mdb.models['Model-2'].rootAssembly
a.regenerate()
a = mdb.models['Model-2'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].view.setValues(nearPlane=2.03706, 
    farPlane=2.32479, width=1.74722, height=0.85971, viewOffsetX=0.0614408, 
    viewOffsetY=-0.0108393)
mdb.Job(name='box_cus_comp', model='Model-2', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1, 
    multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
mdb.jobs['box_cus_comp'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "box_cus_comp.inp".
p1 = mdb.models['Model-2'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
session.viewports['Viewport: 1'].view.setValues(nearPlane=1.67294, 
    farPlane=2.74864, width=1.18696, height=0.584037, cameraPosition=(1.11026, 
    1.54779, 1.12295), cameraUpVector=(-0.586202, 0.696844, -0.41325), 
    cameraTarget=(0.0230693, -0.00575966, 0.0454517), viewOffsetX=0.0567117, 
    viewOffsetY=-0.00982217)
layupOrientation = None
p = mdb.models['Model-2'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#f ]', ), )
region1 = regionToolset.Region(faces=faces)
compositeLayup = mdb.models['Model-2'].parts['Part-1'].compositeLayups['CompositeLayup-1']
compositeLayup.orientation.setValues(additionalRotationType=ROTATION_ANGLE, 
    angle=15.0, additionalRotationField='')
compositeLayup.deletePlies()
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='Material-1', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=0.0, 
    additionalRotationType=ROTATION_NONE, additionalRotationField='', 
    axis=AXIS_3, angle=0.0, numIntPoints=1)
a = mdb.models['Model-2'].rootAssembly
a.regenerate()
session.viewports['Viewport: 1'].setValues(displayedObject=a)
mdb.jobs['box_cus_comp'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "box_cus_comp.inp".
p = mdb.models['Model-2'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].view.setValues(nearPlane=2.0166, 
    farPlane=2.34525, width=1.99461, height=0.981439, viewOffsetX=0.209626, 
    viewOffsetY=-0.0440668)
p1 = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
p1 = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
session.viewports['Viewport: 1'].view.setValues(nearPlane=2.05795, 
    farPlane=2.3039, width=1.49387, height=0.735051, viewOffsetX=0.0138807, 
    viewOffsetY=-0.0134541)
p1 = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\old\abaqus_cs\box_cus\box_cus.cae".
