# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2023 replay file
# Internal Version: 2022_09_28-14.11.55 183150
# Run by tian50 on Thu Apr 24 19:24:29 2025
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=307.691131591797, 
    height=197.607406616211)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
openMdb(
    pathName='C:/Users/tian50/work/dev/sgio/tests/files/abaqus/sg2_box_composite_section.cae')
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#* MdbError: incompatible release number, expected 2023, got 2017
upgradeMdb(
    "C:/Users/tian50/work/dev/sgio/tests/files/abaqus/sg2_box_composite_section-2017.cae", 
    "C:/Users/tian50/work/dev/sgio/tests/files/abaqus/sg2_box_composite_section.cae", 
    )
#: The model database "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_box_composite_section_TEMP.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_box_composite_section.cae".
#: The model database "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_box_composite_section-2017.cae" has been converted.
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p = mdb.models['Model-1'].Part(name='Part-1-failed', 
    objectToCopy=mdb.models['Model-1'].parts['Part-1'])
mdb.models['Model-1'].parts['Part-1-failed'].Unlock(reportWarnings=False)
del mdb.models['Model-1'].parts['Part-1']
mdb.models['Model-1'].parts.changeKey(fromName='Part-1-failed', 
    toName='Part-1')
import assembly
mdb.models['Model-1'].rootAssembly.regenerate()
#* FeatureError: The assembly is locked and cannot be regenerated.
p1 = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
a = mdb.models['Model-1'].rootAssembly
a.unlock()
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=ON)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
session.viewports['Viewport: 1'].view.setValues(nearPlane=124.661, 
    farPlane=158.182, width=175.571, height=82.1421, viewOffsetX=4.63819, 
    viewOffsetY=-8.35194)
elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#ff ]', ), )
pickedRegions =(faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='sg2_box_composite_section_quad8', model='Model-1', 
    description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, 
    queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numDomains=1, activateLoadBalancing=False, 
    numThreadsPerMpiProcess=1, multiprocessingMode=DEFAULT, numCpus=1, 
    numGPUs=0)
mdb.jobs['sg2_box_composite_section_quad8'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_box_composite_section_quad8.inp".
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_box_composite_section.cae".
