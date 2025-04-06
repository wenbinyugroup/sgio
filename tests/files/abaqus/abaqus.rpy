# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2023 replay file
# Internal Version: 2022_09_28-14.11.55 183150
# Run by tian50 on Wed Apr  2 11:39:21 2025
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
    pathName='C:/Users/tian50/work/dev/sgio/tests/files/sg2_airfoil_composite_section.cae')
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#* MdbError: incompatible release number, expected 2023, got 2017
openMdb(pathName='C:/Users/tian50/work/dev/sgio/tests/files/sg2_airfoil_2.cae')
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#* MdbError: incompatible release number, expected 2023, got 2017
openMdb(pathName='C:/Users/tian50/work/dev/sgio/tests/files/sg2_airfoil.cae')
#: The model database "C:\Users\tian50\work\dev\sgio\tests\files\sg2_airfoil.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.46725, 
    farPlane=3.48386, width=0.0865905, height=0.0410122, viewOffsetX=0.517809, 
    viewOffsetY=0.0680749)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    elementLabels=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.46943, 
    farPlane=3.48168, width=0.0722603, height=0.0342249, viewOffsetX=0.519453, 
    viewOffsetY=0.0723402)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Section']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.46535, 
    farPlane=3.48576, width=0.106344, height=0.0503683, viewOffsetX=0.517737, 
    viewOffsetY=0.0705476)
session.printToFile(
    fileName='C:/Users/tian50/work/dev/sgio/tests/files/sg2_airfoil_zoomin4.png', 
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
