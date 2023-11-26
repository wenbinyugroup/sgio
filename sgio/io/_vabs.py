import logging

from sgio.core.sg import StructureGene
import sgio.utils as sutl
import sgio.model as smdl
import sgio.meshio as smsh

logger = logging.getLogger(__name__)


def readBuffer(f, file_format:str, format_version:str, smdim:int):
    """
    """
    sg = StructureGene()
    sg.version = format_version
    sg.smdim = smdim

    # Read head
    configs = _readHeader(f, file_format, format_version, smdim)
    sg.sgdim = configs['sgdim']
    sg.physics = configs['physics']
    sg.do_dampling = configs.get('do_damping', 0)
    _use_elem_local_orient = configs.get('use_elem_local_orient', 0)
    sg.is_temp_nonuniform = configs.get('is_temp_nonuniform', 0)
    if smdim != 3:
        sg.model = configs['model']
        if smdim == 1:
            init_curvs = configs.get('curvature', [0.0, 0.0, 0.0])
            sg.initial_twist = init_curvs[0]
            sg.initial_curvature = init_curvs[1:]
        elif smdim == 2:
            sg.initial_curvature = configs.get('curvature', [0.0, 0.0])

    nnode = configs['num_nodes']
    nelem = configs['num_elements']

    # Read mesh
    sg.mesh = _readMesh(f, file_format, sg.sgdim, nnode, nelem, _use_elem_local_orient)

    # Read material in-plane angle combinations
    nma_comb = configs['num_mat_angle3_comb']
    sg.mocombos = _readMaterialRotationCombinations(f, nma_comb)

    # Read materials
    nmate = configs['num_materials']
    sg.materials = _readMaterials(f, file_format, nmate)

    return sg


def _readHeader(file, file_format:str, format_version:str, smdim:int):
    """
    """

    logger.debug('reading header...')

    configs = {}

    configs['sgdim'] = 2

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['format'] = int(line[0])
    configs['num_mat_angle3_comb'] = int(line[1])

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['model'] = int(line[0])
    configs['do_damping'] = int(line[1])
    configs['physics'] = 1 if int(line[2]) > 0 else 0

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['is_curve'] = int(line[0])
    configs['is_oblique'] = int(line[1])
    configs['model'] = 3 if line[2] == '1' else configs['model']  # trapeze
    configs['model'] = 2 if line[3] == '1' else configs['model']  # vlasov

    if configs['is_curve'] == 1:
        line = sutl.readNextNonEmptyLine(file)
        line = line.split()
        configs['curvature'] = list(map(float, line[:3]))

    if configs['is_oblique'] == 1:
        line = sutl.readNextNonEmptyLine(file)
        line = line.split()
        configs['oblique'] = list(map(float, line[:2]))

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['num_nodes'] = int(line[0])
    configs['num_elements'] = int(line[1])
    configs['num_materials'] = int(line[2])

    return configs


def _readMesh(file, file_format:str, sgdim:int, nnode:int, nelem:int, read_local_frame):
    """
    """

    logger.debug('reading mesh...')

    mesh = smsh.read(
        file, file_format,
        sgdim=sgdim, nnode=nnode, nelem=nelem, read_local_frame=read_local_frame
    )

    return mesh



def _readMaterialRotationCombinations(file, ncomb):
    """
    """

    logger.debug('reading combinations of material and in-plane rotations...')

    combinations = {}

    counter = 0
    while counter < ncomb:
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()

        line = line.split()
        comb_id = int(line[0])
        mate_id = int(line[1])
        ip_ratation = float(line[2])

        combinations[comb_id] = [mate_id, ip_ratation]

        counter += 1

    return combinations









def _readMaterials(file, file_format:str, nmate:int):
    """
    """

    logger.debug('reading materials...')

    materials = {}

    counter = 0
    while counter < nmate:
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()

        line = line.split()

        # Read material id, isotropy
        mate_id, isotropy = list(map(int, line))
        ntemp = 1
        # material, line = _readMaterial(file, file_format, isotropy)

        material = _readMaterial(file, file_format, isotropy, ntemp)

        materials[mate_id] = material

        counter += 1

    return materials




def _readMaterial(file, file_format:str, isotropy:int, ntemp:int=1):
    """
    """

    # mp = mmsd.MaterialProperty()
    # mp = smdl.MaterialSection()
    mp = smdl.CauchyContinuumModel()
    # mp.isotropy = isotropy
    mp.set('isotropy', isotropy)

    temp_counter = 0
    while temp_counter < ntemp:

        # Read elastic properties
        elastic_props = _readElasticProperty(file, isotropy)
        mp.setElastic(elastic_props, isotropy)

        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()
        density = float(line)

        # mp.density = density
        mp.set('density', density)

        # Read thermal properties

        temp_counter += 1

    return mp









def _readElasticProperty(file, isotropy:int):
    """
    """

    constants = []

    if isotropy == 0:
        nrow = 1
    elif isotropy == 1:
        nrow = 3
    elif isotropy == 2:
        nrow = 6

    for i in range(nrow):
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()
        constants.extend(list(map(float, line.split())))

    return constants









# ====================================================================
# Read output
# ====================================================================
def readOutputBuffer(file, analysis=0, sg:StructureGene=None, **kwargs):
    if analysis == 0 or analysis == 'h' or analysis == '':
        return _readOutputH(file, **kwargs)

    elif analysis == 1 or analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
        pass

    elif analysis == 'f' or analysis == 3:
        # return readSCOutFailure(file, analysis)
        pass
    elif analysis == 'fe' or analysis == 4:
        # return readSCOutFailure(file, analysis)
        pass
    elif analysis == 'fi' or analysis == 5:
        return _readOutputFailureIndex(file)

    return




def _readOutputH(file, **kwargs):
    """Read VABS homogenization output.
    """

    if kwargs['submodel'] == 1:
        return _readEulerBernoulliBeamModel(file)
    elif kwargs['submodel'] == 2:
        return _readTimoshenkoBeamModel(file)




def _readEulerBernoulliBeamModel(file):
    """
    """

    model = smdl.EulerBernoulliBeamModel()

    block = ''
    line = file.readline()

    while True:
        if not line:  # EOF
            break

        line = line.strip()

        if len(line) == 0:
            line = file.readline()
            continue
        elif line.startswith('--') or line.startswith('=='):
            line = file.readline()
            continue

        # line = line.lower()
        # line = line.replace('-', ' ')

        elif 'Geometric Center' in line:
            for _ in range(3): line = file.readline()
            model.xg2, model.xg3 = list(map(float, line.split()))
        elif 'Area =' in line:
            model.area = float(line.split()[-1])


        # Inertial properties
        # -------------------

        elif line == 'The 6X6 Mass Matrix':
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass = _matrix
        elif '6X6 Mass Matrix at the Mass Center' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass_mc = _matrix
        elif 'Mass Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xm2, model.xm3 = list(map(float, line.split()))
        elif 'Mass per unit span' in line:
            model.mu = float(line.split()[-1])
        elif 'inertia i11' in line:
            model.i11 = float(line.split()[-1])
        elif 'inertia i22' in line:
            model.i22 = float(line.split()[-1])
        elif 'inertia i33' in line:
            model.i33 = float(line.split()[-1])
        elif 'principal inertial axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pia = float(line[tmp_id - 1])
        elif 'mass-weighted radius of gyration' in line:
            model.rg = float(line.split()[-1])


        # Structural properties
        # ---------------------

        elif 'Classical Stiffness Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.stff = _matrix
        elif 'Classical Compliance Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.cmpl = _matrix

        elif 'Tension Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xt2, model.xt3 = list(map(float, line.split()))
        elif 'extension stiffness EA' in line:
            model.ea = float(line.split()[-1])
        elif 'torsional stiffness GJ' in line:
            model.gj = float(line.split()[-1])
        elif 'Principal bending stiffness EI22' in line:
            model.ei22 = float(line.split()[-1])
        elif 'Principal bending stiffness EI33' in line:
            model.ei33 = float(line.split()[-1])
        elif 'principal bending axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pba = float(line[tmp_id - 1])

        line = file.readline()

    return model




def _readTimoshenkoBeamModel(file):
    """
    """

    model = smdl.TimoshenkoBeamModel()

    block = ''
    line = file.readline()

    while True:
        if not line:  # EOF
            break

        line = line.strip()

        if len(line) == 0:
            line = file.readline()
            continue
        elif line.startswith('--') or line.startswith('=='):
            line = file.readline()
            continue

        # line = line.lower()
        # line = line.replace('-', ' ')

        elif 'Geometric Center' in line:
            for _ in range(3): line = file.readline()
            model.xg2, model.xg3 = list(map(float, line.split()))
        elif 'Area =' in line:
            model.area = float(line.split()[-1])


        # Inertial properties
        # -------------------

        elif line == 'The 6X6 Mass Matrix':
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass = _matrix
        elif '6X6 Mass Matrix at the Mass Center' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass_mc = _matrix
        elif 'Mass Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xm2, model.xm3 = list(map(float, line.split()))
        elif 'Mass per unit span' in line:
            model.mu = float(line.split()[-1])
        elif 'inertia i11' in line:
            model.i11 = float(line.split()[-1])
        elif 'inertia i22' in line:
            model.i22 = float(line.split()[-1])
        elif 'inertia i33' in line:
            model.i33 = float(line.split()[-1])
        elif 'principal inertial axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pia = float(line[tmp_id - 1])
        elif 'mass-weighted radius of gyration' in line:
            model.rg = float(line.split()[-1])


        # Structural properties
        # ---------------------

        elif 'Classical Stiffness Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.stff_c = _matrix
        elif 'Classical Compliance Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.cmpl_c = _matrix

        elif 'Tension Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xt2, model.xt3 = list(map(float, line.split()))
        elif 'extension stiffness EA' in line:
            model.ea = float(line.split()[-1])
        elif 'torsional stiffness GJ' in line:
            model.gj = float(line.split()[-1])
        elif 'Principal bending stiffness EI22' in line:
            model.ei22 = float(line.split()[-1])
        elif 'Principal bending stiffness EI33' in line:
            model.ei33 = float(line.split()[-1])
        elif 'principal bending axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pba = float(line[tmp_id - 1])

        elif 'Timoshenko Stiffness Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6, number_type=float
                )
            model.stff = _matrix
        elif 'Timoshenko Compliance Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6, number_type=float
                )
            model.cmpl = _matrix

        elif 'Shear Center' in line:
            for _ in range(3): line = file.readline()
            model.xs2, model.xs3 = list(map(float, line.split()))
        elif 'Principal shear stiffness GA22' in line:
            model.ga22 = float(line.split()[-1])
        elif 'Principal shear stiffness GA33' in line:
            model.ga33 = float(line.split()[-1])
        elif 'principal shear axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_psa = float(line[tmp_id - 1])

        line = file.readline()

    return model

        # elif 'Vlasov Stiffness Matrix' in line:
        #     keywordsIndex['vsm'] = ln
        # elif 'Vlasov Flexibility Matrix' in line:
        #     keywordsIndex['vfm'] = ln
        
        # elif 'Trapeze Effects' in line:
        #     keywordsIndex['te'] = ln
        # elif 'Ag1--Ag1--Ag1--Ag1' in line:
        #     keywordsIndex['te_ag'] = ln
        # elif 'Bk1--Bk1--Bk1--Bk1' in line:
        #     keywordsIndex['te_bk'] = ln
        # elif 'Ck2--Ck2--Ck2--Ck2' in line:
        #     keywordsIndex['te_ck'] = ln
        # elif 'Dk3--Dk3--Dk3--Dk3' in line:
        #     keywordsIndex['te_dk'] = ln

    # #check whether the analysis is Vlasov or timoshenko
    # #Read stiffness matrix and compliance matrix
    # if 'vsm' in keywordsIndex.keys():
    #     pass
    #     # try:
    #     #     ln = keywordsIndex['vsm']
    #     #     sm.stiffness_refined = utl.textToMatrix(linesRead[ln + 3:ln + 8])
    #     #     #old dic to save valsov stiffness matrix
    #     #     # sm.eff_props[1]['stiffness']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 8])
    #     # except KeyError:
    #     #     if scrnout:
    #     #         print('No Vlasov stiffness matrix found.')
    #     #     else:
    #     #         pass
    #     # try:
    #     #     ln = keywordsIndex['vfm']
    #     #     sm.compliance_refined = utl.textToMatrix(linesRead[ln + 3:ln + 8])
    #     #     #old dic to save valsov compliance matrix
    #     #     # sm.eff_props[1]['compliance']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 8])            
    #     # except KeyError:
    #     #     if scrnout:
    #     #         print('No Vlasov flexibility matrix found.')
    #     #     else:
    #     #         pass
    #     #check whether trapeze effect analysis is on and read the correponding matrix
    #     # if 'te' in keywordsIndex.keys():
    #     #     try:
    #     #         ln = keywordsIndex['te_ag']
    #     #         sm.trapeze_effect['ag'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Ag1--Ag1--Ag1--Ag1 matrix found.')
    #     #         else:
    #     #             pass
    #     #     try:
    #     #         ln = keywordsIndex['te_bk']
    #     #         sm.trapeze_effect['bk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Bk1--Bk1--Bk1--Bk1 matrix found.')
    #     #         else:
    #     #             pass
    #     #     try:
    #     #         ln = keywordsIndex['te_ck']
    #     #         sm.trapeze_effect['ck'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Ck2--Ck2--Ck2--Ck2 matrix found.')
    #     #         else:
    #     #             pass    
    #     #     try:
    #     #         ln = keywordsIndex['te_dk']
    #     #         sm.trapeze_effect['dk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Dk3--Dk3--Dk3--Dk3 matrix found.')
    #     #         else:
    #     #             pass                   
    # else:
    #     try:
    #         ln = keywordsIndex['csm']
    #         bp.stff = sutl.textToMatrix(linesRead[ln + 2:ln + 6])
    #         #old dic method to save classical stiffness
    #         # sm.eff_props[1]['stiffness']['classical'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     except KeyError:
    #         logger.info('No classical stiffness matrix found.')
    #         # if scrnout:
    #         # else:
    #         #     pass

    #     try:
    #         ln = keywordsIndex['cfm']
    #         bp.cmpl = sutl.textToMatrix(linesRead[ln + 2:ln + 6])
    #         #old dic method to save classical compliance
    #         # sm.eff_props[1]['compliance']['classical'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     except KeyError:
    #         logger.info('No classical compliance matrix found.')
    #         # if scrnout:
    #         # else:
    #         #     pass

    #     try:
    #         ln = keywordsIndex['tsm']
    #         bp.stff_t = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
    #         #old dic method to save refined stiffness matrix
    #         # sm.eff_props[1]['stiffness']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
    #     except KeyError:
    #         logger.info('No Timoshenko stiffness matrix found.')
    #         # if scrnout:
    #         # else:
    #         #     pass
    #     try:
    #         ln = keywordsIndex['tfm']
    #         bp.cmpl_t = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
    #         #old dic method to save refined compliance matrix
    #         # sm.eff_props[1]['compliance']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
    #     except KeyError:
    #         logger.info('No Timoshenko compliance matrix found.')
    #         # if scrnout:
    #         # else:
    #         #     pass

    #     if 'tc' in keywordsIndex.keys():
    #         ln = keywordsIndex['tc']
    #         bp.xt2, bp.xt3 = list(map(float, linesRead[ln + 2].split()))
    #     if 'sc' in keywordsIndex.keys():
    #         ln = keywordsIndex['sc']
    #         bp.xs2, bp.xs3 = list(map(float, linesRead[ln + 2].split()))
    #     if 'mc' in keywordsIndex.keys():
    #         ln = keywordsIndex['mc']
    #         bp.xm2, bp.xm3 = list(map(float, linesRead[ln + 2].split()))
    #     if 'gc' in keywordsIndex.keys():
    #         ln = keywordsIndex['gc']
    #         bp.xg2, bp.xg3 = list(map(float, linesRead[ln + 2].split()))

    #     #check whether trapeze effect analysis is on and read the correponding matrix
    #     # if 'te' in keywordsIndex.keys():
    #     #     try:
    #     #         ln = keywordsIndex['te_ag']
    #     #         sm.trapeze_effect['ag'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Ag1--Ag1--Ag1--Ag1 matrix found.')
    #     #         else:
    #     #             pass
    #     #     try:
    #     #         ln = keywordsIndex['te_bk']
    #     #         sm.trapeze_effect['bk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Bk1--Bk1--Bk1--Bk1 matrix found.')
    #     #         else:
    #     #             pass
    #     #     try:
    #     #         ln = keywordsIndex['te_ck']
    #     #         sm.trapeze_effect['ck'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Ck2--Ck2--Ck2--Ck2 matrix found.')
    #     #         else:
    #     #             pass    
    #     #     try:
    #     #         ln = keywordsIndex['te_dk']
    #     #         sm.trapeze_effect['dk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
    #     #     except KeyError:
    #     #         if scrnout:
    #     #             print('No Dk3--Dk3--Dk3--Dk3 matrix found.')
    #     #         else:
    #     #             pass              

    # ms.constitutive = bp

    # return ms



def _readOutputFailureIndex(file):
    """
    """
    # if not logger:
    #     logger = mul.initLogger(__name__)

    # logger.info('reading sg failure indices and strengh ratios: {}...'.format(fn))

    lines = []
    load_case = 0
    sr_min = None
    # with open(fn, 'r') as fobj:
    for i, line in enumerate(file):
        line = line.strip()
        if (line == ''):
            continue
        if line.startswith('Failure index'):
            continue

        if (line.startswith('The sectional strength ratio is')):
            line = line.split()
            tmp_id = line.index('existing')
            sr_min = float(line[tmp_id - 1])
            eid_sr_min = int(line[-1])
            # lines.pop()
            continue

        line = line.split()
        if len(line) == 3:
            lines.append(line)

    result = []
    # fis = []
    # srs = []
    for line in lines:
        # line = line.strip().split()
        result.append([int(line[0]), float(line[1]), float(line[2])])
        # fis.append(float(line[1]))
        # srs.append(float(line[2]))

    return result, sr_min, eid_sr_min




def _readOutputStrengthRatio(fn_in):
    lines = []
    sr_min = None
    with open(fn_in, 'r') as fin:
        for i, line in enumerate(fin.readlines()):
            line = line.strip()
            if (line == ''):
                continue
            if line.startswith('Failure index'):
                continue
            # lines.append(line)
            # initial failure indices and strength ratios
            if (line.startswith('The sectional strength ratio is')):
                line = line.split()
                tmp_id = line.index('existing')
                sr_min = float(line[tmp_id - 1])
                # lines.pop()
                continue
            line = line.split()
            if len(line) == 3:
                lines.append(line)

    # print(lines)
    # initial failure indices and strength ratios
    fis = []
    srs = []
    for line in lines:
        # line = line.strip().split()
        # results.append([int(line[0]), float(line[1]), float(line[2])])
        fis.append(float(line[1]))
        srs.append(float(line[2]))
    return fis, srs, sr_min









# Writers


def writeBuffer(
    sg:StructureGene, file, file_format:str, analysis='h', sg_fmt:int=1,
    sfi:str='8d', sff:str='20.12e', version=None, mesh_only=False
    ):
    """Write analysis input

    Parameters
    ----------
    fn : str
        Name of the input file
    file_format : {'vabs' (or 'v'), 'swfitcomp' (or 'sc', 's')}
        file_format of the analysis
    analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}, optional
        Analysis type, by default 'h'
    sg_fmt : {0, 1}, optional
        Format for the VABS input, by default 1

    Returns
    -------
    str
        Name of the input file
    """


    # string format
    # sfi = '8d'
    # sff = '16.6e'

    _file_format = file_format.lower()

    if analysis.lower().startswith('h'):
        writeInputBuffer(sg, file, _file_format, sfi, sff, sg_fmt, version, mesh_only)

    elif (analysis.lower().startswith('d')) or (analysis.lower().startswith('l')) or (analysis.lower().startswith('f')):
        writeInputBufferGlobal(sg, file, _file_format, sfi, sff, analysis, version)

    return









def writeInputBuffer(sg, file, file_format, sfi, sff, sg_fmt, version=None, mesh_only=False):
    """
    """

    logger.debug(f'writing sg input...')

    ssff = '{:' + sff + '}'
    # if not version is None:
    #     sg.version = sutl.Version(version)
    sg.version = version

    logger.debug('format version: {}'.format(sg.version))

    # with open(fn, 'w') as file:
    # if not mesh_only:
    _writeHeader(sg, file, file_format, sfi, sff, sg_fmt, version)

    _writeMesh(sg, file, file_format=file_format, sgdim=sg.sgdim, int_fmt=sfi, float_fmt=sff)

    # if not mesh_only:
    _writeMOCombos(sg, file, file_format, sfi, sff)

    # if not mesh_only:
    _writeMaterials(sg, file, file_format, sfi, sff)

    if file_format.startswith('s'):
        file.write((ssff + '\n').format(sg.omega))

    return









def _writeMesh(sg, file, file_format, sgdim, int_fmt, float_fmt):
    """
    """
    logger.debug('writing mesh...')

    sg.mesh.write(file, file_format, sgdim=sgdim, int_fmt=int_fmt, float_fmt=float_fmt)

    return









def _writeMOCombos(sg, file, file_format, sfi, sff):
    ssfi = '{:' + sfi + '}'
    ssff = '{:' + sff + '}'
    count = 0
    for cid, combo in sg.mocombos.items():
        count += 1
        file.write((ssfi + ssfi + ssff).format(cid, combo[0], combo[1]))
        if count == 1:
            file.write('  # combination id, material id, in-plane rotation angle')
        file.write('\n')
    file.write('\n')
    return









def _writeMaterials(sg, file, file_format, sfi, sff):
    """
    """

    logger.debug('writing materials...')

    counter = 0
    for mid, m in sg.materials.items():

        # print('writing material {}'.format(mid))

        # if m.stff:
        #     anisotropy = 2
        # else:
        anisotropy = m.get('isotropy')

        # print(m.stff)
        # print(anisotropy)

        sutl.writeFormatIntegers(file, (mid, anisotropy), sfi, newline=False)
        if counter == 0:
            file.write('  # materials')
        file.write('\n')

        # Write elastic properties
        if anisotropy == 0:
            # mpc = m.constants
            sutl.writeFormatFloats(file, [m.e1, m.nu12], sff)

        elif anisotropy == 1:
            # mpc = m.constants
            sutl.writeFormatFloats(file, [m.e1, m.e2, m.e3], sff)
            sutl.writeFormatFloats(file, [m.g12, m.g13, m.g23], sff)
            sutl.writeFormatFloats(file, [m.nu12, m.nu13, m.nu23], sff)


        elif anisotropy == 2:
            for i in range(6):
                sutl.writeFormatFloats(file, m.stff[i][i:], sff)
                # for j in range(i, 6):
                #     file.write(sff.format(m.stff[i][j]))
                # file.write('\n')

        # print('sg.physics =', sg.physics)
        # print('m.cte =', m.cte)
        # print('m.specific_heat =', m.specific_heat)
        if sg.physics in [1, 4, 6]:
            sutl.writeFormatFloats(file, m.cte+[m.specific_heat,], sff)

        if file_format.lower().startswith('v'):
            sutl.writeFormatFloats(file, (m.density,), sff)

        file.write('\n')
        
        counter += 1

    file.write('\n')
    return









def _writeHeader(sg, file, file_format, sfi, sff, sg_fmt, version=None):
    ssfi = '{:' + sfi + '}'

    # format_flag  nlayer
    sutl.writeFormatIntegers(file, [sg_fmt, len(sg.mocombos)], newline=False)
    file.write('  # format_flag, nlayer\n\n')

    # timoshenko_flag  damping_flag  thermal_flag
    model = 0
    trapeze = 0
    vlasov = 0
    if sg.model == 1:
        model = 1
    elif sg.model == 2:
        model = 1
        vlasov = 1
    elif sg.model == 3:
        trapeze = 1
    physics = 0
    if sg.physics == 1:
        physics = 3
    sutl.writeFormatIntegers(
        file, [model, sg.do_damping, physics], sfi, newline=False)
    file.write('  # model_flag, damping_flag, thermal_flag\n\n')

    # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
    line = [0, 0, trapeze, vlasov]
    if (sg.initial_twist != 0.0) or (sg.initial_curvature[0] != 0.0) or (sg.initial_curvature[1] != 0.0):
        line[0] = 1
    if (sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0):
        line[1] = 1
    sutl.writeFormatIntegers(file, line, sfi, newline=False)
    file.write('  # curve_flag, oblique_flag, trapeze_flag, vlasov_flag\n\n')

    # k1  k2  k3
    if line[0] == 1:
        sutl.writeFormatFloats(
            file,
            [sg.initial_twist, sg.initial_curvature[0], sg.initial_curvature[1]],
            sff, newline=False
        )
        file.write('  # k11, k12, k13 (initial curvatures)\n\n')
    
    # oblique1  oblique2
    if line[1] == 1:
        sutl.writeFormatFloats(file, sg.oblique, sff, newline=False)
        file.write('  # cos11, cos21 (obliqueness)\n\n')
    
    # nnode  nelem  nmate
    sutl.writeFormatIntegers(
        file, [sg.nnodes, sg.nelems, sg.nmates], sfi, newline=False)
    file.write('  # nnode, nelem, nmate\n\n')

    return









def _writeInputMaterialStrength(sg, file, file_format, sfi, sff):
    for i, m in sg.materials.items():
        # print(m.strength)
        # print(m.failure_criterion)
        # print(m.char_len)

        # file.write('{} {}'.format(m.failure_criterion, len(m.strength)))

        strength = []
        if m.type == 0:
            pass
        else:
            if m.failure_criterion == 1:
                pass
            elif m.failure_criterion == 2:
                pass
            elif m.failure_criterion == 3:
                pass
            elif m.failure_criterion == 4:
                # Tsai-Wu
                strength = [
                    m.strength_constants['xt'], m.strength_constants['yt'], m.strength_constants['zt'],
                    m.strength_constants['xc'], m.strength_constants['yc'], m.strength_constants['zc'],
                    m.strength_constants['r'], m.strength_constants['t'], m.strength_constants['s'],
                ]
            elif m.failure_criterion == 5:
                pass

        sutl.writeFormatIntegers(
            file,
            # (m.strength['criterion'], len(m.strength['constants'])),
            [m.failure_criterion, len(strength)],
            sfi
        )
        # file.write((sff+'\n').format(m.strength['chara_len']))
        sutl.writeFormatFloats(file, [m.char_len,], sff)
        # sutl.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
        sutl.writeFormatFloats(file, strength, sff)
    return









def _writeInputDisplacements(sg, file, file_format, sff):
    sutl.writeFormatFloats(file, sg.global_displacements, sff[2:-1])
    sutl.writeFormatFloatsMatrix(file, sg.global_rotations, sff[2:-1])









def _writeInputLoads(sg, file, file_format, sfi, sff):
    if file_format.startswith('v'):
        if sg.model == 0:
            sutl.writeFormatFloats(file, sg.global_loads)
        else:
            sutl.writeFormatFloats(file, [sg.global_loads[i] for i in [0, 3, 4, 5]])
            sutl.writeFormatFloats(file, [sg.global_loads[i] for i in [1, 2]])
            file.write('\n')
            sutl.writeFormatFloats(file, sg.global_loads_dist[0])
            sutl.writeFormatFloats(file, sg.global_loads_dist[1])
            sutl.writeFormatFloats(file, sg.global_loads_dist[2])
            sutl.writeFormatFloats(file, sg.global_loads_dist[3])
    elif file_format.startswith('s'):
        # file.write((sfi+'\n').format(sg.global_loads_type))
        for load_case in sg.global_loads:
            sutl.writeFormatFloats(file, load_case, sff)
    file.write('\n')
    return









def writeInputBufferGlobal(sg, file, file_format, sfi, sff, analysis, version=None):
    # with open(fn, 'w') as file:
    if analysis.startswith('d') or analysis.lower().startswith('l'):
        _writeInputDisplacements(sg, file, file_format, sff)
    elif analysis.startswith('f'):
        _writeInputMaterialStrength(sg, file, file_format, sfi, sff)

    if file_format.startswith('s'):
        # file.write((sfi+'\n').format(sg.global_loads_type))
        sutl.writeFormatIntegers(file, [sg.global_loads_type, ], sfi)

    if analysis != 'f':
        _writeInputLoads(sg, file, file_format, sfi, sff)

