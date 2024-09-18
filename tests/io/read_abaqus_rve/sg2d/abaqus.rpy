# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2023 replay file
# Internal Version: 2022_09_28-14.11.55 183150
# Run by tian50 on Wed Mar 20 10:30:42 2024
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=175.392181396484, 
    height=223.918518066406)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
mdb.ModelFromInputFile(name='sg2_airfoil_mesh', 
    inputFileName='C:/Users/tian50/work/dev/sgio/tests/io/read_abaqus_rve/sg2d/sg2_airfoil_mesh.inp')
#: The model "sg2_airfoil_mesh" has been created.
#: The part "PART-1" has been imported from the input file.
#: The model "sg2_airfoil_mesh" has been imported from an input file. 
#: Please scroll up to check for error and warning messages.
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
a = mdb.models['sg2_airfoil_mesh'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
