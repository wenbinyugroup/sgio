from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

def loadAirfoilData(fn, header=0, delimiter=None):
    xy = []

    with open(fn, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if i < header:  continue
            line = line.strip()
            if line == '':  continue
            line = line.split(delimiter)
            # print(line)

            xy.append((float(line[0]), float(line[1])))

    return xy

from abaqus import getInputs
fields = (('Model:','Model-1'), ('Sketch:', 'airfoil'), ('Airfoil file:', ''))
model_name, sketch_name, fn_airfoil = getInputs(
    fields=fields, 
    label='Specify import options:',
    dialogTitle='Import airfoil sketch', )
print 'Model:', model_name
print 'Sketch:', sketch_name
print 'Airfoil file:', fn_airfoil

# model_name = 'Model-1'
m = mdb.models[model_name]

# sketch_name = 'airfoil'
s = m.ConstrainedSketch(name='__profile__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
xy_airfoil = loadAirfoilData(fn_airfoil)
lines = []
for i in range(len(xy_airfoil)-1):
    line = s.Line(point1=xy_airfoil[i], point2=xy_airfoil[i+1])
    lines.append(line) 
# s.Spline(points=tuple(xy_airfoil))
m.sketches.changeKey(fromName='__profile__', toName=sketch_name)
s.unsetPrimaryObject()  # Close the sketch
# del m.sketches['__profile__']
