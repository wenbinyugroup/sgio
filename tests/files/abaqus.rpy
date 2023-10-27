# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2017 replay file
# Internal Version: 2016_09_27-17.54.59 126836
# Run by tian50 on Fri Oct 27 17:03:32 2023
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
s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(10.0, 0.0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
execfile('C:/Users/tian50/work/sgio/tests/files/abq_import_sketch_airfoil.py', 
    __main__.__dict__)
#: Model: Model-1
#: Sketch: airfoil
#: Airfoil file: sc1095,dat
#* IOError: (2, 'No such file or directory', 'sc1095,dat')
#* File "C:/Users/tian50/work/sgio/tests/files/abq_import_sketch_airfoil.py", 
#* line 48, in <module>
#*     xy_airfoil = loadAirfoilData(fn_airfoil)
#* File "C:/Users/tian50/work/sgio/tests/files/abq_import_sketch_airfoil.py", 
#* line 18, in loadAirfoilData
#*     with open(fn, 'r') as file:
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
execfile('C:/Users/tian50/work/sgio/tests/files/abq_import_sketch_airfoil.py', 
    __main__.__dict__)
#: Model: Model-1
#: Sketch: airfoil
#: Airfoil file: sc1095.dat
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p = mdb.models['Model-1'].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(0.0, 
    0.0, 0.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=56.41, gridSpacing=1.41, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.ConstructionLine(point1=(-0.705, 0.0), point2=(1.41, 0.0))
s1.HorizontalConstraint(entity=g[3], addUndoState=False)
s1.ConstructionLine(point1=(0.0, -1.0575), point2=(0.0, 1.41))
s1.VerticalConstraint(entity=g[4], addUndoState=False)
s1.FixedConstraint(entity=v[0])
s1.FixedConstraint(entity=g[3])
s1.FixedConstraint(entity=g[4])
s1.retrieveSketch(sketch=mdb.models['Model-1'].sketches['airfoil'])
session.viewports['Viewport: 1'].view.fitView()
#: Info: 300 entities copied from airfoil.
session.viewports['Viewport: 1'].view.setValues(nearPlane=55.7033, 
    farPlane=57.4338, width=9.28684, height=4.7565, cameraPosition=(0.0500233, 
    -0.64934, 56.5685), cameraTarget=(0.0500233, -0.64934, 0))
s1.mirror(mirrorLine=g[4], objectList=(g[7], g[8], g[9], g[10], g[11], g[12], 
    g[13], g[14], g[15], g[16], g[17], g[18], g[19], g[20], g[21], g[22], 
    g[23], g[24], g[25], g[26], g[27], g[28], g[29], g[30], g[31], g[32], 
    g[33], g[34], g[35], g[36], g[37], g[38], g[39], g[40], g[41], g[42], 
    g[43], g[44], g[45], g[46], g[47], g[48], g[49], g[50], g[51], g[52], 
    g[53], g[54], g[55], g[56], g[57], g[58], g[59], g[60], g[61], g[62], 
    g[63], g[64], g[65], g[66], g[67], g[68], g[69], g[70], g[71], g[72], 
    g[73], g[74], g[75], g[76], g[77], g[78], g[79], g[80], g[81], g[82], 
    g[83], g[84], g[85], g[86], g[87], g[88], g[89], g[90], g[91], g[92], 
    g[93], g[94], g[95], g[96], g[97], g[98], g[99], g[100], g[101], g[102], 
    g[103], g[104], g[105], g[106], g[107], g[108], g[109], g[110], g[111], 
    g[112], g[113], g[114], g[115], g[116], g[117], g[118], g[119], g[120], 
    g[121], g[122], g[123], g[124], g[125], g[126], g[127], g[128], g[129], 
    g[130], g[131], g[132], g[133], g[134], g[135], g[136], g[137], g[138], 
    g[139], g[140], g[141], g[142], g[143], g[144], g[145], g[146], g[147], 
    g[148], g[149], g[150], g[151], g[152], g[153], g[154], g[155], g[156], 
    g[157], g[158], g[159], g[160], g[161], g[162], g[163], g[164], g[165], 
    g[166], g[167], g[168], g[169], g[170], g[171], g[172], g[173], g[174], 
    g[175], g[176], g[177], g[178], g[179], g[180], g[181], g[182], g[183], 
    g[184], g[185], g[186], g[187], g[188], g[189], g[190], g[191], g[192], 
    g[193], g[194], g[195], g[196], g[197], g[198], g[199], g[200], g[201], 
    g[202], g[203], g[204], g[205], g[206], g[207], g[208], g[209], g[210], 
    g[211], g[212], g[213], g[214], g[215], g[216], g[217], g[218], g[219], 
    g[220], g[221], g[222], g[223], g[224], g[225], g[226], g[227], g[228], 
    g[229], g[230], g[231], g[232], g[233], g[234], g[235], g[236], g[237], 
    g[238], g[239], g[240], g[241], g[242], g[243], g[244], g[245], g[246], 
    g[247], g[248], g[249], g[250], g[251], g[252], g[253], g[254], g[255], 
    g[256], g[257], g[258], g[259], g[260], g[261], g[262], g[263], g[264], 
    g[265], g[266], g[267], g[268], g[269], g[270], g[271], g[272], g[273], 
    g[274], g[275], g[276], g[277], g[278], g[279], g[280], g[281], g[282], 
    g[283], g[284], g[285], g[286], g[287], g[288], g[289], g[290], g[291], 
    g[292], g[293], g[294], g[295], g[296], g[297], g[298], g[299], g[300], 
    g[301], g[302], g[303], g[304], g[305], g[306]))
s1.move(vector=(0.25, 0.0), objectList=(g[7], g[8], g[9], g[10], g[11], g[12], 
    g[13], g[14], g[15], g[16], g[17], g[18], g[19], g[20], g[21], g[22], 
    g[23], g[24], g[25], g[26], g[27], g[28], g[29], g[30], g[31], g[32], 
    g[33], g[34], g[35], g[36], g[37], g[38], g[39], g[40], g[41], g[42], 
    g[43], g[44], g[45], g[46], g[47], g[48], g[49], g[50], g[51], g[52], 
    g[53], g[54], g[55], g[56], g[57], g[58], g[59], g[60], g[61], g[62], 
    g[63], g[64], g[65], g[66], g[67], g[68], g[69], g[70], g[71], g[72], 
    g[73], g[74], g[75], g[76], g[77], g[78], g[79], g[80], g[81], g[82], 
    g[83], g[84], g[85], g[86], g[87], g[88], g[89], g[90], g[91], g[92], 
    g[93], g[94], g[95], g[96], g[97], g[98], g[99], g[100], g[101], g[102], 
    g[103], g[104], g[105], g[106], g[107], g[108], g[109], g[110], g[111], 
    g[112], g[113], g[114], g[115], g[116], g[117], g[118], g[119], g[120], 
    g[121], g[122], g[123], g[124], g[125], g[126], g[127], g[128], g[129], 
    g[130], g[131], g[132], g[133], g[134], g[135], g[136], g[137], g[138], 
    g[139], g[140], g[141], g[142], g[143], g[144], g[145], g[146], g[147], 
    g[148], g[149], g[150], g[151], g[152], g[153], g[154], g[155], g[156], 
    g[157], g[158], g[159], g[160], g[161], g[162], g[163], g[164], g[165], 
    g[166], g[167], g[168], g[169], g[170], g[171], g[172], g[173], g[174], 
    g[175], g[176], g[177], g[178], g[179], g[180], g[181], g[182], g[183], 
    g[184], g[185], g[186], g[187], g[188], g[189], g[190], g[191], g[192], 
    g[193], g[194], g[195], g[196], g[197], g[198], g[199], g[200], g[201], 
    g[202], g[203], g[204], g[205], g[206], g[207], g[208], g[209], g[210], 
    g[211], g[212], g[213], g[214], g[215], g[216], g[217], g[218], g[219], 
    g[220], g[221], g[222], g[223], g[224], g[225], g[226], g[227], g[228], 
    g[229], g[230], g[231], g[232], g[233], g[234], g[235], g[236], g[237], 
    g[238], g[239], g[240], g[241], g[242], g[243], g[244], g[245], g[246], 
    g[247], g[248], g[249], g[250], g[251], g[252], g[253], g[254], g[255], 
    g[256], g[257], g[258], g[259], g[260], g[261], g[262], g[263], g[264], 
    g[265], g[266], g[267], g[268], g[269], g[270], g[271], g[272], g[273], 
    g[274], g[275], g[276], g[277], g[278], g[279], g[280], g[281], g[282], 
    g[283], g[284], g[285], g[286], g[287], g[288], g[289], g[290], g[291], 
    g[292], g[293], g[294], g[295], g[296], g[297], g[298], g[299], g[300], 
    g[301], g[302], g[303], g[304], g[305], g[306]))
s1.scale(scaleValue=2.0, scaleCenter=(0.0, 0.0), objectList=(g[7], g[8], g[9], 
    g[10], g[11], g[12], g[13], g[14], g[15], g[16], g[17], g[18], g[19], 
    g[20], g[21], g[22], g[23], g[24], g[25], g[26], g[27], g[28], g[29], 
    g[30], g[31], g[32], g[33], g[34], g[35], g[36], g[37], g[38], g[39], 
    g[40], g[41], g[42], g[43], g[44], g[45], g[46], g[47], g[48], g[49], 
    g[50], g[51], g[52], g[53], g[54], g[55], g[56], g[57], g[58], g[59], 
    g[60], g[61], g[62], g[63], g[64], g[65], g[66], g[67], g[68], g[69], 
    g[70], g[71], g[72], g[73], g[74], g[75], g[76], g[77], g[78], g[79], 
    g[80], g[81], g[82], g[83], g[84], g[85], g[86], g[87], g[88], g[89], 
    g[90], g[91], g[92], g[93], g[94], g[95], g[96], g[97], g[98], g[99], 
    g[100], g[101], g[102], g[103], g[104], g[105], g[106], g[107], g[108], 
    g[109], g[110], g[111], g[112], g[113], g[114], g[115], g[116], g[117], 
    g[118], g[119], g[120], g[121], g[122], g[123], g[124], g[125], g[126], 
    g[127], g[128], g[129], g[130], g[131], g[132], g[133], g[134], g[135], 
    g[136], g[137], g[138], g[139], g[140], g[141], g[142], g[143], g[144], 
    g[145], g[146], g[147], g[148], g[149], g[150], g[151], g[152], g[153], 
    g[154], g[155], g[156], g[157], g[158], g[159], g[160], g[161], g[162], 
    g[163], g[164], g[165], g[166], g[167], g[168], g[169], g[170], g[171], 
    g[172], g[173], g[174], g[175], g[176], g[177], g[178], g[179], g[180], 
    g[181], g[182], g[183], g[184], g[185], g[186], g[187], g[188], g[189], 
    g[190], g[191], g[192], g[193], g[194], g[195], g[196], g[197], g[198], 
    g[199], g[200], g[201], g[202], g[203], g[204], g[205], g[206], g[207], 
    g[208], g[209], g[210], g[211], g[212], g[213], g[214], g[215], g[216], 
    g[217], g[218], g[219], g[220], g[221], g[222], g[223], g[224], g[225], 
    g[226], g[227], g[228], g[229], g[230], g[231], g[232], g[233], g[234], 
    g[235], g[236], g[237], g[238], g[239], g[240], g[241], g[242], g[243], 
    g[244], g[245], g[246], g[247], g[248], g[249], g[250], g[251], g[252], 
    g[253], g[254], g[255], g[256], g[257], g[258], g[259], g[260], g[261], 
    g[262], g[263], g[264], g[265], g[266], g[267], g[268], g[269], g[270], 
    g[271], g[272], g[273], g[274], g[275], g[276], g[277], g[278], g[279], 
    g[280], g[281], g[282], g[283], g[284], g[285], g[286], g[287], g[288], 
    g[289], g[290], g[291], g[292], g[293], g[294], g[295], g[296], g[297], 
    g[298], g[299], g[300], g[301], g[302], g[303], g[304], g[305], g[306]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5461, 
    farPlane=56.591, width=0.241219, height=0.123547, cameraPosition=(-1.46533, 
    -0.0234023, 56.5685), cameraTarget=(-1.46533, -0.0234023, 0))
s1.Line(point1=(-1.5, -0.003458), point2=(-1.5, 0.003458))
s1.VerticalConstraint(entity=g[307], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5087, 
    farPlane=56.6284, width=0.727487, height=0.372602, cameraPosition=(
    -1.21396, -0.0035392, 56.5685), cameraTarget=(-1.21396, -0.0035392, 0))
s1.offset(distance=0.01, objectList=(g[7], g[8], g[9], g[10], g[11], g[12], 
    g[13], g[14], g[15], g[16], g[17], g[18], g[19], g[20], g[21], g[22], 
    g[23], g[24], g[25], g[26], g[27], g[28], g[29], g[30], g[31], g[32], 
    g[33], g[34], g[35], g[36], g[37], g[38], g[39], g[40], g[41], g[42], 
    g[43], g[44], g[45], g[46], g[47], g[48], g[49], g[50], g[51], g[52], 
    g[53], g[54], g[55], g[56], g[57], g[58], g[59], g[60], g[61], g[62], 
    g[63], g[64], g[65], g[66], g[67], g[68], g[69], g[70], g[71], g[72], 
    g[73], g[74], g[75], g[76], g[77], g[78], g[79], g[80], g[81], g[82], 
    g[83], g[84], g[85], g[86], g[87], g[88], g[89], g[90], g[91], g[92], 
    g[93], g[94], g[95], g[96], g[97], g[98], g[99], g[100], g[101], g[102], 
    g[103], g[104], g[105], g[106], g[107], g[108], g[109], g[110], g[111], 
    g[112], g[113], g[114], g[115], g[116], g[117], g[118], g[119], g[120], 
    g[121], g[122], g[123], g[124], g[125], g[126], g[127], g[128], g[129], 
    g[130], g[131], g[132], g[133], g[134], g[135], g[136], g[137], g[138], 
    g[139], g[140], g[141], g[142], g[143], g[144], g[145], g[146], g[147], 
    g[148], g[149], g[150], g[151], g[152], g[153], g[154], g[155], g[156], 
    g[157], g[158], g[159], g[160], g[161], g[162], g[163], g[164], g[165], 
    g[166], g[167], g[168], g[169], g[170], g[171], g[172], g[173], g[174], 
    g[175], g[176], g[177], g[178], g[179], g[180], g[181], g[182], g[183], 
    g[184], g[185], g[186], g[187], g[188], g[189], g[190], g[191], g[192], 
    g[193], g[194], g[195], g[196], g[197], g[198], g[199], g[200], g[201], 
    g[202], g[203], g[204], g[205], g[206], g[207], g[208], g[209], g[210], 
    g[211], g[212], g[213], g[214], g[215], g[216], g[217], g[218], g[219], 
    g[220], g[221], g[222], g[223], g[224], g[225], g[226], g[227], g[228], 
    g[229], g[230], g[231], g[232], g[233], g[234], g[235], g[236], g[237], 
    g[238], g[239], g[240], g[241], g[242], g[243], g[244], g[245], g[246], 
    g[247], g[248], g[249], g[250], g[251], g[252], g[253], g[254], g[255], 
    g[256], g[257], g[258], g[259], g[260], g[261], g[262], g[263], g[264], 
    g[265], g[266], g[267], g[268], g[269], g[270], g[271], g[272], g[273], 
    g[274], g[275], g[276], g[277], g[278], g[279], g[280], g[281], g[282], 
    g[283], g[284], g[285], g[286], g[287], g[288], g[289], g[290], g[291], 
    g[292], g[293], g[294], g[295], g[296], g[297], g[298], g[299], g[300], 
    g[301], g[302], g[303], g[304], g[305], g[306], g[307]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4396, 
    farPlane=56.6975, width=1.38416, height=0.708932, cameraPosition=(0.151416, 
    -0.0656281, 56.5685), cameraTarget=(0.151416, -0.0656281, 0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.0463, 
    farPlane=57.0908, width=5.60871, height=2.87265, viewOffsetX=-0.194019, 
    viewOffsetY=-0.465994)
p = mdb.models['Model-1'].parts['Part-1']
f1 = p.faces
p.RemoveFaces(faceList = f1[2:3], deleteCells=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3028, 
    farPlane=56.8342, width=2.85268, height=1.46108, viewOffsetX=-0.494934, 
    viewOffsetY=-0.133458)
session.viewports['Viewport: 1'].view.fitView()
mdb.saveAs(
    pathName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil_composite_section.cae')
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_composite_section.cae".
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(
    type=ENGINEERING_CONSTANTS, table=((10.0, 20.0, 30.0, 0.12, 0.13, 0.23, 
    1.2, 1.3, 2.3), ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.84529, 
    farPlane=4.19068, width=1.85874, height=0.952004, viewOffsetX=0.0822824, 
    viewOffsetY=-0.0107251)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#ffffffff:9 #1fff ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-1')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-1', description='', elementType=SOLID, 
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
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=True)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
mdb.models['Model-1'].Material(name='Material-2')
mdb.models['Model-1'].materials['Material-2'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['Material-2'].Elastic(table=((1.0, 0.0), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-2', thickness=None)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#2 ]', ), )
region = p.Set(faces=faces, name='Set-3')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Part']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Section']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.8338, 
    farPlane=4.20217, width=2.23119, height=1.14276, viewOffsetX=-0.0404353, 
    viewOffsetY=-0.0743095)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_composite_section.cae".
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.81155, 
    farPlane=4.22442, width=2.21824, height=1.13901, viewOffsetX=0.050576, 
    viewOffsetY=0.0233839)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Meshability']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=0.01, deviationFactor=0.1, minSizeFactor=0.1)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.83263, 
    farPlane=4.20334, width=2.23964, height=1.14999, viewOffsetX=0.118124, 
    viewOffsetY=0.021889)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_composite_section.cae".
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Section']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_composite_section.cae".
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='sg2_airfoil_composite_section', model='Model-1', description='', 
    type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
    memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
    numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
    numCpus=1, numGPUs=0)
mdb.jobs['sg2_airfoil_composite_section'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_airfoil_composite_section.inp".
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_composite_section.cae".
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_composite_section.cae".
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
s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(10.0, 0.0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
execfile('C:/Users/tian50/work/sgio/tests/files/abq_import_sketch_airfoil.py', 
    __main__.__dict__)
#: Model: Model-1
#: Sketch: airfoil
#: Airfoil file: sc1095.dat
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p = mdb.models['Model-1'].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(0.0, 
    0.0, 0.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=56.41, gridSpacing=1.41, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.retrieveSketch(sketch=mdb.models['Model-1'].sketches['airfoil'])
session.viewports['Viewport: 1'].view.fitView()
#: Info: 300 entities copied from airfoil.
s1.undo()
s1.ConstructionLine(point1=(-1.41, 0.0), point2=(0.705000000037253, 0.0))
s1.HorizontalConstraint(entity=g[3], addUndoState=False)
s1.ConstructionLine(point1=(0.0, -0.705), point2=(0.0, 0.705000000037253))
s1.VerticalConstraint(entity=g[4], addUndoState=False)
s1.FixedConstraint(entity=v[0])
s1.FixedConstraint(entity=g[3])
s1.FixedConstraint(entity=g[4])
s1.retrieveSketch(sketch=mdb.models['Model-1'].sketches['airfoil'])
session.viewports['Viewport: 1'].view.fitView()
#: Info: 300 entities copied from airfoil.
s1.mirror(mirrorLine=g[4], objectList=(g[7], g[8], g[9], g[10], g[11], g[12], 
    g[13], g[14], g[15], g[16], g[17], g[18], g[19], g[20], g[21], g[22], 
    g[23], g[24], g[25], g[26], g[27], g[28], g[29], g[30], g[31], g[32], 
    g[33], g[34], g[35], g[36], g[37], g[38], g[39], g[40], g[41], g[42], 
    g[43], g[44], g[45], g[46], g[47], g[48], g[49], g[50], g[51], g[52], 
    g[53], g[54], g[55], g[56], g[57], g[58], g[59], g[60], g[61], g[62], 
    g[63], g[64], g[65], g[66], g[67], g[68], g[69], g[70], g[71], g[72], 
    g[73], g[74], g[75], g[76], g[77], g[78], g[79], g[80], g[81], g[82], 
    g[83], g[84], g[85], g[86], g[87], g[88], g[89], g[90], g[91], g[92], 
    g[93], g[94], g[95], g[96], g[97], g[98], g[99], g[100], g[101], g[102], 
    g[103], g[104], g[105], g[106], g[107], g[108], g[109], g[110], g[111], 
    g[112], g[113], g[114], g[115], g[116], g[117], g[118], g[119], g[120], 
    g[121], g[122], g[123], g[124], g[125], g[126], g[127], g[128], g[129], 
    g[130], g[131], g[132], g[133], g[134], g[135], g[136], g[137], g[138], 
    g[139], g[140], g[141], g[142], g[143], g[144], g[145], g[146], g[147], 
    g[148], g[149], g[150], g[151], g[152], g[153], g[154], g[155], g[156], 
    g[157], g[158], g[159], g[160], g[161], g[162], g[163], g[164], g[165], 
    g[166], g[167], g[168], g[169], g[170], g[171], g[172], g[173], g[174], 
    g[175], g[176], g[177], g[178], g[179], g[180], g[181], g[182], g[183], 
    g[184], g[185], g[186], g[187], g[188], g[189], g[190], g[191], g[192], 
    g[193], g[194], g[195], g[196], g[197], g[198], g[199], g[200], g[201], 
    g[202], g[203], g[204], g[205], g[206], g[207], g[208], g[209], g[210], 
    g[211], g[212], g[213], g[214], g[215], g[216], g[217], g[218], g[219], 
    g[220], g[221], g[222], g[223], g[224], g[225], g[226], g[227], g[228], 
    g[229], g[230], g[231], g[232], g[233], g[234], g[235], g[236], g[237], 
    g[238], g[239], g[240], g[241], g[242], g[243], g[244], g[245], g[246], 
    g[247], g[248], g[249], g[250], g[251], g[252], g[253], g[254], g[255], 
    g[256], g[257], g[258], g[259], g[260], g[261], g[262], g[263], g[264], 
    g[265], g[266], g[267], g[268], g[269], g[270], g[271], g[272], g[273], 
    g[274], g[275], g[276], g[277], g[278], g[279], g[280], g[281], g[282], 
    g[283], g[284], g[285], g[286], g[287], g[288], g[289], g[290], g[291], 
    g[292], g[293], g[294], g[295], g[296], g[297], g[298], g[299], g[300], 
    g[301], g[302], g[303], g[304], g[305], g[306]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=55.1491, 
    farPlane=57.9879, width=15.2351, height=7.80306, cameraPosition=(0.350283, 
    -0.0460277, 56.5685), cameraTarget=(0.350283, -0.0460277, 0))
s1.move(vector=(0.25, 0.0), objectList=(g[7], g[8], g[9], g[10], g[11], g[12], 
    g[13], g[14], g[15], g[16], g[17], g[18], g[19], g[20], g[21], g[22], 
    g[23], g[24], g[25], g[26], g[27], g[28], g[29], g[30], g[31], g[32], 
    g[33], g[34], g[35], g[36], g[37], g[38], g[39], g[40], g[41], g[42], 
    g[43], g[44], g[45], g[46], g[47], g[48], g[49], g[50], g[51], g[52], 
    g[53], g[54], g[55], g[56], g[57], g[58], g[59], g[60], g[61], g[62], 
    g[63], g[64], g[65], g[66], g[67], g[68], g[69], g[70], g[71], g[72], 
    g[73], g[74], g[75], g[76], g[77], g[78], g[79], g[80], g[81], g[82], 
    g[83], g[84], g[85], g[86], g[87], g[88], g[89], g[90], g[91], g[92], 
    g[93], g[94], g[95], g[96], g[97], g[98], g[99], g[100], g[101], g[102], 
    g[103], g[104], g[105], g[106], g[107], g[108], g[109], g[110], g[111], 
    g[112], g[113], g[114], g[115], g[116], g[117], g[118], g[119], g[120], 
    g[121], g[122], g[123], g[124], g[125], g[126], g[127], g[128], g[129], 
    g[130], g[131], g[132], g[133], g[134], g[135], g[136], g[137], g[138], 
    g[139], g[140], g[141], g[142], g[143], g[144], g[145], g[146], g[147], 
    g[148], g[149], g[150], g[151], g[152], g[153], g[154], g[155], g[156], 
    g[157], g[158], g[159], g[160], g[161], g[162], g[163], g[164], g[165], 
    g[166], g[167], g[168], g[169], g[170], g[171], g[172], g[173], g[174], 
    g[175], g[176], g[177], g[178], g[179], g[180], g[181], g[182], g[183], 
    g[184], g[185], g[186], g[187], g[188], g[189], g[190], g[191], g[192], 
    g[193], g[194], g[195], g[196], g[197], g[198], g[199], g[200], g[201], 
    g[202], g[203], g[204], g[205], g[206], g[207], g[208], g[209], g[210], 
    g[211], g[212], g[213], g[214], g[215], g[216], g[217], g[218], g[219], 
    g[220], g[221], g[222], g[223], g[224], g[225], g[226], g[227], g[228], 
    g[229], g[230], g[231], g[232], g[233], g[234], g[235], g[236], g[237], 
    g[238], g[239], g[240], g[241], g[242], g[243], g[244], g[245], g[246], 
    g[247], g[248], g[249], g[250], g[251], g[252], g[253], g[254], g[255], 
    g[256], g[257], g[258], g[259], g[260], g[261], g[262], g[263], g[264], 
    g[265], g[266], g[267], g[268], g[269], g[270], g[271], g[272], g[273], 
    g[274], g[275], g[276], g[277], g[278], g[279], g[280], g[281], g[282], 
    g[283], g[284], g[285], g[286], g[287], g[288], g[289], g[290], g[291], 
    g[292], g[293], g[294], g[295], g[296], g[297], g[298], g[299], g[300], 
    g[301], g[302], g[303], g[304], g[305], g[306]))
s1.scale(scaleValue=2.0, scaleCenter=(0.0, 0.0), objectList=(g[7], g[8], g[9], 
    g[10], g[11], g[12], g[13], g[14], g[15], g[16], g[17], g[18], g[19], 
    g[20], g[21], g[22], g[23], g[24], g[25], g[26], g[27], g[28], g[29], 
    g[30], g[31], g[32], g[33], g[34], g[35], g[36], g[37], g[38], g[39], 
    g[40], g[41], g[42], g[43], g[44], g[45], g[46], g[47], g[48], g[49], 
    g[50], g[51], g[52], g[53], g[54], g[55], g[56], g[57], g[58], g[59], 
    g[60], g[61], g[62], g[63], g[64], g[65], g[66], g[67], g[68], g[69], 
    g[70], g[71], g[72], g[73], g[74], g[75], g[76], g[77], g[78], g[79], 
    g[80], g[81], g[82], g[83], g[84], g[85], g[86], g[87], g[88], g[89], 
    g[90], g[91], g[92], g[93], g[94], g[95], g[96], g[97], g[98], g[99], 
    g[100], g[101], g[102], g[103], g[104], g[105], g[106], g[107], g[108], 
    g[109], g[110], g[111], g[112], g[113], g[114], g[115], g[116], g[117], 
    g[118], g[119], g[120], g[121], g[122], g[123], g[124], g[125], g[126], 
    g[127], g[128], g[129], g[130], g[131], g[132], g[133], g[134], g[135], 
    g[136], g[137], g[138], g[139], g[140], g[141], g[142], g[143], g[144], 
    g[145], g[146], g[147], g[148], g[149], g[150], g[151], g[152], g[153], 
    g[154], g[155], g[156], g[157], g[158], g[159], g[160], g[161], g[162], 
    g[163], g[164], g[165], g[166], g[167], g[168], g[169], g[170], g[171], 
    g[172], g[173], g[174], g[175], g[176], g[177], g[178], g[179], g[180], 
    g[181], g[182], g[183], g[184], g[185], g[186], g[187], g[188], g[189], 
    g[190], g[191], g[192], g[193], g[194], g[195], g[196], g[197], g[198], 
    g[199], g[200], g[201], g[202], g[203], g[204], g[205], g[206], g[207], 
    g[208], g[209], g[210], g[211], g[212], g[213], g[214], g[215], g[216], 
    g[217], g[218], g[219], g[220], g[221], g[222], g[223], g[224], g[225], 
    g[226], g[227], g[228], g[229], g[230], g[231], g[232], g[233], g[234], 
    g[235], g[236], g[237], g[238], g[239], g[240], g[241], g[242], g[243], 
    g[244], g[245], g[246], g[247], g[248], g[249], g[250], g[251], g[252], 
    g[253], g[254], g[255], g[256], g[257], g[258], g[259], g[260], g[261], 
    g[262], g[263], g[264], g[265], g[266], g[267], g[268], g[269], g[270], 
    g[271], g[272], g[273], g[274], g[275], g[276], g[277], g[278], g[279], 
    g[280], g[281], g[282], g[283], g[284], g[285], g[286], g[287], g[288], 
    g[289], g[290], g[291], g[292], g[293], g[294], g[295], g[296], g[297], 
    g[298], g[299], g[300], g[301], g[302], g[303], g[304], g[305], g[306]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5564, 
    farPlane=56.5806, width=0.129924, height=0.0665442, cameraPosition=(
    -1.47967, -0.00312114, 56.5685), cameraTarget=(-1.47967, -0.00312114, 0))
s1.Line(point1=(-1.5, -0.003458), point2=(-1.5, 0.003458))
s1.VerticalConstraint(entity=g[307], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5539, 
    farPlane=56.5832, width=0.177756, height=0.0910425, cameraPosition=(
    -1.45935, -0.00280474, 56.5685), cameraTarget=(-1.45935, -0.00280474, 0))
s1.undo()
s1.Line(point1=(-1.5, 0.003458), point2=(-1.5, -0.003458))
s1.VerticalConstraint(entity=g[307], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5251, 
    farPlane=56.612, width=0.527969, height=0.270413, cameraPosition=(-1.30874, 
    0.0142679, 56.5685), cameraTarget=(-1.30874, 0.0142679, 0))
s1.offset(distance=0.002, objectList=(g[7], g[8], g[9], g[10], g[11], g[12], 
    g[13], g[14], g[15], g[16], g[17], g[18], g[19], g[20], g[21], g[22], 
    g[23], g[24], g[25], g[26], g[27], g[28], g[29], g[30], g[31], g[32], 
    g[33], g[34], g[35], g[36], g[37], g[38], g[39], g[40], g[41], g[42], 
    g[43], g[44], g[45], g[46], g[47], g[48], g[49], g[50], g[51], g[52], 
    g[53], g[54], g[55], g[56], g[57], g[58], g[59], g[60], g[61], g[62], 
    g[63], g[64], g[65], g[66], g[67], g[68], g[69], g[70], g[71], g[72], 
    g[73], g[74], g[75], g[76], g[77], g[78], g[79], g[80], g[81], g[82], 
    g[83], g[84], g[85], g[86], g[87], g[88], g[89], g[90], g[91], g[92], 
    g[93], g[94], g[95], g[96], g[97], g[98], g[99], g[100], g[101], g[102], 
    g[103], g[104], g[105], g[106], g[107], g[108], g[109], g[110], g[111], 
    g[112], g[113], g[114], g[115], g[116], g[117], g[118], g[119], g[120], 
    g[121], g[122], g[123], g[124], g[125], g[126], g[127], g[128], g[129], 
    g[130], g[131], g[132], g[133], g[134], g[135], g[136], g[137], g[138], 
    g[139], g[140], g[141], g[142], g[143], g[144], g[145], g[146], g[147], 
    g[148], g[149], g[150], g[151], g[152], g[153], g[154], g[155], g[156], 
    g[157], g[158], g[159], g[160], g[161], g[162], g[163], g[164], g[165], 
    g[166], g[167], g[168], g[169], g[170], g[171], g[172], g[173], g[174], 
    g[175], g[176], g[177], g[178], g[179], g[180], g[181], g[182], g[183], 
    g[184], g[185], g[186], g[187], g[188], g[189], g[190], g[191], g[192], 
    g[193], g[194], g[195], g[196], g[197], g[198], g[199], g[200], g[201], 
    g[202], g[203], g[204], g[205], g[206], g[207], g[208], g[209], g[210], 
    g[211], g[212], g[213], g[214], g[215], g[216], g[217], g[218], g[219], 
    g[220], g[221], g[222], g[223], g[224], g[225], g[226], g[227], g[228], 
    g[229], g[230], g[231], g[232], g[233], g[234], g[235], g[236], g[237], 
    g[238], g[239], g[240], g[241], g[242], g[243], g[244], g[245], g[246], 
    g[247], g[248], g[249], g[250], g[251], g[252], g[253], g[254], g[255], 
    g[256], g[257], g[258], g[259], g[260], g[261], g[262], g[263], g[264], 
    g[265], g[266], g[267], g[268], g[269], g[270], g[271], g[272], g[273], 
    g[274], g[275], g[276], g[277], g[278], g[279], g[280], g[281], g[282], 
    g[283], g[284], g[285], g[286], g[287], g[288], g[289], g[290], g[291], 
    g[292], g[293], g[294], g[295], g[296], g[297], g[298], g[299], g[300], 
    g[301], g[302], g[303], g[304], g[305], g[306], g[307]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.471, 
    farPlane=56.6661, width=1.185, height=0.606931, cameraPosition=(0.174552, 
    0.0319888, 56.5685), cameraTarget=(0.174552, 0.0319888, 0))
s1.ConstructionLine(point1=(-0.129362359642982, 0.0), point2=(
    -0.129362359642982, 0.0540115684270859))
s1.VerticalConstraint(entity=g[607], addUndoState=False)
s1.ConstructionLine(point1=(0.146515414118767, 0.0), point2=(0.146515414118767, 
    0.0405739694833755))
s1.VerticalConstraint(entity=g[608], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5635, 
    farPlane=56.5736, width=0.0610422, height=0.0312644, cameraPosition=(
    0.496223, 0.00294905, 56.5685), cameraTarget=(0.496223, 0.00294905, 0))
s1.ConstructionLine(point1=(0.5, 0.0), point2=(0.5, 0.00777522008866072))
s1.VerticalConstraint(entity=g[609], addUndoState=False)
s1.CoincidentConstraint(entity1=v[152], entity2=g[609], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.423, 
    farPlane=56.714, width=1.56178, height=0.799907, cameraPosition=(0.177317, 
    0.0213615, 56.5685), cameraTarget=(0.177317, 0.0213615, 0))
s1.FixedConstraint(entity=g[609])
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4514, 
    farPlane=56.6857, width=1.42346, height=0.729065, cameraPosition=(0.140521, 
    0.0251027, 56.5685), cameraTarget=(0.140521, 0.0251027, 0))
s1.DistanceDimension(entity1=g[608], entity2=g[609], textPoint=(
    0.301726847887039, 0.157374680042267), value=0.4)
session.viewports['Viewport: 1'].view.setValues(width=1.51432, height=0.775601, 
    cameraPosition=(0.130231, 0.0166598, 56.5685), cameraTarget=(0.130231, 
    0.0166598, 0))
s1.DistanceDimension(entity1=g[607], entity2=g[609], textPoint=(
    0.311280965805054, -0.221362978219986), value=0.8)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5092, 
    farPlane=56.6279, width=0.636808, height=0.326158, cameraPosition=(
    -0.127406, 0.00619983, 56.5685), cameraTarget=(-0.127406, 0.00619983, 0))
s1.breakCurve(curve1=g[393], point1=(-0.310815095901489, 0.101078651845455), 
    curve2=g[607], point2=(-0.30117255449295, 0.0922526940703392))
s1.breakCurve(curve1=g[522], point1=(-0.312422186136246, -0.0710270926356316), 
    curve2=g[607], point2=(-0.297958374023438, -0.0529740452766418))
s1.breakCurve(curve1=g[403], point1=(-0.00667387247085571, 0.106293968856335), 
    curve2=g[4], point2=(-0.00104904174804688, 0.0954621359705925))
s1.breakCurve(curve1=g[512], point1=(-0.00787916779518127, 
    -0.0758412405848503), curve2=g[4], point2=(-0.000647276639938354, 
    -0.0565846562385559))
s1.Line(point1=(-0.3, 0.104032476653665), point2=(-0.3, -0.0732975719074166))
s1.VerticalConstraint(entity=g[618], addUndoState=False)
s1.Line(point1=(0.0, -0.0767628961517199), point2=(0.0, 0.108960026953935))
s1.VerticalConstraint(entity=g[619], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.528, 
    farPlane=56.609, width=0.525569, height=0.269184, cameraPosition=(
    -0.116883, 0.00160813, 56.5685), cameraTarget=(-0.116883, 0.00160813, 0))
s1.offset(distance=0.004, objectList=(g[394], g[395], g[396], g[397], g[398], 
    g[399], g[400], g[401], g[402], g[513], g[514], g[515], g[516], g[517], 
    g[518], g[519], g[520], g[521], g[610], g[613], g[615], g[616], g[618], 
    g[619]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4967, 
    farPlane=56.6404, width=0.771671, height=0.395232, cameraPosition=(
    -0.0124266, 0.0180618, 56.5685), cameraTarget=(-0.0124266, 0.0180618, 0))
s1.offset(distance=0.008, objectList=(g[620], g[621], g[622], g[623], g[624], 
    g[625], g[626], g[627], g[628], g[629], g[630], g[631], g[632], g[633], 
    g[634], g[635], g[636], g[637], g[638], g[639], g[640], g[641], g[642], 
    g[643]), side=RIGHT)
s1.offset(distance=0.004, objectList=(g[644], g[645], g[646], g[647], g[648], 
    g[649], g[650], g[651], g[652], g[653], g[654], g[655], g[656], g[657], 
    g[658], g[659], g[660], g[661], g[662], g[663], g[664], g[665]), 
    side=RIGHT)
mdb.saveAs(pathName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil_2.cae')
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4247, 
    farPlane=56.7124, width=1.74719, height=0.89487, cameraPosition=(0.387041, 
    0.0743287, 56.5685), cameraTarget=(0.387041, 0.0743287, 0))
s1.ConstructionLine(point1=(0.394206494092941, 0.0), point2=(0.394206494092941, 
    0.0352538749575615))
s1.VerticalConstraint(entity=g[686], addUndoState=False)
#: Warning: Cannot continue yet--complete the step or cancel the procedure.
s1.DistanceDimension(entity1=g[686], entity2=g[609], textPoint=(
    0.571681261062622, 0.113403670489788), value=0.1)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.553, 
    farPlane=56.584, width=0.166417, height=0.0852351, cameraPosition=(
    0.409174, 0.0493501, 56.5685), cameraTarget=(0.409174, 0.0493501, 0))
s1.breakCurve(curve1=g[421], point1=(0.398726880550385, 0.0700560212135315), 
    curve2=g[686], point2=(0.399671852588654, 0.0647091716527939))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.541, 
    farPlane=56.596, width=0.295216, height=0.151203, cameraPosition=(0.402593, 
    -0.0102584, 56.5685), cameraTarget=(0.402593, -0.0102584, 0))
s1.breakCurve(curve1=g[494], point1=(0.395980894565582, -0.0546149648725986), 
    curve2=g[686], point2=(0.399333536624908, -0.0484775751829147))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5303, 
    farPlane=56.6068, width=0.410763, height=0.210383, cameraPosition=(
    0.434042, 0.00895476, 56.5685), cameraTarget=(0.434042, 0.00895476, 0))
s1.offset(distance=0.004, objectList=(g[422], g[423], g[424], g[425], g[426], 
    g[427], g[428], g[429], g[430], g[431], g[432], g[433], g[434], g[435], 
    g[436], g[437], g[438], g[439], g[440], g[441], g[442], g[443], g[444], 
    g[445], g[446], g[447], g[448], g[449], g[450], g[451], g[452], g[453], 
    g[454], g[455], g[456], g[457], g[458], g[459], g[460], g[461], g[462], 
    g[463], g[464], g[465], g[466], g[467], g[468], g[469], g[470], g[471], 
    g[472], g[473], g[474], g[475], g[476], g[477], g[478], g[479], g[480], 
    g[481], g[482], g[483], g[484], g[485], g[486], g[487], g[488], g[489], 
    g[490], g[491], g[492], g[493], g[687], g[690]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5604, 
    farPlane=56.5767, width=0.0874557, height=0.0447928, cameraPosition=(
    0.411915, -0.0539094, 56.5685), cameraTarget=(0.411915, -0.0539094, 0))
s1.Line(point1=(0.39919555399686, -0.0495587563951101), point2=(0.4, 
    -0.0534770298194744))
s1.PerpendicularConstraint(entity1=g[764], entity2=g[765], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.554, 
    farPlane=56.5831, width=0.156414, height=0.0801116, cameraPosition=(
    0.404865, 0.0439755, 56.5685), cameraTarget=(0.404865, 0.0439755, 0))
s1.Line(point1=(0.4, 0.0701776736341914), point2=(0.398882691934157, 
    0.066336889510337))
s1.PerpendicularConstraint(entity1=g[687], entity2=g[766], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5234, 
    farPlane=56.6137, width=0.484247, height=0.24802, cameraPosition=(0.404096, 
    0.0269348, 56.5685), cameraTarget=(0.404096, 0.0269348, 0))
s1.ConstructionLine(point1=(0.37858521938324, 0.0), point2=(0.37858521938324, 
    0.029832947999239))
s1.VerticalConstraint(entity=g[767], addUndoState=False)
s1.DistanceDimension(entity1=g[767], entity2=g[686], textPoint=(
    0.398749440908432, 0.0990832448005676), value=0.004)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5589, 
    farPlane=56.5781, width=0.103101, height=0.052806, cameraPosition=(
    0.397992, 0.0588252, 56.5685), cameraTarget=(0.397992, 0.0588252, 0))
s1.breakCurve(curve1=g[688], point1=(0.392625451087952, 0.0723027586936951), 
    curve2=g[767], point2=(0.395617634057999, 0.070289246737957))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5549, 
    farPlane=56.5822, width=0.146097, height=0.0748274, cameraPosition=(
    0.397276, -0.0296675, 56.5685), cameraTarget=(0.397276, -0.0296675, 0))
s1.breakCurve(curve1=g[689], point1=(0.392436742782593, -0.0551161244511604), 
    curve2=g[767], point2=(0.396031528711319, -0.0521708913147449))
s1.Line(point1=(0.396, -0.0542982547977557), point2=(0.39919555399686, 
    -0.0495587563951101))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5579, 
    farPlane=56.5792, width=0.114532, height=0.0586604, cameraPosition=(
    0.398529, 0.0584767, 56.5685), cameraTarget=(0.398529, 0.0584767, 0))
s1.Line(point1=(0.398882691934157, 0.066336889510337), point2=(0.396, 
    0.071341298591928))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.503, 
    farPlane=56.6341, width=0.796384, height=0.407889, cameraPosition=(
    0.208951, 0.006885, 56.5685), cameraTarget=(0.208951, 0.006885, 0))
s1.offset(distance=0.004, objectList=(g[404], g[405], g[406], g[407], g[408], 
    g[409], g[410], g[411], g[412], g[413], g[414], g[415], g[416], g[417], 
    g[418], g[419], g[420], g[495], g[496], g[497], g[498], g[499], g[500], 
    g[501], g[502], g[503], g[504], g[505], g[506], g[507], g[508], g[509], 
    g[510], g[511], g[614], g[617], g[619], g[691], g[692], g[693], g[694], 
    g[695], g[696], g[697], g[698], g[699], g[700], g[701], g[702], g[703], 
    g[704], g[705], g[706], g[707], g[708], g[709], g[710], g[711], g[712], 
    g[713], g[714], g[715], g[716], g[717], g[718], g[719], g[720], g[721], 
    g[722], g[723], g[724], g[725], g[726], g[727], g[728], g[729], g[730], 
    g[731], g[732], g[733], g[734], g[735], g[736], g[737], g[738], g[739], 
    g[740], g[741], g[742], g[743], g[744], g[745], g[746], g[747], g[748], 
    g[749], g[750], g[751], g[752], g[753], g[754], g[755], g[756], g[757], 
    g[758], g[759], g[760], g[761], g[762], g[763], g[764], g[769], g[770], 
    g[772], g[773]), side=RIGHT)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5219, 
    farPlane=56.6152, width=0.567066, height=0.290438, cameraPosition=(
    -0.311301, 0.00589866, 56.5685), cameraTarget=(-0.311301, 0.00589866, 0))
s1.ConstructionLine(point1=(-0.384107202291489, 0.0), point2=(
    -0.384107202291489, 0.0432304814457893))
s1.VerticalConstraint(entity=g[889], addUndoState=False)
s1.DistanceDimension(entity1=g[889], entity2=g[607], textPoint=(
    -0.329368323087692, 0.122181035578251), value=0.1)
s1.breakCurve(curve1=g[390], point1=(-0.41952645778656, 0.0975313410162926), 
    curve2=g[889], point2=(-0.401280164718628, 0.08717130869627))
s1.breakCurve(curve1=g[525], point1=(-0.408793330192566, -0.0689435973763466), 
    curve2=g[889], point2=(-0.399491310119629, -0.0589408129453659))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5241, 
    farPlane=56.613, width=0.477075, height=0.244347, cameraPosition=(
    -0.324139, -0.00616506, 56.5685), cameraTarget=(-0.324139, -0.00616506, 0))
s1.offset(distance=0.004, objectList=(g[391], g[392], g[523], g[524], g[611], 
    g[612], g[618], g[890], g[893]), side=RIGHT)
s1.Line(point1=(-0.4, 0.100090678524562), point2=(-0.399817679888691, 
    0.096094835762764))
s1.PerpendicularConstraint(entity1=g[890], entity2=g[903], addUndoState=False)
s1.Line(point1=(-0.399870866156106, -0.066517268509113), point2=(-0.4, 
    -0.0705151835220115))
s1.PerpendicularConstraint(entity1=g[902], entity2=g[904], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.518, 
    farPlane=56.619, width=0.542131, height=0.277667, cameraPosition=(
    -0.347013, -0.000213888, 56.5685), cameraTarget=(-0.347013, -0.000213888, 
    0))
s1.ConstructionLine(point1=(-0.434746205806732, 0.0), point2=(
    -0.434746205806732, 0.0248888470232487))
s1.VerticalConstraint(entity=g[905], addUndoState=False)
#: Warning: Cannot continue yet--complete the step or cancel the procedure.
s1.DistanceDimension(entity1=g[905], entity2=g[889], textPoint=(
    -0.410119414329529, 0.0498207993805408), value=0.004)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5445, 
    farPlane=56.5926, width=0.258011, height=0.132147, cameraPosition=(
    -0.355304, 0.0467942, 56.5685), cameraTarget=(-0.355304, 0.0467942, 0))
s1.breakCurve(curve1=g[891], point1=(-0.412034153938293, 0.0995393395423889), 
    curve2=g[905], point2=(-0.403406649827957, 0.0951506942510605))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5508, 
    farPlane=56.5863, width=0.190908, height=0.0977786, cameraPosition=(
    -0.384237, -0.0421059, 56.5685), cameraTarget=(-0.384237, -0.0421059, 0))
s1.breakCurve(curve1=g[892], point1=(-0.411156684160233, -0.0701886564493179), 
    curve2=g[905], point2=(-0.404170751571655, -0.0671819373965263))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5576, 
    farPlane=56.5795, width=0.117326, height=0.0600915, cameraPosition=(
    -0.379604, 0.0834755, 56.5685), cameraTarget=(-0.379604, 0.0834755, 0))
s1.Line(point1=(-0.404, 0.0999081687287791), point2=(-0.399817679888691, 
    0.096094835762764))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5644, 
    farPlane=56.5726, width=0.0439527, height=0.0225115, cameraPosition=(
    -0.393404, 0.0900287, 56.5685), cameraTarget=(-0.393404, 0.0900287, 0))
s1.delete(objectList=(g[903], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.562, 
    farPlane=56.575, width=0.0697834, height=0.0357415, cameraPosition=(
    -0.391653, -0.0658145, 56.5685), cameraTarget=(-0.391653, -0.0658145, 0))
s1.Line(point1=(-0.399870866156106, -0.066517268509113), point2=(-0.404, 
    -0.0703859823327612))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5668, 
    farPlane=56.5703, width=0.0190299, height=0.00974669, cameraPosition=(
    -0.398388, -0.0688259, 56.5685), cameraTarget=(-0.398388, -0.0688259, 0))
s1.delete(objectList=(g[904], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.563, 
    farPlane=56.5741, width=0.0594635, height=0.0304558, cameraPosition=(
    0.396225, -0.049341, 56.5685), cameraTarget=(0.396225, -0.049341, 0))
s1.delete(objectList=(g[765], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5557, 
    farPlane=56.5814, width=0.137974, height=0.070667, cameraPosition=(
    0.403291, 0.0444038, 56.5685), cameraTarget=(0.403291, 0.0444038, 0))
s1.delete(objectList=(g[766], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.553, 
    farPlane=56.5841, width=0.167194, height=0.0856328, cameraPosition=(
    -0.0185532, 0.0831239, 56.5685), cameraTarget=(-0.0185532, 0.0831239, 0))
s1.FilletByRadius(radius=0.002, curve1=g[619], nearPoint1=(
    0.000170420855283737, 0.107507690787315), curve2=g[615], nearPoint2=(
    -0.00172831490635872, 0.108771644532681))
#* A fillet cannot be created at a vertex shared by more than two entities.
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5538, 
    farPlane=56.5832, width=0.157805, height=0.0808241, cameraPosition=(
    0.00506294, 0.0883542, 56.5685), cameraTarget=(0.00506294, 0.0883542, 0))
s1.CircleByCenterPerimeter(center=(-0.00285221869125962, 0.106894999742508), 
    point1=(0.0, 0.106894999742508))
s1.CoincidentConstraint(entity1=v[881], entity2=g[4], addUndoState=False)
s1.TangentConstraint(entity1=g[912], entity2=g[4])
s1.TangentConstraint(entity1=g[912], entity2=g[615])
s1.undo()
s1.TangentConstraint(entity1=g[615], entity2=g[912])
s1.undo()
s1.FixedConstraint(entity=g[615])
s1.TangentConstraint(entity1=g[615], entity2=g[912])
s1.delete(objectList=(c[1827], ))
s1.RadialDimension(curve=g[912], textPoint=(-0.00872634537518024, 
    0.101327776908875), radius=0.002)
s1.undo()
s1.FixedConstraint(entity=g[615])
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5346, 
    farPlane=56.6025, width=0.412704, height=0.211377, cameraPosition=(
    0.0310934, 0.0379007, 56.5685), cameraTarget=(0.0310934, 0.0379007, 0))
s1.FixedConstraint(entity=g[4])
s1.FixedConstraint(entity=g[619])
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5567, 
    farPlane=56.5804, width=0.12737, height=0.065236, cameraPosition=(
    0.0118628, 0.0928746, 56.5685), cameraTarget=(0.0118628, 0.0928746, 0))
s1.RadialDimension(curve=g[912], textPoint=(-0.00730296038091183, 
    0.100136443972588), radius=0.002)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5635, 
    farPlane=56.5736, width=0.0608661, height=0.0311742, cameraPosition=(
    0.00665326, 0.101025, 56.5685), cameraTarget=(0.00665326, 0.101025, 0))
s1.FixedConstraint(entity=g[614])
s1.CircleByCenterPerimeter(center=(0.00256352033466101, 0.106834165751934), 
    point1=(0.00379236321896315, 0.106987543404102))
s1.TangentConstraint(entity1=g[913], entity2=g[4])
s1.TangentConstraint(entity1=g[913], entity2=g[614])
s1.RadialDimension(curve=g[913], textPoint=(0.0018722964450717, 
    0.103191427886486), radius=0.002)
s1.autoTrimCurve(curve1=g[912], point1=(-0.00358068663626909, 
    0.108252920210361))
s1.autoTrimCurve(curve1=g[913], point1=(0.00363875646144152, 
    0.108214572072029))
s1.autoTrimCurve(curve1=g[916], point1=(0.00386916380375624, 
    0.106795825064182))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5644, 
    farPlane=56.5727, width=0.0446698, height=0.0228789, cameraPosition=(
    0.00535271, 0.102932, 56.5685), cameraTarget=(0.00535271, 0.102932, 0))
s1.autoTrimCurve(curve1=g[619], point1=(1.20596960186958e-05, 
    0.108348786830902))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5634, 
    farPlane=56.5737, width=0.0549221, height=0.0281298, cameraPosition=(
    0.00545748, -0.0794911, 56.5685), cameraTarget=(0.00545748, -0.0794911, 0))
s1.FixedConstraint(entity=g[4])
s1.FixedConstraint(entity=g[918])
s1.FixedConstraint(entity=g[617])
s1.FixedConstraint(entity=g[616])
s1.CircleByCenterPerimeter(center=(-0.0025989105924964, -0.0748720094561577), 
    point1=(-0.00142077077180147, -0.0752526074647903))
s1.CircleByCenterPerimeter(center=(0.00169783178716898, -0.0748720094561577), 
    point1=(0.00280666816979647, -0.0750104039907455))
s1.TangentConstraint(entity1=g[919], entity2=g[616])
s1.TangentConstraint(entity1=g[919], entity2=g[4])
s1.TangentConstraint(entity1=g[920], entity2=g[617])
s1.TangentConstraint(entity1=g[920], entity2=g[4])
s1.RadialDimension(curve=g[919], textPoint=(-0.00384635385125875, 
    -0.0740762054920197), radius=0.002)
s1.RadialDimension(curve=g[920], textPoint=(0.0013166693970561, 
    -0.0733150094747543), radius=0.002)
s1.autoTrimCurve(curve1=g[919], point1=(-0.00381170306354761, 
    -0.0753564089536667))
s1.autoTrimCurve(curve1=g[920], point1=(0.000311785377562046, 
    -0.0737302079796791))
s1.autoTrimCurve(curve1=g[922], point1=(0.00398480799049139, 
    -0.0754602029919624))
s1.autoTrimCurve(curve1=g[918], point1=(0.0, -0.0760830044746399))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5665, 
    farPlane=56.5706, width=0.0217103, height=0.0111195, cameraPosition=(
    0.00206924, -0.0773368, 56.5685), cameraTarget=(0.00206924, -0.0773368, 0))
s1.autoTrimCurve(curve1=g[921], point1=(-1.96017790585756e-05, 
    -0.0745535045862198))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5539, 
    farPlane=56.5832, width=0.156958, height=0.0803902, cameraPosition=(
    0.00282891, 0.0736659, 56.5685), cameraTarget=(0.00282891, 0.0736659, 0))
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
s1.FilletByRadius(radius=0.002, curve1=g[629], nearPoint1=(-0.0037563880905509, 
    0.102885253727436), curve2=g[628], nearPoint2=(-0.00534082110971212, 
    0.104566223919392))
s1.FilletByRadius(radius=0.002, curve1=g[887], nearPoint1=(0.00565118435770273, 
    0.104961752891541), curve2=g[886], nearPoint2=(0.00376966688781977, 
    0.103280767798424))
s1.FilletByRadius(radius=0.002, curve1=g[652], nearPoint1=(-0.0121736964210868, 
    0.095568060874939), curve2=g[651], nearPoint2=(-0.0135600669309497, 
    0.0967546328902245))
s1.FilletByRadius(radius=0.002, curve1=g[672], nearPoint1=(-0.0161347724497318, 
    0.0912173017859459), curve2=g[671], nearPoint2=(-0.0175211541354656, 
    0.0926016345620155))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5599, 
    farPlane=56.5772, width=0.0925968, height=0.0474259, cameraPosition=(
    0.00122451, -0.0745265, 56.5685), cameraTarget=(0.00122451, -0.0745265, 0))
s1.FilletByRadius(radius=0.002, curve1=g[886], nearPoint1=(0.00388265447691083, 
    -0.0712889134883881), curve2=g[885], nearPoint2=(0.00522633315995336, 
    -0.0725139304995537))
s1.FilletByRadius(radius=0.002, curve1=g[630], nearPoint1=(
    -0.00505571020767093, -0.0726889371871948), curve2=g[629], nearPoint2=(
    -0.00417939899489284, -0.0719305872917175))
s1.FilletByRadius(radius=0.002, curve1=g[653], nearPoint1=(-0.0134098716080189, 
    -0.0648721158504486), curve2=g[652], nearPoint2=(-0.0121830329298973, 
    -0.0637637600302696))
s1.FilletByRadius(radius=0.002, curve1=g[673], nearPoint1=(-0.0182587876915932, 
    -0.060788705945015), curve2=g[672], nearPoint2=(-0.0162140652537346, 
    -0.0594470091164112))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5655, 
    farPlane=56.5715, width=0.0364936, height=0.0186912, cameraPosition=(
    -0.289258, 0.0936238, 56.5685), cameraTarget=(-0.289258, 0.0936238, 0))
s1.FilletByRadius(radius=0.002, curve1=g[642], nearPoint1=(-0.295463413000107, 
    0.100141614675522), curve2=g[641], nearPoint2=(-0.295946925878525, 
    0.0993369519710541))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5636, 
    farPlane=56.5735, width=0.0601128, height=0.0307884, cameraPosition=(
    -0.284805, 0.0894968, 56.5685), cameraTarget=(-0.284805, 0.0894968, 0))
s1.FilletByRadius(radius=0.002, curve1=g[664], nearPoint1=(-0.285999417304993, 
    0.0923181176185608), curve2=g[663], nearPoint2=(-0.287743985652924, 
    0.090424619615078))
s1.FilletByRadius(radius=0.002, curve1=g[683], nearPoint1=(-0.28235849738121, 
    0.0884932428598404), curve2=g[682], nearPoint2=(-0.283875554800034, 
    0.0865618735551834))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5624, 
    farPlane=56.5747, width=0.0658037, height=0.0337031, cameraPosition=(
    -0.280128, -0.0588011, 56.5685), cameraTarget=(-0.280128, -0.0588011, 0))
s1.FilletByRadius(radius=0.002, curve1=g[682], nearPoint1=(-0.284175843000412, 
    -0.0567075684666634), curve2=g[681], nearPoint2=(-0.283262461423874, 
    -0.0574952214956284))
s1.FilletByRadius(radius=0.002, curve1=g[663], nearPoint1=(-0.28824445605278, 
    -0.0594436191022396), curve2=g[662], nearPoint2=(-0.28637620806694, 
    -0.0616822019219399))
s1.FilletByRadius(radius=0.002, curve1=g[641], nearPoint1=(-0.295883506536484, 
    -0.067693218588829), curve2=g[639], nearPoint2=(-0.294388920068741, 
    -0.0693928897380829))
#* A fillet cannot be created at a vertex shared by more than two entities.
s1.FilletByRadius(radius=0.002, curve1=g[641], nearPoint1=(-0.296091079711914, 
    -0.0675688534975052), curve2=g[640], nearPoint2=(-0.295675933361053, 
    -0.0694343447685242))
s1.autoTrimCurve(curve1=g[639], point1=(-0.295219242572784, 
    -0.0695172548294067))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5666, 
    farPlane=56.5704, width=0.0203917, height=0.0104441, cameraPosition=(
    -0.289251, -0.0676365, 56.5685), cameraTarget=(-0.289251, -0.0676365, 0))
s1.autoTrimCurve(curve1=g[640], point1=(-0.294931054115295, 
    -0.0694543123245239))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5669, 
    farPlane=56.5701, width=0.0170946, height=0.00875544, cameraPosition=(
    -0.291919, 0.099106, 56.5685), cameraTarget=(-0.291919, 0.099106, 0))
s1.autoTrimCurve(curve1=g[642], point1=(-0.294760644435883, 0.100296013057232))
s1.autoTrimCurve(curve1=g[934], point1=(-0.294933199882507, 0.100091397762299))
s1.undo()
s1.autoTrimCurve(curve1=g[643], point1=(-0.294933199882507, 0.100231394171715))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5613, 
    farPlane=56.5758, width=0.0879927, height=0.0450678, cameraPosition=(
    -0.286617, 0.0918249, 56.5685), cameraTarget=(-0.286617, 0.0918249, 0))
s1.FilletByRadius(radius=0.002, curve1=g[898], nearPoint1=(-0.30402085185051, 
    0.0985047221183777), curve2=g[897], nearPoint2=(-0.305852890014648, 
    0.0997796952724457))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5554, 
    farPlane=56.5817, width=0.140851, height=0.0721405, cameraPosition=(
    -0.298513, -0.0598634, 56.5685), cameraTarget=(-0.298513, -0.0598634, 0))
s1.FilletByRadius(radius=0.002, curve1=g[899], nearPoint1=(-0.30655500292778, 
    -0.0686924159526825), curve2=g[898], nearPoint2=(-0.303889065980911, 
    -0.0664740800857544))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.343, 
    farPlane=56.7941, width=2.7394, height=1.40306, cameraPosition=(-0.259516, 
    -0.169425, 56.5685), cameraTarget=(-0.259516, -0.169425, 0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
#* Feature creation failed.
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.2945, 
    farPlane=56.8426, width=3.55581, height=1.82121, cameraPosition=(0.148056, 
    -0.16353, 56.5685), cameraTarget=(0.148056, -0.16353, 0))
mdb.models['Model-1'].ConstrainedSketch(name='Sketch-2', objectToCopy=s1)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e, d1 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
#* Feature creation failed.
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4935, 
    farPlane=56.6436, width=0.805393, height=0.412503, cameraPosition=(
    -0.115262, 0.0261846, 56.5685), cameraTarget=(-0.115262, 0.0261846, 0))
s1.delete(objectList=(g[607], g[618], g[641], g[663], g[682], g[898], c[1212]))
s1.delete(objectList=(g[4], g[629], g[652], g[672], g[886], g[924]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5199, 
    farPlane=56.6172, width=0.591081, height=0.302738, cameraPosition=(
    -0.139173, -0.00490754, 56.5685), cameraTarget=(-0.139173, -0.00490754, 0))
s1.delete(objectList=(g[653], g[654], g[655], g[656], g[657], g[658], g[659], 
    g[660], g[661], g[662], g[673], g[674], g[675], g[676], g[677], g[678], 
    g[679], g[680], g[681], g[932], g[933], g[937], g[938], d[16], d[17], 
    d[21], d[22], c[1932], c[1941], c[1978], c[1987]))
s1.delete(objectList=(g[644], g[645], g[646], g[647], g[648], g[649], g[650], 
    g[651], g[664], g[665], g[666], g[667], g[668], g[669], g[670], g[671], 
    g[683], g[684], g[685], g[928], g[929], g[935], g[936], d[12], d[13], 
    d[19], d[20], c[1897], c[1906], c[1959], c[1968]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5656, 
    farPlane=56.5715, width=0.0318465, height=0.016311, cameraPosition=(
    0.00335887, 0.102439, 56.5685), cameraTarget=(0.00335887, 0.102439, 0))
s1.delete(objectList=(g[914], ))
s1.delete(objectList=(g[917], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.568, 
    farPlane=56.5691, width=0.00637361, height=0.00326442, cameraPosition=(
    0.00075744, 0.105973, 56.5685), cameraTarget=(0.00075744, 0.105973, 0))
s1.delete(objectList=(g[915], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5656, 
    farPlane=56.5715, width=0.031863, height=0.0163195, cameraPosition=(
    0.00447231, -0.0719885, 56.5685), cameraTarget=(0.00447231, -0.0719885, 0))
s1.delete(objectList=(g[923], g[925]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5546, 
    farPlane=56.5825, width=0.149732, height=0.0766893, cameraPosition=(
    0.0100062, 0.0747152, 56.5685), cameraTarget=(0.0100062, 0.0747152, 0))
s1.Line(point1=(-0.004, -0.0707829007268361), point2=(-0.004, 
    0.102994935862258))
s1.VerticalConstraint(entity=g[944], addUndoState=False)
s1.TangentConstraint(entity1=g[931], entity2=g[944], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5573, 
    farPlane=56.5798, width=0.121079, height=0.0620141, cameraPosition=(
    0.0169949, -0.068226, 56.5685), cameraTarget=(0.0169949, -0.068226, 0))
s1.Line(point1=(0.004, 0.10292492454268), point2=(0.004, -0.0707428332844021))
s1.VerticalConstraint(entity=g[945], addUndoState=False)
s1.TangentConstraint(entity1=g[927], entity2=g[945], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5548, 
    farPlane=56.5823, width=0.147495, height=0.0755436, cameraPosition=(
    -0.288965, 0.0764615, 56.5685), cameraTarget=(-0.288965, 0.0764615, 0))
s1.Line(point1=(-0.304, -0.0671454917521563), point2=(-0.304, 
    0.097815461737381))
s1.VerticalConstraint(entity=g[946], addUndoState=False)
s1.TangentConstraint(entity1=g[943], entity2=g[946], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5469, 
    farPlane=56.5902, width=0.232139, height=0.118896, cameraPosition=(
    -0.278431, -0.0315692, 56.5685), cameraTarget=(-0.278431, -0.0315692, 0))
s1.Line(point1=(-0.296, 0.0982419181352058), point2=(-0.296, 
    -0.0674458916718361))
s1.VerticalConstraint(entity=g[947], addUndoState=False)
s1.TangentConstraint(entity1=g[934], entity2=g[947], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.397, 
    farPlane=56.7401, width=2.08418, height=1.06747, cameraPosition=(-0.073806, 
    0.126948, 56.5685), cameraTarget=(-0.073806, 0.126948, 0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3028, 
    farPlane=56.8342, width=2.85268, height=1.46108, viewOffsetX=0.166154, 
    viewOffsetY=-0.240511)
p = mdb.models['Model-1'].parts['Part-1']
f1 = p.faces
p.RemoveFaces(faceList = f1[1:2]+f1[5:6], deleteCells=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.2534, 
    farPlane=56.8837, width=3.82737, height=1.96029, viewOffsetX=0.000261068, 
    viewOffsetY=-0.128175)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4985, 
    farPlane=56.6386, width=0.751555, height=0.384929, viewOffsetX=-0.122222, 
    viewOffsetY=0.0438632)
p = mdb.models['Model-1'].parts['Part-1']
s = p.features['Partition face-1'].sketch
mdb.models['Model-1'].ConstrainedSketch(name='__edit__', objectToCopy=s)
s2 = mdb.models['Model-1'].sketches['__edit__']
g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s2, 
    upToFeature=p.features['Partition face-1'], filter=COPLANAR_EDGES)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3956, 
    farPlane=56.432, width=0.195694, height=0.10023, cameraPosition=(0.0265212, 
    -0.0514461, 56.4138), cameraTarget=(0.0265212, -0.0514461, 0))
s2.Line(point1=(0.0, 0.108960026953935), point2=(0.0, -0.0767628961517199))
s2.VerticalConstraint(entity=g[948], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4005, 
    farPlane=56.4271, width=0.143192, height=0.0733398, cameraPosition=(
    -0.275141, -0.0508127, 56.4138), cameraTarget=(-0.275141, -0.0508127, 0))
s2.Line(point1=(-0.3, 0.104032476653665), point2=(-0.3, -0.0732975719074166))
s2.VerticalConstraint(entity=g[949], addUndoState=False)
s2.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
p.features['Partition face-1'].setValues(sketch=s2)
del mdb.models['Model-1'].sketches['__edit__']
p = mdb.models['Model-1'].parts['Part-1']
p.regenerate()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3579, 
    farPlane=56.7792, width=2.55879, height=1.31055, viewOffsetX=-0.0416142, 
    viewOffsetY=0.0673993)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3865, 
    farPlane=56.7505, width=1.95395, height=1.00077, viewOffsetX=-0.521387, 
    viewOffsetY=0.0646009)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='skin')
mdb.models['Model-1'].materials['skin'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['skin'].Elastic(table=((1.0, 0.0), ))
mdb.models['Model-1'].Material(name='cfrp')
mdb.models['Model-1'].materials['cfrp'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['cfrp'].Elastic(type=ENGINEERING_CONSTANTS, 
    table=((10.0, 20.0, 30.0, 0.12, 0.13, 0.23, 1.2, 1.3, 2.3), ))
mdb.models['Model-1'].Material(name='foam')
mdb.models['Model-1'].materials['foam'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['foam'].Elastic(table=((1.0, 0.0), ))
mdb.models['Model-1'].Material(name='honeycomb')
mdb.models['Model-1'].materials['honeycomb'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['honeycomb'].Elastic(
    type=ENGINEERING_CONSTANTS, table=((10.0, 20.0, 30.0, 0.12, 0.13, 0.23, 
    1.2, 1.3, 2.3), ))
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
mdb.models['Model-1'].HomogeneousSolidSection(name='skin', material='skin', 
    thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='foam', material='foam', 
    thickness=None)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.512, 
    farPlane=56.6251, width=0.606849, height=0.310814, viewOffsetX=-0.13472, 
    viewOffsetY=0.0211094)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#8 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#0:10 #fffff000 #77 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-1')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='cfrp', description='', elementType=SOLID, symmetric=False, 
    thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='cfrp', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=0.0, 
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4437, 
    farPlane=56.6934, width=1.3407, height=0.686676, viewOffsetX=-0.29044, 
    viewOffsetY=0.0620945)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#40 ]', ), )
region = p.Set(faces=faces, name='Set-3')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='skin', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5003, 
    farPlane=56.6368, width=0.732177, height=0.375004, viewOffsetX=0.277569, 
    viewOffsetY=-0.00549098)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#4 ]', ), )
region = p.Set(faces=faces, name='Set-4')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='foam', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
mdb.models['Model-1'].Material(name='metal')
mdb.models['Model-1'].materials['metal'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['metal'].Elastic(table=((1.0, 0.0), ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5398, 
    farPlane=56.5972, width=0.308113, height=0.157808, viewOffsetX=0.465675, 
    viewOffsetY=0.0143269)
mdb.models['Model-1'].HomogeneousSolidSection(name='metal', material='metal', 
    thickness=None)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#2 ]', ), )
region = p.Set(faces=faces, name='Set-5')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='metal', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5068, 
    farPlane=56.6303, width=0.75042, height=0.384347, viewOffsetX=0.220166, 
    viewOffsetY=-0.0073656)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#ffffffff:3 #1fffff ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-6')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='cfrp_le', description='', elementType=SOLID, symmetric=False, 
    thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='cfrp', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=45.0, 
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5217, 
    farPlane=56.6154, width=0.5695, height=0.291685, viewOffsetX=-0.30662, 
    viewOffsetY=0.018355)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#20 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#0:9 #100000 #0:6 #fe000000 #7 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-8')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='cfrp_back', description='', elementType=SOLID, symmetric=False, 
    thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='cfrp', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=60.0, 
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4329, 
    farPlane=56.7042, width=1.45617, height=0.745817, viewOffsetX=-0.494447, 
    viewOffsetY=0.0309071)
mdb.models['Model-1'].HomogeneousSolidSection(name='honeycomb', 
    material='honeycomb', thickness=None)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#10 ]', ), )
region = p.Set(faces=faces, name='Set-10')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='honeycomb', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#10 ]', ), )
region = regionToolset.Region(faces=faces)
mdb.models['Model-1'].parts['Part-1'].MaterialOrientation(region=region, 
    orientationType=DISCRETE, axis=AXIS_3, normalAxisDefinition=VECTOR, 
    normalAxisVector=(0.0, 0.0, 1.0), flipNormalDirection=False, 
    normalAxisDirection=AXIS_3, primaryAxisDefinition=VECTOR, 
    primaryAxisVector=(1.0, 0.0, 0.0), primaryAxisDirection=AXIS_1, 
    flipPrimaryDirection=False, additionalRotationType=ROTATION_NONE, 
    angle=0.0, additionalRotationField='', stackDirection=STACK_3)
#: Specified material orientation has been assigned to the selected regions.
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3579, 
    farPlane=56.7792, width=2.73322, height=1.39989, viewOffsetX=-0.219219, 
    viewOffsetY=0.240765)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Section']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4608, 
    farPlane=56.6763, width=1.3085, height=0.670185, viewOffsetX=-0.103619, 
    viewOffsetY=0.0368732)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Material']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3536, 
    farPlane=56.7835, width=2.30738, height=1.18178, viewOffsetX=-0.437504, 
    viewOffsetY=-0.0276225)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
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
p.seedPart(size=0.002, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5019, 
    farPlane=56.6352, width=0.713984, height=0.366611, viewOffsetX=-0.206883, 
    viewOffsetY=-0.00829188)
p = mdb.models['Model-1'].parts['Part-1']
p.deleteMesh()
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=0.1, deviationFactor=0.1, minSizeValue=0.002)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3828, 
    farPlane=56.7543, width=1.98923, height=1.02141, viewOffsetX=-0.155865, 
    viewOffsetY=0.0658114)
p = mdb.models['Model-1'].parts['Part-1']
p.deleteMesh()
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=0.01, deviationFactor=0.1, minSizeValue=0.002)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3036, 
    farPlane=56.8335, width=2.83773, height=1.4571, viewOffsetX=-0.411649, 
    viewOffsetY=0.174186)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='sg2_airfoil_2', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
    numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
    numCpus=1, numGPUs=0)
mdb.jobs['sg2_airfoil_2'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_airfoil_2.inp".
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae".
