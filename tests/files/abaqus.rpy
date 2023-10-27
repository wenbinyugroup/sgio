# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2017 replay file
# Internal Version: 2016_09_27-17.54.59 126836
# Run by tian50 on Thu Oct 26 16:44:59 2023
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=319.21923828125, 
    height=215.422225952148)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(-23.75, 22.5), point2=(25.0, -21.25))
s.ConstructionLine(point1=(-2.5, 0.0), point2=(3.75, 0.0))
s.HorizontalConstraint(entity=g[6], addUndoState=False)
s.ConstructionLine(point1=(0.0, -3.75), point2=(0.0, 5.0))
s.VerticalConstraint(entity=g[7], addUndoState=False)
s.FixedConstraint(entity=g[6])
s.FixedConstraint(entity=g[7])
s.SymmetryConstraint(entity1=g[2], entity2=g[4], symmetryAxis=g[7])
s.SymmetryConstraint(entity1=g[3], entity2=g[5], symmetryAxis=g[6])
s.ObliqueDimension(vertex1=v[2], vertex2=v[3], textPoint=(30.6540908813477, 
    3.40098571777344), value=50.0)
s.ObliqueDimension(vertex1=v[1], vertex2=v[2], textPoint=(8.66592407226563, 
    -30.1783485412598), value=50.0)
s.rectangle(point1=(-20.0, 20.0), point2=(20.0, -20.0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=130.7, 
    farPlane=152.143, width=129.608, height=66.3823, viewOffsetX=-0.889539, 
    viewOffsetY=1.03736)
p = mdb.models['Model-1'].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(0.0, 
    0.0, 0.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=141.42, gridSpacing=3.53, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.rectangle(point1=(-21.18, 21.18), point2=(21.18, -21.18))
s1.Line(point1=(-25.0, 25.0), point2=(-20.0, 20.0))
s1.Line(point1=(20.0, 20.0), point2=(25.0, 25.0))
s1.Line(point1=(-20.0, -20.0), point2=(-25.0, -25.0))
s1.Line(point1=(20.0, -20.0), point2=(25.0, -25.0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=130.041, 
    farPlane=152.802, width=122.782, height=62.886, viewOffsetX=10.3097, 
    viewOffsetY=-5.28464)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(
    type=ENGINEERING_CONSTANTS, table=((10.0, 20.0, 30.0, 0.12, 0.13, 0.23, 
    1.2, 1.3, 2.3), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-1', thickness=None)
sectionLayer1 = section.SectionLayer(material='Material-1', thickness=1.0, 
    orientAngle=0.0, numIntPts=1, plyName='')
sectionLayer2 = section.SectionLayer(material='Material-1', thickness=1.0, 
    orientAngle=0.0, numIntPts=1, plyName='')
mdb.models['Model-1'].CompositeSolidSection(name='Section-2', 
    layupName='layer1', symmetric=False, layup=(sectionLayer1, sectionLayer2, 
    ))
sectionLayer1 = section.SectionLayer(material='Material-1', thickness=1.0, 
    orientAngle=45.0, numIntPts=1, plyName='')
sectionLayer2 = section.SectionLayer(material='Material-1', thickness=1.0, 
    orientAngle=45.0, numIntPts=1, plyName='')
mdb.models['Model-1'].CompositeSolidSection(name='Section-3', 
    layupName='layer2', symmetric=False, layup=(sectionLayer1, sectionLayer2, 
    ))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1b ]', ), )
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-3', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#e4 ]', ), )
region = p.Set(faces=faces, name='Set-2')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-2', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Section']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=ON)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF, mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Meshability']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedRegions = f.getSequenceFromMask(mask=('[#ff ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON, mesh=OFF)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=OFF)
session.viewports['Viewport: 1'].view.setValues(nearPlane=130.668, 
    farPlane=152.175, width=115.972, height=59.398, viewOffsetX=0.928374, 
    viewOffsetY=-1.51657)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#ff ]', ), )
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#2842 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-4')
mdb.models['Model-1'].parts['Part-1'].MaterialOrientation(region=region, 
    orientationType=DISCRETE, axis=AXIS_3, normalAxisDefinition=VECTOR, 
    normalAxisVector=(0.0, 0.0, 1.0), flipNormalDirection=False, 
    normalAxisDirection=AXIS_3, primaryAxisDefinition=EDGE, 
    primaryAxisRegion=primaryAxisRegion, primaryAxisDirection=AXIS_1, 
    flipPrimaryDirection=True, additionalRotationType=ROTATION_NONE, angle=0.0, 
    additionalRotationField='', stackDirection=STACK_3)
#: Specified material orientation has been assigned to the selected regions.
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF, mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
mdb.saveAs(
    pathName='C:/Users/tian50/work/sgio/tests/files/sg2_box_solid_section')
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_box_solid_section.cae".
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='sg2_box_solid_section', model='Model-1', description='', 
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
    memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
    numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
    numCpus=1, numGPUs=0)
mdb.jobs['sg2_box_solid_section'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_box_solid_section.inp".
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=OFF)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_box_solid_section.cae".
Mdb()
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(-25.0, 25.0), point2=(25.0, -25.0))
s.rectangle(point1=(-20.0, 20.0), point2=(20.0, -20.0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=131.338, 
    farPlane=151.504, width=121.928, height=62.4488, viewOffsetX=1.96146, 
    viewOffsetY=-3.93244)
p = mdb.models['Model-1'].parts['Part-1']
f1, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f1[0], sketchPlaneSide=SIDE1, origin=(
    0.0, 0.0, 0.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=141.42, gridSpacing=3.53, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.rectangle(point1=(-21.18, 21.18), point2=(21.18, -21.18))
session.viewports['Viewport: 1'].view.setValues(width=109.046, height=55.8511, 
    cameraPosition=(0.0268318, -0.29059, 141.421), cameraTarget=(0.0268318, 
    -0.29059, 0))
s1.Line(point1=(-25.0, 25.0), point2=(-20.0, 20.0))
s1.Line(point1=(20.0, 20.0), point2=(25.0, 25.0))
s1.Line(point1=(-25.0, -25.0), point2=(-20.0, -20.0))
s1.Line(point1=(25.0, -25.0), point2=(20.0, -20.0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(
    type=ENGINEERING_CONSTANTS, table=((10.0, 20.0, 30.0, 0.12, 0.13, 0.23, 
    1.2, 1.3, 2.3), ))
sectionLayer1 = section.SectionLayer(material='Material-1', thickness=1.0, 
    orientAngle=0.0, numIntPts=3, plyName='')
sectionLayer2 = section.SectionLayer(material='Material-1', thickness=1.0, 
    orientAngle=0.0, numIntPts=3, plyName='')
mdb.models['Model-1'].CompositeShellSection(name='Section-1', 
    layupName='layup1', preIntegrate=OFF, idealization=NO_IDEALIZATION, 
    symmetric=False, thicknessType=UNIFORM, poissonDefinition=DEFAULT, 
    thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, 
    integrationRule=SIMPSON, layup=(sectionLayer1, sectionLayer2, ))
del mdb.models['Model-1'].sections['Section-1']
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1b ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#2842 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-1')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-1', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='Material-1', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
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
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#e4 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#d0200 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-3')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-2', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='Material-1', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=45.0, 
    additionalRotationType=ROTATION_NONE, additionalRotationField='', 
    axis=AXIS_3, angle=0.0, numIntPoints=1)
compositeLayup.ReferenceOrientation(orientationType=DISCRETE, localCsys=None, 
    additionalRotationType=ROTATION_NONE, angle=0.0, 
    additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3, 
    normalAxisDefinition=VECTOR, normalAxisVector=(0.0, 0.0, 1.0), 
    normalAxisDirection=AXIS_3, flipNormalDirection=False, 
    primaryAxisDefinition=EDGE, primaryAxisRegion=primaryAxisRegion, 
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=False)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
mdb.saveAs(
    pathName='C:/Users/tian50/work/sgio/tests/files/sg2_box_composite_section.cae')
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_box_composite_section.cae".
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=ON)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
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
pickedRegions = f.getSequenceFromMask(mask=('[#ff ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED)
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_box_composite_section.cae".
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='sg2_box_composite_section', model='Model-1', description='', 
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
    memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
    numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
    numCpus=1, numGPUs=0)
mdb.jobs['sg2_box_composite_section'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_box_composite_section.inp".
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_box_composite_section.cae".
Mdb()
#: A new model database has been created.
#: The model "Model-1" has been created.
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=OFF)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
session.viewports['Viewport: 1'].setValues(displayedObject=None)
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(-25.0, 25.0), point2=(25.0, -25.0))
s.rectangle(point1=(-20.0, 20.0), point2=(20.0, -20.0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchUpEdge=e[7], 
    sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=141.42, gridSpacing=3.53, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.rectangle(point1=(-21.18, 21.18), point2=(21.18, -21.18))
s1.Line(point1=(-25.0, 25.0), point2=(-20.0, 20.0))
s1.Line(point1=(25.0, 25.0), point2=(20.0, 20.0))
s1.Line(point1=(-25.0, -25.0), point2=(-20.0, -20.0))
s1.Line(point1=(25.0, -25.0), point2=(20.0, -20.0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(sketchUpEdge=e1[7], faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(
    type=ENGINEERING_CONSTANTS, table=((10.0, 20.0, 30.0, 0.12, 0.13, 0.23, 
    1.2, 1.3, 2.3), ))
mdb.models['Model-1'].HomogeneousShellSection(name='Section-1', 
    preIntegrate=OFF, material='Material-1', thicknessType=UNIFORM, 
    thickness=1.0, thicknessField='', nodalThicknessField='', 
    idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
    thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, 
    integrationRule=SIMPSON, numIntPts=5)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1b ]', ), )
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
mdb.models['Model-1'].sections['Section-1'].setValues(preIntegrate=OFF, 
    material='Material-1', thicknessType=UNIFORM, thickness=1.0, 
    thicknessField='', nodalThicknessField='', idealization=NO_IDEALIZATION, 
    integrationRule=SIMPSON, numIntPts=5)
mdb.models['Model-1'].HomogeneousShellSection(name='Section-2', 
    preIntegrate=OFF, material='Material-1', thicknessType=UNIFORM, 
    thickness=2.0, thicknessField='', nodalThicknessField='', 
    idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
    thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, 
    integrationRule=SIMPSON, numIntPts=5)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#e4 ]', ), )
region = p.Set(faces=faces, name='Set-2')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-2', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
mdb.saveAs(
    pathName='C:/Users/tian50/work/sgio/tests/files/sg2_box_shell_section.cae')
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_box_shell_section.cae".
openMdb(
    pathName='C:/Users/tian50/work/sgio/tests/files/sg2_box_composite_section.cae')
#: The model database "C:\Users\tian50\work\sgio\tests\files\sg2_box_composite_section.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
    engineeringFeatures=OFF)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
