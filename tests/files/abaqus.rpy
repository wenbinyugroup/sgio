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
