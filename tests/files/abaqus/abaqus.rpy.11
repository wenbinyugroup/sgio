# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2017 replay file
# Internal Version: 2016_09_27-17.54.59 126836
# Run by tian50 on Thu Nov 02 10:38:45 2023
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
openMdb(pathName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil_2.cae')
#: The model database "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_2.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
openMdb(
    pathName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil_composite_section.cae')
#: The model database "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil_composite_section.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
Mdb()
#: A new model database has been created.
#: The model "Model-1" has been created.
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
s1.ConstructionLine(point1=(-1.0575, 0.0), point2=(1.41, 0.0))
s1.HorizontalConstraint(entity=g[3], addUndoState=False)
s1.ConstructionLine(point1=(0.0, -1.0575), point2=(0.0, 1.05750000005588))
s1.VerticalConstraint(entity=g[4], addUndoState=False)
s1.FixedConstraint(entity=v[0])
s1.FixedConstraint(entity=g[3])
s1.FixedConstraint(entity=g[4])
s1.retrieveSketch(sketch=mdb.models['Model-1'].sketches['airfoil'])
session.viewports['Viewport: 1'].view.fitView()
#: Info: 300 entities copied from airfoil.
session.viewports['Viewport: 1'].view.setValues(nearPlane=55.4604, 
    farPlane=57.6767, width=11.8948, height=6.09223, cameraPosition=(0.0431988, 
    -0.678937, 56.5685), cameraTarget=(0.0431988, -0.678937, 0))
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
s1.scale(scaleValue=1.73, scaleCenter=(0.0, 0.0), objectList=(g[7], g[8], g[9], 
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.556, 
    farPlane=56.5811, width=0.134943, height=0.0691145, cameraPosition=(
    -1.28117, -0.00542177, 56.5685), cameraTarget=(-1.28117, -0.00542177, 0))
s1.Line(point1=(-1.2975, 0.00299117), point2=(-1.2975, -0.00299117))
s1.VerticalConstraint(entity=g[307], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3567, 
    farPlane=56.7804, width=2.57377, height=1.31822, cameraPosition=(-0.369429, 
    0.119494, 56.5685), cameraTarget=(-0.369429, 0.119494, 0))
s1.offset(distance=0.00045, objectList=(g[7], g[8], g[9], g[10], g[11], g[12], 
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4277, 
    farPlane=56.7093, width=1.71042, height=0.876037, cameraPosition=(
    -0.105994, -0.0120329, 56.5685), cameraTarget=(-0.105994, -0.0120329, 0))
s1.ConstructionLine(point1=(0.095263659954071, 0.0), point2=(0.095263659954071, 
    0.0456153303384781))
s1.VerticalConstraint(entity=g[609], addUndoState=False)
s1.ConstructionLine(point1=(-0.283510684967041, 0.0), point2=(
    -0.283510684967041, 0.0305298119783401))
s1.VerticalConstraint(entity=g[610], addUndoState=False)
s1.DistanceDimension(entity1=g[4], entity2=g[609], textPoint=(
    0.0607315897941589, 0.151213899254799), value=0.0865)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4362, 
    farPlane=56.7009, width=1.42065, height=0.727623, cameraPosition=(
    -0.0190969, 0.0611089, 56.5685), cameraTarget=(-0.0190969, 0.0611089, 0))
s1.DistanceDimension(entity1=g[610], entity2=g[4], textPoint=(
    -0.0724272355437279, 0.129575207829475), value=0.02595)
s1.delete(objectList=(d[1], ))
#: Warning: Cannot continue yet--complete the step or cancel the procedure.
#: Warning: Cannot continue yet--complete the step or cancel the procedure.
s1.DistanceDimension(entity1=g[610], entity2=g[4], textPoint=(
    -0.00789310783147812, 0.122415289282799), value=0.2595)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5664, 
    farPlane=56.5707, width=0.0227836, height=0.0116692, cameraPosition=(
    -0.258338, 0.088901, 56.5685), cameraTarget=(-0.258338, 0.088901, 0))
s1.breakCurve(curve1=g[394], point1=(-0.26031482219696, 0.0911759957671165), 
    curve2=g[610], point2=(-0.259509861469269, 0.0906592756509781))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5663, 
    farPlane=56.5708, width=0.0239553, height=0.0122693, cameraPosition=(
    -0.25417, -0.0666411, 56.5685), cameraTarget=(-0.25417, -0.0666411, 0))
s1.breakCurve(curve1=g[523], point1=(-0.260495364665985, -0.0646565854549408), 
    curve2=g[610], point2=(-0.259467631578445, -0.0641585662961006))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5651, 
    farPlane=56.5719, width=0.0364679, height=0.018678, cameraPosition=(
    0.0984231, 0.0920237, 56.5685), cameraTarget=(0.0984231, 0.0920237, 0))
s1.breakCurve(curve1=g[408], point1=(0.0857340693473816, 0.0937122628092766), 
    curve2=g[609], point2=(0.0864703357219696, 0.0930000692605972))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5667, 
    farPlane=56.5704, width=0.0196088, height=0.0100431, cameraPosition=(
    0.0880715, -0.0676601, 56.5685), cameraTarget=(0.0880715, -0.0676601, 0))
s1.breakCurve(curve1=g[509], point1=(0.0862714126706123, -0.0667027533054352), 
    curve2=g[609], point2=(0.0865188390016556, -0.0662827417254448))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5586, 
    farPlane=56.5785, width=0.106623, height=0.0546096, cameraPosition=(
    -0.251201, -0.0664642, 56.5685), cameraTarget=(-0.251201, -0.0664642, 0))
s1.Line(point1=(-0.2595, 0.0912689069673674), point2=(-0.2595, 
    -0.0646828012218663))
s1.VerticalConstraint(entity=g[619], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5592, 
    farPlane=56.5779, width=0.100629, height=0.05154, cameraPosition=(
    0.0959001, -0.0668702, 56.5685), cameraTarget=(0.0959001, -0.0668702, 0))
s1.Line(point1=(0.0865, 0.0937073636158992), point2=(0.0865, 
    -0.0666999924078861))
s1.VerticalConstraint(entity=g[620], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.508, 
    farPlane=56.6291, width=0.649775, height=0.331981, cameraPosition=(
    -0.059554, 0.0224052, 56.5685), cameraTarget=(-0.059554, 0.0224052, 0))
s1.offset(distance=0.0045, objectList=(g[395], g[396], g[397], g[398], g[399], 
    g[400], g[401], g[402], g[403], g[404], g[405], g[406], g[407], g[510], 
    g[511], g[512], g[513], g[514], g[515], g[516], g[517], g[518], g[519], 
    g[520], g[521], g[522], g[611], g[614], g[616], g[617], g[619], g[620]), 
    side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5274, 
    farPlane=56.6097, width=0.441916, height=0.225783, cameraPosition=(
    -0.288902, 0.0117643, 56.5685), cameraTarget=(-0.288902, 0.0117643, 0))
s1.offset(distance=0.0045, objectList=(g[308], g[309], g[310], g[311], g[312], 
    g[313], g[314], g[315], g[316], g[317], g[318], g[319], g[320], g[321], 
    g[322], g[323], g[324], g[325], g[326], g[327], g[328], g[329], g[330], 
    g[331], g[332], g[333], g[334], g[335], g[336], g[337], g[338], g[339], 
    g[340], g[341], g[342], g[343], g[344], g[345], g[346], g[347], g[348], 
    g[349], g[350], g[351], g[352], g[353], g[354], g[355], g[356], g[357], 
    g[358], g[359], g[360], g[361], g[362], g[363], g[364], g[365], g[366], 
    g[367], g[368], g[369], g[370], g[371], g[372], g[373], g[374], g[375], 
    g[376], g[377], g[378], g[379], g[380], g[381], g[382], g[383], g[384], 
    g[385], g[386], g[387], g[388], g[389], g[390], g[391], g[392], g[393], 
    g[524], g[525], g[526], g[527], g[528], g[529], g[530], g[531], g[532], 
    g[533], g[534], g[535], g[536], g[537], g[538], g[539], g[540], g[541], 
    g[542], g[543], g[544], g[545], g[546], g[547], g[548], g[549], g[550], 
    g[551], g[552], g[553], g[554], g[555], g[556], g[557], g[558], g[559], 
    g[560], g[561], g[562], g[563], g[564], g[565], g[566], g[567], g[568], 
    g[569], g[570], g[571], g[572], g[573], g[574], g[575], g[576], g[577], 
    g[578], g[579], g[580], g[581], g[582], g[583], g[584], g[585], g[586], 
    g[587], g[588], g[589], g[590], g[591], g[592], g[593], g[594], g[595], 
    g[596], g[597], g[598], g[599], g[600], g[601], g[602], g[603], g[604], 
    g[605], g[606], g[607], g[608], g[612], g[613], g[619]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5048, 
    farPlane=56.6323, width=0.684256, height=0.349598, cameraPosition=(
    -0.0221782, -0.0131193, 56.5685), cameraTarget=(-0.0221782, -0.0131193, 0))
s1.offset(distance=0.009, objectList=(g[621], g[622], g[623], g[624], g[625], 
    g[626], g[627], g[628], g[629], g[630], g[631], g[632], g[633], g[634], 
    g[635], g[636], g[637], g[638], g[639], g[640], g[641], g[642], g[643], 
    g[644], g[645], g[646], g[647], g[648], g[649], g[650]), side=RIGHT)
s1.offset(distance=0.0045, objectList=(g[790], g[791], g[792], g[793], g[794], 
    g[795], g[796], g[797], g[798], g[799], g[800], g[801], g[802], g[803], 
    g[804], g[805], g[806], g[807], g[808], g[809], g[810], g[811], g[812], 
    g[813], g[814], g[815], g[816], g[817], g[818], g[819]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5065, 
    farPlane=56.6306, width=0.666178, height=0.340362, cameraPosition=(
    0.272461, -0.00126185, 56.5685), cameraTarget=(0.272461, -0.00126185, 0))
s1.ConstructionLine(point1=(0.336557000875473, 0.0), point2=(0.336557000875473, 
    0.0362996459007263))
s1.VerticalConstraint(entity=g[848], addUndoState=False)
s1.DistanceDimension(entity1=g[4], entity2=g[848], textPoint=(
    0.239467293024063, -0.102614894509315), value=0.346)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.506, 
    farPlane=56.6311, width=0.760118, height=0.388357, cameraPosition=(
    0.273452, -0.0179446, 56.5685), cameraTarget=(0.273452, -0.0179446, 0))
d[3].setValues(value=0.3979, )
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5593, 
    farPlane=56.5778, width=0.0990543, height=0.0506085, cameraPosition=(
    0.400732, 0.023471, 56.5685), cameraTarget=(0.400732, 0.023471, 0))
s1.breakCurve(curve1=g[428], point1=(0.396513104438782, 0.0391652509570122), 
    curve2=g[848], point2=(0.397825479507446, 0.0366691425442696))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5616, 
    farPlane=56.5755, width=0.0742384, height=0.0379296, cameraPosition=(
    0.40336, -0.0328142, 56.5685), cameraTarget=(0.40336, -0.0328142, 0))
s1.breakCurve(curve1=g[489], point1=(0.396450877189636, -0.0310135968029499), 
    curve2=g[848], point2=(0.397715508937836, -0.0291428379714489))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5629, 
    farPlane=56.5742, width=0.0601968, height=0.0307556, cameraPosition=(
    0.405497, 0.0290199, 56.5685), cameraTarget=(0.405497, 0.0290199, 0))
s1.offset(distance=0.0004, objectList=(g[429], g[430], g[431], g[432], g[433], 
    g[434], g[435], g[436], g[437], g[438], g[439], g[440], g[441], g[442], 
    g[443], g[444], g[445], g[446], g[447], g[448], g[449], g[450], g[451], 
    g[452], g[453], g[454], g[455], g[456], g[457], g[458], g[459], g[460], 
    g[461], g[462], g[463], g[464], g[465], g[466], g[467], g[468], g[469], 
    g[470], g[471], g[472], g[473], g[474], g[475], g[476], g[477], g[478], 
    g[479], g[480], g[481], g[482], g[483], g[484], g[485], g[486], g[487], 
    g[488], g[849], g[852]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5677, 
    farPlane=56.5694, width=0.00884173, height=0.00451739, cameraPosition=(
    0.398762, 0.0381982, 56.5685), cameraTarget=(0.398762, 0.0381982, 0))
s1.Line(point1=(0.3979, 0.0386823797862032), point2=(0.397687552222065, 
    0.0383434610030034))
s1.PerpendicularConstraint(entity1=g[849], entity2=g[915], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(width=0.00833104, 
    height=0.00425647, cameraPosition=(0.39822, -0.0319693, 56.5685), 
    cameraTarget=(0.39822, -0.0319693, 0))
s1.Line(point1=(0.397742775820573, -0.0304908063172934), point2=(0.3979, 
    -0.0308586113708148))
s1.PerpendicularConstraint(entity1=g[914], entity2=g[916], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5577, 
    farPlane=56.5794, width=0.1316, height=0.0672367, cameraPosition=(0.402012, 
    0.0160421, 56.5685), cameraTarget=(0.402012, 0.0160421, 0))
s1.ConstructionLine(point1=(0.395079612731934, 0.0), point2=(0.395079612731934, 
    0.0139279831200838))
s1.VerticalConstraint(entity=g[917], addUndoState=False)
s1.DistanceDimension(entity1=g[917], entity2=g[848], textPoint=(
    0.407367825508118, 0.0105288401246071), value=0.0012)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5673, 
    farPlane=56.5698, width=0.0133348, height=0.00681298, cameraPosition=(
    0.398263, 0.0387852, 56.5685), cameraTarget=(0.398263, 0.0387852, 0))
s1.breakCurve(curve1=g[850], point1=(0.396517127752304, 0.0395454280078411), 
    curve2=g[917], point2=(0.396685391664505, 0.0390749871730804))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5652, 
    farPlane=56.5719, width=0.0362451, height=0.0185182, cameraPosition=(
    0.398196, -0.0308025, 56.5685), cameraTarget=(0.398196, -0.0308025, 0))
s1.breakCurve(curve1=g[851], point1=(0.396012097597122, -0.0317501053214073), 
    curve2=g[917], point2=(0.396629512310028, -0.0305855795741081))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5656, 
    farPlane=56.5715, width=0.0320261, height=0.0163627, cameraPosition=(
    0.397153, -0.0309579, 56.5685), cameraTarget=(0.397153, -0.0309579, 0))
s1.Line(point1=(0.3967, -0.0313715706506824), point2=(0.397742775820573, 
    -0.0304908063172934))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5665, 
    farPlane=56.5706, width=0.0216461, height=0.0110594, cameraPosition=(
    0.398617, 0.0373047, 56.5685), cameraTarget=(0.398617, 0.0373047, 0))
s1.Line(point1=(0.397687552222065, 0.0383434610030034), point2=(0.3967, 
    0.0394345875313392))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.5243, 
    farPlane=56.6128, width=0.474754, height=0.24256, cameraPosition=(0.253365, 
    0.0265423, 56.5685), cameraTarget=(0.253365, 0.0265423, 0))
s1.offset(distance=0.0018, objectList=(g[409], g[410], g[411], g[412], g[413], 
    g[414], g[415], g[416], g[417], g[418], g[419], g[420], g[421], g[422], 
    g[423], g[424], g[425], g[426], g[427], g[490], g[491], g[492], g[493], 
    g[494], g[495], g[496], g[497], g[498], g[499], g[500], g[501], g[502], 
    g[503], g[504], g[505], g[506], g[507], g[508], g[615], g[618], g[620], 
    g[853], g[854], g[855], g[856], g[857], g[858], g[859], g[860], g[861], 
    g[862], g[863], g[864], g[865], g[866], g[867], g[868], g[869], g[870], 
    g[871], g[872], g[873], g[874], g[875], g[876], g[877], g[878], g[879], 
    g[880], g[881], g[882], g[883], g[884], g[885], g[886], g[887], g[888], 
    g[889], g[890], g[891], g[892], g[893], g[894], g[895], g[896], g[897], 
    g[898], g[899], g[900], g[901], g[902], g[903], g[904], g[905], g[906], 
    g[907], g[908], g[909], g[910], g[911], g[912], g[913], g[914], g[919], 
    g[920], g[922], g[923]), side=RIGHT)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3795, 
    farPlane=56.7575, width=2.02857, height=1.03643, cameraPosition=(-0.411525, 
    0.0596976, 56.5685), cameraTarget=(-0.411525, 0.0596976, 0))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
e1, d2 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['Part-1']
f1 = p.faces
p.RemoveFaces(faceList = f1[9:10], deleteCells=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=54.0515, 
    farPlane=59.0856, width=27.0937, height=13.8426, viewOffsetX=1.81832, 
    viewOffsetY=0.0214316)
session.viewports['Viewport: 1'].view.fitView()
mdb.saveAs(pathName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil.cae')
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.30723, 
    farPlane=3.64388, width=2.03881, height=1.04166, viewOffsetX=0.0103118, 
    viewOffsetY=0.020757)
p = mdb.models['Model-1'].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(
    0.235625, 0.010199, 0.0))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=56.41, gridSpacing=1.41, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
#: Warning: The limit for coplanar entities has been exceeded; therefore,
#: no entities will be automatically projected onto this sketch.
#: Use the sketch project tools to manually project edges onto this sketch.
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.716107, 
    farPlane=0.806307, width=0.54785, height=0.279906, cameraPosition=(
    -0.283446, 0.0139489, 0.761207), cameraTarget=(-0.283446, 0.0139489, 0))
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['Part-1']
s1 = p.features['Partition face-1'].sketch
mdb.models['Model-1'].ConstrainedSketch(name='__edit__', objectToCopy=s1)
s2 = mdb.models['Model-1'].sketches['__edit__']
g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s2, 
    upToFeature=p.features['Partition face-1'], filter=COPLANAR_EDGES)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4022, 
    farPlane=56.4254, width=0.140641, height=0.0718559, cameraPosition=(
    -0.259027, 0.0763428, 56.4138), cameraTarget=(-0.259027, 0.0763428, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[720], nearPoint1=(-0.26377409696579, 
    0.0825005769729614), curve2=g[719], nearPoint2=(-0.267678320407867, 
    0.0864876508712769))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4092, 
    farPlane=56.4184, width=0.0497284, height=0.0254071, cameraPosition=(
    -0.261197, -0.0581354, 56.4138), cameraTarget=(-0.261197, -0.0581354, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[721], nearPoint1=(-0.265511065721512, 
    -0.0601246953010559), curve2=g[720], nearPoint2=(-0.264067858457565, 
    -0.0580257102847099))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3925, 
    farPlane=56.4351, width=0.228965, height=0.116982, cameraPosition=(
    -0.224908, 0.0472046, 56.4138), cameraTarget=(-0.224908, 0.0472046, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[650], nearPoint1=(-0.250837683677673, 
    0.0866553336381912), curve2=g[649], nearPoint2=(-0.254882484674454, 
    0.0814625471830368))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3863, 
    farPlane=56.4414, width=0.295667, height=0.151061, cameraPosition=(
    -0.199231, -0.0192441, 56.4138), cameraTarget=(-0.199231, -0.0192441, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[649], nearPoint1=(-0.254726707935333, 
    -0.0551002398133278), curve2=g[648], nearPoint2=(-0.250809341669083, 
    -0.0599431358277798))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3935, 
    farPlane=56.4341, width=0.217879, height=0.111318, cameraPosition=(
    0.0329619, -0.0324177, 56.4138), cameraTarget=(0.0329619, -0.0324177, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[635], nearPoint1=(0.0777060836553574, 
    -0.0619973093271255), curve2=g[634], nearPoint2=(0.0822423696517944, 
    -0.0596638880670071))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3956, 
    farPlane=56.432, width=0.19489, height=0.0995727, cameraPosition=(
    0.0439547, 0.0528967, 56.4138), cameraTarget=(0.0439547, 0.0528967, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[634], nearPoint1=(0.0816417187452316, 
    0.0843892171978951), curve2=g[633], nearPoint2=(0.0786907076835632, 
    0.0893003270030022))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3985, 
    farPlane=56.4291, width=0.164633, height=0.0841137, cameraPosition=(
    0.101974, 0.0629361, 56.4138), cameraTarget=(0.101974, 0.0629361, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[1029], nearPoint1=(
    0.0919504538178444, 0.091821014881134), curve2=g[1028], nearPoint2=(
    0.088315024971962, 0.0893318206071854))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3952, 
    farPlane=56.4324, width=0.199839, height=0.102101, cameraPosition=(
    0.102956, -0.0306781, 56.4138), cameraTarget=(0.102956, -0.0306781, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[1028], nearPoint1=(
    0.0883935391902924, -0.0627183467149735), curve2=g[1027], nearPoint2=(
    0.0899065062403679, -0.0647326707839966))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3935, 
    farPlane=56.4341, width=0.217992, height=0.111376, cameraPosition=(
    -0.217384, 0.0401324, 56.4138), cameraTarget=(-0.217384, 0.0401324, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[818], nearPoint1=(-0.241108417510986, 
    0.078241840004921), curve2=g[817], nearPoint2=(-0.246059656143188, 
    0.0752205476164818))
s2.FilletByRadius(radius=0.0045, curve1=g[845], nearPoint1=(-0.238082647323608, 
    0.0739845708012581), curve2=g[844], nearPoint2=(-0.241108417510986, 
    0.0690406337380409))
#* A fillet cannot be created at a vertex shared by more than two entities.
s2.FilletByRadius(radius=0.0045, curve1=g[845], nearPoint1=(-0.237670063972473, 
    0.0737098976969719), curve2=g[844], nearPoint2=(-0.240970879793167, 
    0.0693152993917465))
#* A fillet cannot be created at a vertex shared by more than two entities.
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4067, 
    farPlane=56.4209, width=0.0764472, height=0.0390582, cameraPosition=(
    -0.23164, -0.0474613, 56.4138), cameraTarget=(-0.23164, -0.0474613, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[817], nearPoint1=(-0.246133223176003, 
    -0.0486894100904465), curve2=g[816], nearPoint2=(-0.243142873048782, 
    -0.0515790395438671))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4126, 
    farPlane=56.415, width=0.0125757, height=0.00642516, cameraPosition=(
    0.0724652, -0.0531231, 56.4138), cameraTarget=(0.0724652, -0.0531231, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[803], nearPoint1=(0.0728500112891197, 
    -0.0534439161419868), curve2=g[802], nearPoint2=(0.072969026863575, 
    -0.0530953258275986))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4126, 
    farPlane=56.415, width=0.0126264, height=0.00645106, cameraPosition=(
    0.0729014, 0.0793838, 56.4138), cameraTarget=(0.0729014, 0.0793838, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[802], nearPoint1=(0.0730249136686325, 
    0.0804377272725105), curve2=g[801], nearPoint2=(0.072873555123806, 
    0.0806922689080238))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4114, 
    farPlane=56.4162, width=0.0292804, height=0.0149598, cameraPosition=(
    0.0683572, 0.0778452, 56.4138), cameraTarget=(0.0683572, 0.0778452, 0))
s2.undo()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4071, 
    farPlane=56.4205, width=0.0722761, height=0.0369271, cameraPosition=(
    0.0638215, -0.0447873, 56.4138), cameraTarget=(0.0638215, -0.0447873, 0))
s2.undo()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4114, 
    farPlane=56.4162, width=0.028873, height=0.0147517, cameraPosition=(
    0.0673728, -0.0477458, 56.4138), cameraTarget=(0.0673728, -0.0477458, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[831], nearPoint1=(0.0677097886800766, 
    -0.049046341329813), curve2=g[830], nearPoint2=(0.068493090569973, 
    -0.0482641905546188))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4107, 
    farPlane=56.4169, width=0.0337023, height=0.0172191, cameraPosition=(
    0.0691191, 0.0720822, 56.4138), cameraTarget=(0.0691191, 0.0720822, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[830], nearPoint1=(0.0685981065034866, 
    0.073387935757637), curve2=g[829], nearPoint2=(0.066960833966732, 
    0.0764877945184708))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4124, 
    farPlane=56.4152, width=0.0153511, height=0.00784315, cameraPosition=(
    -0.239738, -0.0468768, 56.4138), cameraTarget=(-0.239738, -0.0468768, 0))
s2.FilletByRadius(radius=0.0045, curve1=g[844], nearPoint1=(-0.241515055298805, 
    -0.0460885763168335), curve2=g[843], nearPoint2=(-0.240285024046898, 
    -0.0471620559692383))
#* A fillet cannot be created at a vertex shared by more than two entities.
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4017, 
    farPlane=56.4259, width=0.130078, height=0.0664589, cameraPosition=(
    -0.221782, 0.0683071, 56.4138), cameraTarget=(-0.221782, 0.0683071, 0))
s2.CircleByCenterPerimeter(center=(-0.231014877557755, 0.0652341246604919), 
    point1=(-0.226501137018204, 0.0669550076127052))
s2.RadialDimension(curve=g[1043], textPoint=(-0.222808077931404, 
    0.0661355406045914), radius=0.0045)
s2.FixedConstraint(entity=g[845])
s2.FixedConstraint(entity=g[844])
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4067, 
    farPlane=56.4209, width=0.0764263, height=0.0390475, cameraPosition=(
    -0.228037, 0.0629398, 56.4138), cameraTarget=(-0.228037, 0.0629398, 0))
s2.TangentConstraint(entity1=g[1043], entity2=g[845])
s2.TangentConstraint(entity1=g[1043], entity2=g[844])
s2.autoTrimCurve(curve1=g[845], point1=(-0.240790918469429, 
    0.0736044347286224))
s2.autoTrimCurve(curve1=g[844], point1=(-0.24156242609024, 0.0725933462381363))
s2.autoTrimCurve(curve1=g[1043], point1=(-0.234811827540398, 
    0.0728822275996208))
s2.autoTrimCurve(curve1=g[1046], point1=(-0.232786655426025, 
    0.068500816822052))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.412, 
    farPlane=56.4156, width=0.0223535, height=0.0114208, cameraPosition=(
    -0.237815, 0.0708471, 56.4138), cameraTarget=(-0.237815, 0.0708471, 0))
s2.dragEntity(entity=v[832], points=((-0.2415, 0.0738505309415066), (-0.2415, 
    0.0738505309415066), (-0.241700917482376, 0.0738678053021431)))
s2.undo()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4087, 
    farPlane=56.4189, width=0.0552096, height=0.0282075, cameraPosition=(
    -0.230497, -0.0453076, 56.4138), cameraTarget=(-0.230497, -0.0453076, 0))
s2.CircleByCenterPerimeter(center=(-0.237829029560089, -0.0436554737389088), 
    point1=(-0.235808730125427, -0.0428555086255074))
s2.RadialDimension(curve=g[1048], textPoint=(-0.231733322143555, 
    -0.0435511283576488), radius=0.0045)
s2.FixedConstraint(entity=g[1045])
s2.FixedConstraint(entity=g[843])
s2.TangentConstraint(entity1=g[1048], entity2=g[1045])
s2.TangentConstraint(entity1=g[1048], entity2=g[843])
s2.autoTrimCurve(curve1=g[1045], point1=(-0.241312280297279, 
    -0.0458466857671738))
s2.autoTrimCurve(curve1=g[843], point1=(-0.240197643637657, 
    -0.0472031533718109))
s2.autoTrimCurve(curve1=g[1048], point1=(-0.23445026576519, 
    -0.0466466546058655))
s2.autoTrimCurve(curve1=g[1051], point1=(-0.233056962490082, 
    -0.0401077941060066))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4093, 
    farPlane=56.4183, width=0.0486377, height=0.0248498, cameraPosition=(
    0.0703805, -0.0502757, 56.4138), cameraTarget=(0.0703805, -0.0502757, 0))
s2.CircleByCenterPerimeter(center=(0.068708099424839, -0.0501991249620914), 
    point1=(0.0708561390638351, -0.0499846376478672))
s2.RadialDimension(curve=g[1053], textPoint=(0.0710709393024445, 
    -0.0477784872055054), radius=0.0045)
s2.FixedConstraint(entity=g[804])
s2.FixedConstraint(entity=g[802])
s2.TangentConstraint(entity1=g[1053], entity2=g[802])
s2.TangentConstraint(entity1=g[1053], entity2=g[804])
s2.autoTrimCurve(curve1=g[804], point1=(0.0711323171854019, 
    -0.0534470677375793))
s2.autoTrimCurve(curve1=g[802], point1=(0.0730041787028313, 
    -0.052190788090229))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.413, 
    farPlane=56.4147, width=0.00915009, height=0.00467494, cameraPosition=(
    0.0726232, -0.0533814, 56.4138), cameraTarget=(0.0726232, -0.0533814, 0))
s2.autoTrimCurve(curve1=g[803], point1=(0.0728627517819405, 
    -0.0534823089838028))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4104, 
    farPlane=56.4172, width=0.0415929, height=0.0212505, cameraPosition=(
    0.0696861, -0.0485671, 56.4138), cameraTarget=(0.0696861, -0.0485671, 0))
s2.autoTrimCurve(curve1=g[1053], point1=(0.0722708851099014, 
    -0.0467460006475449))
s2.autoTrimCurve(curve1=g[1056], point1=(0.066235326230526, 
    -0.0453572496771812))
s2.autoTrimCurve(curve1=g[1057], point1=(0.0652643889188766, 
    -0.0520651750266552))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4129, 
    farPlane=56.4147, width=0.00942079, height=0.00481324, cameraPosition=(
    0.0730105, -0.049372, 56.4138), cameraTarget=(0.0730105, -0.049372, 0))
s2.autoTrimCurve(curve1=g[1058], point1=(0.0729421079158783, 
    -0.0486567914485931))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.41, 
    farPlane=56.4176, width=0.0411079, height=0.0210027, cameraPosition=(
    0.069928, 0.0770676, 56.4138), cameraTarget=(0.069928, 0.0770676, 0))
s2.CircleByCenterPerimeter(center=(0.0697853043675423, 0.0766143724322319), 
    point1=(0.0719379559159279, 0.076588474214077))
s2.RadialDimension(curve=g[1060], textPoint=(0.0755170658230782, 
    0.0751382261514664), radius=0.0045)
s2.FixedConstraint(entity=g[800])
s2.FixedConstraint(entity=g[1055])
s2.TangentConstraint(entity1=g[1060], entity2=g[800])
s2.TangentConstraint(entity1=g[1060], entity2=g[1055])
s2.autoTrimCurve(curve1=g[800], point1=(0.0718342140316963, 
    0.0807320401072502))
s2.autoTrimCurve(curve1=g[1055], point1=(0.0731050595641136, 
    0.0801364034414291))
s2.autoTrimCurve(curve1=g[801], point1=(0.0728197693824768, 0.080680251121521))
s2.autoTrimCurve(curve1=g[1060], point1=(0.0664914920926094, 
    0.0803694799542427))
s2.autoTrimCurve(curve1=g[1064], point1=(0.064053550362587, 0.074749767780304))
s2.autoTrimCurve(curve1=g[1065], point1=(0.0699149817228317, 
    0.0720564499497414))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4136, 
    farPlane=56.4142, width=0.00240281, height=0.00122764, cameraPosition=(
    0.072888, 0.0763523, 56.4138), cameraTarget=(0.072888, 0.0763523, 0))
s2.undo()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4116, 
    farPlane=56.416, width=0.0263855, height=0.0134808, cameraPosition=(
    0.0698236, 0.0758617, 56.4138), cameraTarget=(0.0698236, 0.0758617, 0))
s2.undo()
s2.undo()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4115, 
    farPlane=56.4161, width=0.0277103, height=0.0141577, cameraPosition=(
    0.071476, 0.0746725, 56.4138), cameraTarget=(0.071476, 0.0746725, 0))
s2.undo()
s2.undo()
s2.undo()
s2.undo()
s2.undo()
s2.delete(objectList=(g[1060], ))
s2.CircleByCenterPerimeter(center=(0.0702784582972527, 0.0770554021000862), 
    point1=(0.0658203288912773, 0.0737036466598511))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4105, 
    farPlane=56.4171, width=0.0356372, height=0.0182076, cameraPosition=(
    0.0719352, 0.0755235, 56.4138), cameraTarget=(0.0719352, 0.0755235, 0))
s2.RadialDimension(curve=g[1061], textPoint=(0.0617387406527996, 
    0.0734468474984169), radius=0.0045)
s2.TangentConstraint(entity1=g[800], entity2=g[1061])
s2.TangentConstraint(entity1=g[1061], entity2=g[1055])
s2.autoTrimCurve(curve1=g[800], point1=(0.0716991573572159, 
    0.0806760117411613))
s2.autoTrimCurve(curve1=g[1055], point1=(0.0731156542897224, 
    0.0799351334571838))
s2.autoTrimCurve(curve1=g[801], point1=(0.0727559104561806, 
    0.0806984677910805))
s2.autoTrimCurve(curve1=g[1061], point1=(0.067067451775074, 
    0.0805862098932266))
s2.autoTrimCurve(curve1=g[1065], point1=(0.0640995651483536, 
    0.0755123198032379))
s2.autoTrimCurve(curve1=g[1064], point1=(0.0653361827135086, 
    0.0731325373053551))
s2.autoTrimCurve(curve1=g[1066], point1=(0.0710696056485176, 
    0.0728182196617126))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.3708, 
    farPlane=56.4568, width=0.52272, height=0.267066, cameraPosition=(-1.12061, 
    -0.000473306, 56.4138), cameraTarget=(-1.12061, -0.000473306, 0))
s2.ConstructionLine(point1=(-1.08350467681885, 0.0), point2=(-1.08350467681885, 
    0.0602834522724152))
s2.VerticalConstraint(entity=g[1068], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.1769, 
    farPlane=56.6507, width=2.54283, height=1.29917, cameraPosition=(-0.433445, 
    0.156028, 56.4138), cameraTarget=(-0.433445, 0.156028, 0))
s2.DistanceDimension(entity1=g[1068], entity2=g[4], textPoint=(
    -0.498419046401978, -0.227636009454727), value=1.211)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4059, 
    farPlane=56.4217, width=0.0845958, height=0.0432214, cameraPosition=(
    -1.19996, 0.000806051, 56.4138), cameraTarget=(-1.19996, 0.000806051, 0))
s2.breakCurve(curve1=g[667], point1=(-1.21039819717407, 0.00621538888663054), 
    curve2=g[1068], point2=(-1.21093189716339, 0.00520280469208956))
s2.breakCurve(curve1=g[773], point1=(-1.21018469333649, -0.00273800012655556), 
    curve2=g[1068], point2=(-1.21087849140167, -0.00444340612739325))
s2.Arc3Points(point1=(-1.211, 0.00610230641711419), point2=(-1.211, 
    -0.00283871624162764), point3=(-1.21450793743134, 0.00168540212325752))
s2.TangentConstraint(entity1=g[1073], entity2=g[1069])
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4134, 
    farPlane=56.4142, width=0.00445845, height=0.0022779, cameraPosition=(
    -1.21065, 0.00571124, 56.4138), cameraTarget=(-1.21065, 0.00571124, 0))
s2.undo()
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4115, 
    farPlane=56.4161, width=0.0275517, height=0.0140766, cameraPosition=(
    -1.20722, 0.00153183, 56.4138), cameraTarget=(-1.20722, 0.00153183, 0))
s2.FixedConstraint(entity=g[1069])
s2.FixedConstraint(entity=g[1072])
s2.TangentConstraint(entity1=g[1073], entity2=g[1069])
s2.undo()
s2.FixedConstraint(entity=v[1106])
s2.FixedConstraint(entity=v[1107])
s2.TangentConstraint(entity1=g[1073], entity2=g[1069])
s2.TangentConstraint(entity1=g[1073], entity2=g[1072])
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4054, 
    farPlane=56.4222, width=0.101914, height=0.0520697, cameraPosition=(
    -1.21877, 0.00669356, 56.4138), cameraTarget=(-1.21877, 0.00669356, 0))
s2.delete(objectList=(g[651], g[652], g[653], g[654], g[655], g[656], g[657], 
    g[658], g[659], g[778], g[779], g[780], g[781], g[782], g[783], g[784], 
    g[785], g[786], g[787], g[788], g[789], g[659], g[660], g[661], g[662], 
    g[662], g[663], g[664], g[665], g[666], g[776], g[777], g[778], g[774], 
    g[775], g[776]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.4109, 
    farPlane=56.4167, width=0.0314532, height=0.0160699, cameraPosition=(
    -1.20719, 0.00257106, 56.4138), cameraTarget=(-1.20719, 0.00257106, 0))
s2.delete(objectList=(g[1070], g[1071]))
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.405, 
    farPlane=56.4226, width=0.0942966, height=0.0481777, cameraPosition=(
    -1.2064, -0.00345443, 56.4138), cameraTarget=(-1.2064, -0.00345443, 0))
s2.delete(objectList=(c[2262], ))
s2.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
p.features['Partition face-1'].setValues(sketch=s2)
del mdb.models['Model-1'].sketches['__edit__']
p = mdb.models['Model-1'].parts['Part-1']
p.regenerate()
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.36642, 
    farPlane=3.58469, width=1.17391, height=0.599771, viewOffsetX=0.354397, 
    viewOffsetY=-0.0276136)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
p = mdb.models['Model-1'].parts['Part-1']
f1 = p.faces
p.RemoveFaces(faceList = f1[10:11], deleteCells=False)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.36557, 
    farPlane=3.58555, width=1.33365, height=0.681385, viewOffsetX=0.476269, 
    viewOffsetY=-0.0282402)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.42392, 
    farPlane=3.52719, width=0.554769, height=0.283441, viewOffsetX=0.37475, 
    viewOffsetY=-0.00517181)
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
mdb.models['Model-1'].Material(name='cfrp')
mdb.models['Model-1'].materials['cfrp'].Density(table=((3.104511, ), ))
mdb.models['Model-1'].materials['cfrp'].Elastic(type=ENGINEERING_CONSTANTS, 
    table=((2822400000.0, 192960000.0, 192960000.0, 0.348, 0.348, 0.3, 
    131040000.0, 131040000.0, 74220000.0), ))
mdb.models['Model-1'].Material(name='al')
mdb.models['Model-1'].materials['al'].Density(table=((5.6393, ), ))
mdb.models['Model-1'].materials['al'].Elastic(table=((1886400000.0, 0.33), ))
mdb.models['Model-1'].Material(name='foam')
mdb.models['Model-1'].materials['foam'].Density(table=((0.146, ), ))
mdb.models['Model-1'].materials['foam'].Elastic(type=ENGINEERING_CONSTANTS, 
    table=((1890000.0, 1890000.0, 1890000.0, 0.315, 0.315, 0.3, 593000.0, 
    593000.0, 593000.0), ))
mdb.models['Model-1'].Material(name='honeycomb')
mdb.models['Model-1'].materials['honeycomb'].Density(table=((0.0935, ), ))
mdb.models['Model-1'].materials['honeycomb'].Elastic(
    type=ENGINEERING_CONSTANTS, table=((144000.0, 144000.0, 2880000.0, 0.3, 
    0.01, 0.01, 144000.0, 835000.0, 504000.0), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='al', material='al', 
    thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='foam', material='foam', 
    thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='honeycomb', 
    material='honeycomb', thickness=None)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.46276, 
    farPlane=3.48836, width=0.137418, height=0.0702092, viewOffsetX=0.515827, 
    viewOffsetY=-0.0800292)
mdb.models['Model-1'].Material(name='coat')
mdb.models['Model-1'].materials['coat'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['coat'].Elastic(table=((1.0, 0.3), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='coat', material='coat', 
    thickness=None)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.41415, 
    farPlane=3.53696, width=0.745125, height=0.380697, viewOffsetX=0.478537, 
    viewOffsetY=-0.000963986)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.46147, 
    farPlane=3.48965, width=0.151271, height=0.0772869, viewOffsetX=-0.813023, 
    viewOffsetY=-0.0340039)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#8 ]', ), )
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='coat', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.47267, 
    farPlane=3.47845, width=0.0309991, height=0.0158379, viewOffsetX=0.8576, 
    viewOffsetY=-0.0124834)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#20 ]', ), )
region = p.Set(faces=faces, name='Set-2')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='al', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.47381, 
    farPlane=3.47731, width=0.0187813, height=0.00959568, viewOffsetX=0.829646, 
    viewOffsetY=0.0253594)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#70 ]', ), )
region=p.Set(faces=faces, name='Set-3')
mdb.models['Model-1'].parts['Part-1'].sectionAssignments[1].setValues(
    region=region)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.4026, 
    farPlane=3.54852, width=0.885139, height=0.452233, viewOffsetX=0.579667, 
    viewOffsetY=-0.00705307)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#80 ]', ), )
region = p.Set(faces=faces, name='Set-4')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='foam', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.37596, 
    farPlane=3.57516, width=1.07099, height=0.547185, viewOffsetX=0.435049, 
    viewOffsetY=-0.006032)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#400 ]', ), )
region = p.Set(faces=faces, name='Set-5')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='honeycomb', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.43783, 
    farPlane=3.51329, width=0.405244, height=0.207046, viewOffsetX=0.66554, 
    viewOffsetY=-0.000463475)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#0:3 #fffff800 #ffffffff:2 #ffffff ]', ), 
    )
primaryAxisRegion = p.Set(edges=edges, name='Set-6')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-1', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
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
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=True)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.42922, 
    farPlane=3.5219, width=0.562476, height=0.287379, viewOffsetX=0.192524, 
    viewOffsetY=0.0105295)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#200 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#0:27 #ffe00000 #ffffffff:3 #7 ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-8')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-2', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
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
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=True)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.42638, 
    farPlane=3.52473, width=0.528291, height=0.269913, viewOffsetX=0.365972, 
    viewOffsetY=-0.00433263)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#4 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#0:7 #ff000000 #3ffffff ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-10')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-3', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
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
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#2 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#0:6 #ff000000 #ffffff ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-12')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-4', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
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
    primaryAxisDirection=AXIS_1, flipPrimaryDirection=True)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
layupOrientation = None
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#100 ]', ), )
region1=regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['Part-1']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#0:26 #ffe00000 #1fffff ]', ), )
primaryAxisRegion = p.Set(edges=edges, name='Set-14')
compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-5', description='', elementType=SOLID, 
    symmetric=False, thicknessAssignment=FROM_SECTION)
compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region1, 
    material='cfrp', thicknessType=SPECIFY_THICKNESS, thickness=1.0, 
    orientationType=SPECIFY_ORIENT, orientationValue=-45.0, 
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.29854, 
    farPlane=3.65258, width=1.90618, height=0.969097, viewOffsetX=0.137825, 
    viewOffsetY=0.0741773)
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Section']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.38312, 
    farPlane=3.568, width=0.993892, height=0.505292, viewOffsetX=0.369958, 
    viewOffsetY=0.000568397)
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
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.29635, 
    farPlane=3.65476, width=2.16468, height=1.1033, viewOffsetX=0.144377, 
    viewOffsetY=-0.146571)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Meshability']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.29743, 
    farPlane=3.65369, width=1.91334, height=0.975195, viewOffsetX=0.0763319, 
    viewOffsetY=-0.0864155)
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=0.008, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.27515, 
    farPlane=3.67597, width=2.4199, height=1.23338, viewOffsetX=0.214377, 
    viewOffsetY=0.163099)
p = mdb.models['Model-1'].parts['Part-1']
p.deleteMesh()
p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=0.004, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.30457, 
    farPlane=3.64654, width=1.83637, height=0.935966, viewOffsetX=0.0601975, 
    viewOffsetY=-0.0233026)
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Section']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.31235, 
    farPlane=3.63876, width=1.75258, height=0.893262, viewOffsetX=-0.0260084, 
    viewOffsetY=-0.00976163)
session.viewports['Viewport: 1'].view.fitView()
session.viewports['Viewport: 1'].view.fitView()
session.viewports['Viewport: 1'].view.fitView()
session.viewports['Viewport: 1'].view.fitView()
session.printOptions.setValues(vpDecorations=OFF)
session.printToFile(
    fileName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil.png', 
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.46298, 
    farPlane=3.48813, width=0.152327, height=0.0776384, viewOffsetX=0.831575, 
    viewOffsetY=-0.000528277)
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=OFF)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.47167, 
    farPlane=3.47945, width=0.0472488, height=0.0240211, viewOffsetX=0.83009, 
    viewOffsetY=0.0236)
session.printToFile(
    fileName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil_zoomin1.png', 
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.46537, 
    farPlane=3.48574, width=0.10937, height=0.0556033, viewOffsetX=0.176683, 
    viewOffsetY=0.0636148)
session.printToFile(
    fileName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil_zoomin2.png', 
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.455, 
    farPlane=3.49611, width=0.220713, height=0.11221, viewOffsetX=-0.771778, 
    viewOffsetY=-0.00966093)
session.printToFile(
    fileName='C:/Users/tian50/work/sgio/tests/files/sg2_airfoil_zoomin3.png', 
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.29785, 
    farPlane=3.65327, width=1.91367, height=0.972902, viewOffsetX=0.0352736, 
    viewOffsetY=-0.0494536)
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='sg2_airfoil', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
    numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
    numCpus=1, numGPUs=0)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.31271, 
    farPlane=3.63841, width=1.75374, height=0.891594, viewOffsetX=-0.00339171, 
    viewOffsetY=0.00193293)
mdb.jobs['sg2_airfoil'].writeInput(consistencyChecking=OFF)
#: The job input file has been written to "sg2_airfoil.inp".
session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
    engineeringFeatures=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].view.setValues(nearPlane=3.30193, 
    farPlane=3.64919, width=1.86956, height=0.950479, viewOffsetX=0.0139343, 
    viewOffsetY=-0.0160173)
session.viewports['Viewport: 1'].view.fitView()
p = mdb.models['Model-1'].parts['Part-1']
s = p.features['Partition face-1'].sketch
mdb.models['Model-1'].ConstrainedSketch(name='__edit__', objectToCopy=s)
s1 = mdb.models['Model-1'].sketches['__edit__']
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s1, 
    upToFeature=p.features['Partition face-1'], filter=COPLANAR_EDGES)
session.viewports['Viewport: 1'].view.setValues(nearPlane=56.2327, 
    farPlane=56.5949, width=1.94372, height=1.07145, cameraPosition=(-0.383626, 
    -0.0718236, 56.4138), cameraTarget=(-0.383626, -0.0718236, 0))
session.viewports['Viewport: 1'].view.fitView()
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__edit__']
mdb.save()
#: The model database has been saved to "C:\Users\tian50\work\sgio\tests\files\sg2_airfoil.cae".
