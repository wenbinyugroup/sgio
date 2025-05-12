# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2023 replay file
# Internal Version: 2022_09_28-14.11.55 183150
# Run by tian50 on Mon May 12 09:38:16 2025
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=312.906219482422, 
    height=197.607406616211)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=10.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.ConstructionLine(point1=(-0.45, 0.0), point2=(0.35, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
s.ConstructionLine(point1=(0.0, -0.3), point2=(0.0, 0.3))
s.VerticalConstraint(entity=g[3], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(width=6.54781, height=3.29, 
    cameraPosition=(-0.0837495, 0.0227099, 9.42809), cameraTarget=(-0.0837495, 
    0.0227099, 0))
s.FixedConstraint(entity=g[2])
s.FixedConstraint(entity=g[3])
session.viewports['Viewport: 1'].view.setValues(nearPlane=8.67976, 
    farPlane=10.1764, width=8.95838, height=4.50121, cameraPosition=(0.0371426, 
    0.229169, 9.42809), cameraTarget=(0.0371426, 0.229169, 0))
s.Line(point1=(-1.3, 1.65), point2=(1.3, 1.65))
s.HorizontalConstraint(entity=g[4], addUndoState=False)
s.Line(point1=(1.3, 1.65), point2=(1.3, 1.35))
s.VerticalConstraint(entity=g[5], addUndoState=False)
s.PerpendicularConstraint(entity1=g[4], entity2=g[5], addUndoState=False)
s.Line(point1=(1.3, 1.35), point2=(0.55, 1.35))
s.HorizontalConstraint(entity=g[6], addUndoState=False)
s.PerpendicularConstraint(entity1=g[5], entity2=g[6], addUndoState=False)
s.Line(point1=(0.55, 1.35), point2=(0.55, -0.65))
s.VerticalConstraint(entity=g[7], addUndoState=False)
s.PerpendicularConstraint(entity1=g[6], entity2=g[7], addUndoState=False)
s.Line(point1=(0.55, -0.65), point2=(1.3, -0.65))
s.HorizontalConstraint(entity=g[8], addUndoState=False)
s.PerpendicularConstraint(entity1=g[7], entity2=g[8], addUndoState=False)
s.Line(point1=(1.3, -0.65), point2=(1.3, -1.1))
s.VerticalConstraint(entity=g[9], addUndoState=False)
s.PerpendicularConstraint(entity1=g[8], entity2=g[9], addUndoState=False)
s.Line(point1=(1.3, -1.1), point2=(-1.5, -1.1))
s.HorizontalConstraint(entity=g[10], addUndoState=False)
s.PerpendicularConstraint(entity1=g[9], entity2=g[10], addUndoState=False)
s.Line(point1=(-1.5, -1.1), point2=(-1.5, -0.65))
s.VerticalConstraint(entity=g[11], addUndoState=False)
s.PerpendicularConstraint(entity1=g[10], entity2=g[11], addUndoState=False)
s.Line(point1=(-1.5, -0.65), point2=(-0.85, -0.65))
s.HorizontalConstraint(entity=g[12], addUndoState=False)
s.PerpendicularConstraint(entity1=g[11], entity2=g[12], addUndoState=False)
s.Line(point1=(-0.85, -0.65), point2=(-0.85, 1.35))
s.VerticalConstraint(entity=g[13], addUndoState=False)
s.PerpendicularConstraint(entity1=g[12], entity2=g[13], addUndoState=False)
s.Line(point1=(-0.85, 1.35), point2=(-1.3, 1.35))
s.HorizontalConstraint(entity=g[14], addUndoState=False)
s.PerpendicularConstraint(entity1=g[13], entity2=g[14], addUndoState=False)
s.Line(point1=(-1.3, 1.35), point2=(-1.3, 1.65))
s.VerticalConstraint(entity=g[15], addUndoState=False)
s.PerpendicularConstraint(entity1=g[14], entity2=g[15], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=8.52344, 
    farPlane=10.3327, width=9.56918, height=4.80812, cameraPosition=(0.563419, 
    0.138142, 9.42809), cameraTarget=(0.563419, 0.138142, 0))
s.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(0.710448503494263, 
    -1.49619507789612), value=1.0)
s.undo()
s.SymmetryConstraint(entity1=g[11], entity2=g[9], symmetryAxis=g[3])
s.SymmetryConstraint(entity1=g[13], entity2=g[7], symmetryAxis=g[3])
s.SymmetryConstraint(entity1=g[15], entity2=g[5], symmetryAxis=g[3])
s.SymmetryConstraint(entity1=g[10], entity2=g[4], symmetryAxis=g[2])
s.SymmetryConstraint(entity1=g[8], entity2=g[6], symmetryAxis=g[2])
s.DistanceDimension(entity1=g[13], entity2=g[7], textPoint=(0.69206976890564, 
    -0.565785586833954), value=0.001016)
session.viewports['Viewport: 1'].view.setValues(nearPlane=9.21424, 
    farPlane=9.64194, width=2.26202, height=1.13657, cameraPosition=(1.12656, 
    0.719131, 9.42809), cameraTarget=(1.12656, 0.719131, 0))
s.ObliqueDimension(vertex1=v[1], vertex2=v[2], textPoint=(1.41619396209717, 
    1.04469275474548), value=0.001016)
session.viewports['Viewport: 1'].view.setValues(nearPlane=9.4102, 
    farPlane=9.44598, width=0.189277, height=0.0951038, cameraPosition=(
    0.0824691, -1.03659, 9.42809), cameraTarget=(0.0824691, -1.03659, 0))
s.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(0.0549621805548668, 
    -1.04530811309814), value=1.0)
session.viewports['Viewport: 1'].view.setValues(nearPlane=9.40132, 
    farPlane=9.45486, width=0.283142, height=0.142267, cameraPosition=(
    0.0869958, -1.03187, 9.42809), cameraTarget=(0.0869958, -1.03187, 0))
s.undo()
s.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(0.0467540919780731, 
    -1.05197465419769), value=0.0254)
session.viewports['Viewport: 1'].view.setValues(nearPlane=9.42008, 
    farPlane=9.4361, width=0.0847635, height=0.0425901, cameraPosition=(
    0.0305624, 1.02281, 9.42809), cameraTarget=(0.0305624, 1.02281, 0))
s.DistanceDimension(entity1=g[10], entity2=g[4], textPoint=(0.0269808638840914, 
    1.02335429191589), value=0.0127)
session.viewports['Viewport: 1'].view.setValues(nearPlane=9.4233, 
    farPlane=9.43288, width=0.0507115, height=0.0254804, cameraPosition=(
    0.00446395, -0.000373484, 9.42809), cameraTarget=(0.00446395, -0.000373484, 
    0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0542304, 
    farPlane=0.0593618, width=0.0306594, height=0.0154051, 
    viewOffsetX=0.0010664, viewOffsetY=0.000170518)
p = mdb.models['Model-1'].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(0.0, 
    0.0, 0.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=0.056, gridSpacing=0.001, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.sketchOptions.setValues(decimalPlaces=3)
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0535668, 
    farPlane=0.0600255, width=0.0341595, height=0.0171637, cameraPosition=(
    0.00154526, -0.000652283, 0.0567961), cameraTarget=(0.00154526, 
    -0.000652283, 0))
s1.Line(point1=(-0.0127, 0.005842), point2=(0.0127000000396743, 0.005842))
s1.HorizontalConstraint(entity=g[14], addUndoState=False)
s1.PerpendicularConstraint(entity1=g[2], entity2=g[14], addUndoState=False)
s1.CoincidentConstraint(entity1=v[12], entity2=g[2], addUndoState=False)
s1.EqualDistanceConstraint(entity1=v[0], entity2=v[1], midpoint=v[12], 
    addUndoState=False)
s1.CoincidentConstraint(entity1=v[13], entity2=g[12], addUndoState=False)
s1.EqualDistanceConstraint(entity1=v[10], entity2=v[11], midpoint=v[13], 
    addUndoState=False)
s1.Line(point1=(-0.0127, -0.005842), point2=(0.0127000000396743, -0.005842))
s1.HorizontalConstraint(entity=g[15], addUndoState=False)
s1.PerpendicularConstraint(entity1=g[6], entity2=g[15], addUndoState=False)
s1.CoincidentConstraint(entity1=v[14], entity2=g[6], addUndoState=False)
s1.EqualDistanceConstraint(entity1=v[4], entity2=v[5], midpoint=v[14], 
    addUndoState=False)
s1.CoincidentConstraint(entity1=v[15], entity2=g[8], addUndoState=False)
s1.EqualDistanceConstraint(entity1=v[6], entity2=v[7], midpoint=v[15], 
    addUndoState=False)
s1.Line(point1=(0.0, 0.005842), point2=(0.0, -0.00584200000660866))
s1.VerticalConstraint(entity=g[16], addUndoState=False)
s1.PerpendicularConstraint(entity1=g[14], entity2=g[16], addUndoState=False)
s1.CoincidentConstraint(entity1=v[16], entity2=g[14], addUndoState=False)
s1.EqualDistanceConstraint(entity1=v[12], entity2=v[13], midpoint=v[16], 
    addUndoState=False)
s1.CoincidentConstraint(entity1=v[17], entity2=g[15], addUndoState=False)
s1.EqualDistanceConstraint(entity1=v[14], entity2=v[15], midpoint=v[17], 
    addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0539427, 
    farPlane=0.0596496, width=0.0341595, height=0.0171637, cameraPosition=(
    0.000298575, -0.000112646, 0.0567961), cameraTarget=(0.000298575, 
    -0.000112646, 0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
mdb.saveAs(
    pathName='C:/Users/tian50/work/dev/sgio/tests/files/abaqus/sg2_i_simple')
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_i_simple.cae".
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='aluminum')
mdb.models['Model-1'].materials['aluminum'].Elastic(table=((71000000000.0, 
    0.33), ))
mdb.models['Model-1'].Material(name='gfrp')
mdb.models['Model-1'].materials['gfrp'].Elastic(type=LAMINA, table=((
    37600000000.0, 9584000000.0, 0.26, 4081000000.0, 4081000000.0, 
    4081000000.0), ))
mdb.models['Model-1'].materials['gfrp'].Density(table=((1903.0, ), ))
mdb.models['Model-1'].materials['aluminum'].Density(table=((2640.0, ), ))
mdb.models['Model-1'].Material(name='cfrp')
mdb.models['Model-1'].materials['cfrp'].Elastic(type=ENGINEERING_CONSTANTS, 
    table=((126000000000.0, 11000000000.0, 11000000000.0, 0.28, 0.28, 0.4, 
    6600000000.0, 6600000000.0, 3929000000.0), ))
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_i_simple.cae".
mdb.models['Model-1'].HomogeneousSolidSection(name='aluminum', 
    material='aluminum', thickness=None)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#8 ]', ), )
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='aluminum', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
region = p.Set(faces=faces, name='Set-2')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='aluminum', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
mdb.models['Model-1'].HomogeneousSolidSection(name='gfrp', material='gfrp', 
    thickness=None)
del mdb.models['Model-1'].sections['gfrp']
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0428827, 
    farPlane=0.072656, width=0.0242439, height=0.0121816, cameraPosition=(
    0.0513344, -0.00714647, 0.0255268), cameraUpVector=(0.240311, 0.948226, 
    -0.207648), cameraTarget=(0.000647467, 0.000332031, 0.00101754), 
    viewOffsetX=0.000843251, viewOffsetY=0.000134837)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.042497, 
    farPlane=0.0733932, width=0.024026, height=0.012072, cameraPosition=(
    0.0517083, 0.0173886, 0.0195484), cameraUpVector=(-0.146018, 0.902668, 
    -0.404807), cameraTarget=(0.000686472, 0.000783379, 0.000924911), 
    viewOffsetX=0.000835667, viewOffsetY=0.000133624)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0450292, 
    farPlane=0.0704782, width=0.0254576, height=0.0127914, cameraPosition=(
    0.0395797, 0.0163638, 0.0387537), cameraUpVector=(-0.032025, 0.934008, 
    -0.355813), cameraTarget=(8.65228e-05, 0.000657391, 0.0010789), 
    viewOffsetX=0.000885461, viewOffsetY=0.000141586)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0498325, 
    farPlane=0.0652786, width=0.0281732, height=0.0141559, cameraPosition=(
    0.0175954, 0.0130536, 0.0532294), cameraUpVector=(-0.000110418, 0.9721, 
    -0.234568), cameraTarget=(-0.000540236, 0.000426641, 0.000908732), 
    viewOffsetX=0.000979914, viewOffsetY=0.000156689)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0511786, 
    farPlane=0.0637889, width=0.0289343, height=0.0145383, cameraPosition=(
    0.0138123, 0.00550818, 0.0555332), cameraUpVector=(-0.0300034, 0.995654, 
    -0.0881591), cameraTarget=(-0.000606177, 0.000232065, 0.000851693), 
    viewOffsetX=0.00100638, viewOffsetY=0.000160921)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#2 ]', ), )
region1 = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#61 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-3')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-1', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='gfrp', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=0.0, 
    additionalRotationType=ROTATION_NONE, additionalRotationField='', 
    axis=AXIS_3, angle=0.0, numIntPoints=1)
compositeLayup.ReferenceOrientation(orientationType=DISCRETE, localCsys=None, 
    additionalRotationType=ROTATION_NONE, angle=0.0, 
    additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3, 
    normalAxisDefinition=VECTOR, normalAxisVector=(0.0, 0.0, 1.0), 
    normalAxisDirection=AXIS_3, flipNormalDirection=False, 
    primaryAxisDefinition=EDGE, primaryAxisRegion=primaryAxisRegion, 
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=True)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0510946, 
    farPlane=0.0638729, width=0.0307307, height=0.0154409, 
    viewOffsetX=0.000787127, viewOffsetY=0.000650569)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#4 ]', ), )
region1 = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1030 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-5')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-2', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='cfrp', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=90.0, 
    additionalRotationType=ROTATION_NONE, additionalRotationField='', 
    axis=AXIS_3, angle=0.0, numIntPoints=1)
compositeLayup.ReferenceOrientation(orientationType=DISCRETE, localCsys=None, 
    additionalRotationType=ROTATION_NONE, angle=0.0, 
    additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3, 
    normalAxisDefinition=VECTOR, normalAxisVector=(0.0, 0.0, 1.0), 
    normalAxisDirection=AXIS_3, flipNormalDirection=False, 
    primaryAxisDefinition=EDGE, primaryAxisRegion=primaryAxisRegion, 
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=False)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_i_simple.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0505759, 
    farPlane=0.0643916, width=0.0367731, height=0.018477, 
    viewOffsetX=7.12839e-05, viewOffsetY=0.000254002)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF, mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=0.0013, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_i_simple.cae".
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
mdb.Job(name='sg2_i_simple_eo1', model='Model-1', description='', 
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
    memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numDomains=1, activateLoadBalancing=False, 
    numThreadsPerMpiProcess=1, multiprocessingMode=DEFAULT, numCpus=1, 
    numGPUs=0)
mdb.jobs['sg2_i_simple_eo1'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_i_simple_eo1.inp".
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=ON)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_i_simple.cae".
mdb.jobs['sg2_i_simple_eo1'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_i_simple_eo1.inp".
