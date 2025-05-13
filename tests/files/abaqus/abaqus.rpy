# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2023 replay file
# Internal Version: 2022_09_28-14.11.55 183150
# Run by tian50 on Mon May 12 16:43:38 2025
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=312.906219482422, 
    height=208.296295166016)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
openMdb(
    pathName='C:/Users/tian50/work/dev/sgio/tests/files/abaqus/sg2_i_simple.cae')
#: The model database "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_i_simple.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.053959, 
    farPlane=0.0596332, width=0.0351133, height=0.0179358, 
    viewOffsetX=0.00178821, viewOffsetY=-0.000545501)
elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD, 
    secondOrderAccuracy=OFF, distortionControl=DEFAULT)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#f ]', ), )
pickedRegions =(faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
mdb.Job(name='sg2_i_simple_eo2', model='Model-1', description='', 
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
    memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numDomains=1, activateLoadBalancing=False, 
    numThreadsPerMpiProcess=1, multiprocessingMode=DEFAULT, numCpus=1, 
    numGPUs=0)
mdb.jobs['sg2_i_simple_eo2'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_i_simple_eo2.inp".
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\dev\sgio\tests\files\abaqus\sg2_i_simple.cae".
