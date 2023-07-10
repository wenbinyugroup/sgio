import logging

from sgio.core.sg import StructureGene
import sgio.utils.io as sui
import sgio.utils.version as suv
import sgio.model as sgmodel
import sgio.meshio as smsh

logger = logging.getLogger(__name__)


def readBuffer(f, file_format:str, format_version:str, smdim:int):
    r"""
    """
    sg = StructureGene()
    sg.version = format_version
    sg.smdim = smdim

    # Read head
    configs = _readHeader(f, file_format, format_version, smdim)
    sg.sgdim = configs['sgdim']
    sg.physics = configs['physics']
    sg.do_dampling = configs.get('do_damping', 0)
    sg.use_elem_local_orient = configs.get('use_elem_local_orient', 0)
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
    sg.mesh = _readMesh(f, file_format, sg.sgdim, nnode, nelem, sg.use_elem_local_orient)

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

    line = sui.readNextNonEmptyLine(file)
    line = line.split()
    configs['format'] = int(line[0])
    configs['num_mat_angle3_comb'] = int(line[1])

    line = sui.readNextNonEmptyLine(file)
    line = line.split()
    configs['model'] = int(line[0])
    configs['do_damping'] = int(line[1])
    configs['physics'] = 1 if int(line[2]) > 0 else 0

    line = sui.readNextNonEmptyLine(file)
    line = line.split()
    configs['is_curve'] = int(line[0])
    configs['is_oblique'] = int(line[1])
    configs['model'] = 3 if line[2] == '1' else configs['model']  # trapeze
    configs['model'] = 2 if line[3] == '1' else configs['model']  # vlasov

    if configs['is_curve'] == 1:
        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['curvature'] = list(map(float, line[:3]))

    if configs['is_oblique'] == 1:
        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['oblique'] = list(map(float, line[:2]))

    line = sui.readNextNonEmptyLine(file)
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
    mp = sgmodel.MaterialSection()
    mp.isotropy = isotropy

    temp_counter = 0
    while temp_counter < ntemp:

        # Read elastic properties
        elastic_props = _readElasticProperty(file, isotropy)
        mp.setElasticProperty(elastic_props, isotropy)

        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()
        density = float(line)

        mp.density = density

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
def readOutputBuffer(file, analysis=0, sg:StructureGene=None):
    if analysis == 0 or analysis == 'h' or analysis == '':
        return _readOutputH(file)

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




def _readOutputH(file):
    """Read VABS homogenization results

    Parameters
    ----------
    fn : str
        VABS output file name (e.g. example.sg.k).
    scrnout : bool, default True
        Switch of printing cmd output.

    Returns
    -------
    msgpi.sg.MaterialSection
        Material/sectional properties.
    """
    # sm = mms.MaterialSection(smdim = 1)
    # bp = mmbm.BeamProperty()
    ms = sgmodel.MaterialSection(smdim=1)
    bp = sgmodel.BeamModel()

    linesRead = []
    keywordsIndex = {}


    # with open(fn, 'r') as fin:
    ln = -1
    lines = file.readlines()
    for i, line in enumerate(lines):

        line = line.strip()

        if len(line) > 0:
            linesRead.append(line)
            ln += 1
        else:
            continue

        if '=====' in line:
            continue

        line = line.lower()
        # line = line.replace('-', ' ')

        if 'geometric center' in line:
            keywordsIndex['gc'] = ln
        elif 'area =' in line:
            bp.area = float(line.split()[-1])


        # Inertial properties
        # -------------------

        elif '6x6 mass matrix at the mass center' in line:
            keywordsIndex['mass_mc'] = ln
        elif '6x6 mass matrix' in line:
            keywordsIndex['mass'] = ln
        elif 'mass center of the cross section' in line or 'mass center of the cross-section' in line:
            keywordsIndex['mc'] = ln
        elif 'mass per unit span' in line:
            bp.mu = float(line.split()[-1])
        elif 'inertia i11' in line:
            bp.i11 = float(line.split()[-1])
        elif 'inertia i22' in line:
            bp.i22 = float(line.split()[-1])
        elif 'inertia i33' in line:
            bp.i33 = float(line.split()[-1])
        elif 'principal inertial axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = lines[i+1].split()
                tmp_id = line.index('degrees')
            bp.phi_pia = float(line[tmp_id - 1])
        elif 'mass-weighted radius of gyration' in line:
            bp.rg = float(line.split()[-1])


        # Structural properties
        # ---------------------

        elif 'classical stiffness matrix' in line:
            keywordsIndex['csm'] = ln
        elif 'classical compliance matrix' in line:
            keywordsIndex['cfm'] = ln

        elif 'tension center' in line:
            keywordsIndex['tc'] = ln
        elif 'extension stiffness ea' in line:
            bp.ea = float(line.split()[-1])
        elif 'torsional stiffness gj' in line:
            bp.gj = float(line.split()[-1])
        elif 'principal bending stiffness ei22' in line:
            bp.ei22 = float(line.split()[-1])
        elif 'principal bending stiffness ei33' in line:
            bp.ei33 = float(line.split()[-1])
        elif 'principal bending axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = lines[i+1].split()
                tmp_id = line.index('degrees')
            bp.phi_pba = float(line[tmp_id - 1])

        elif 'timoshenko stiffness matrix' in line:
            keywordsIndex['tsm'] = ln
        elif 'timoshenko compliance matrix' in line:
            keywordsIndex['tfm'] = ln

        elif 'shear center' in line:
            keywordsIndex['sc'] = ln
        elif 'principal shear stiffness ga22' in line:
            bp.ga22 = float(line.split()[-1])
        elif 'principal shear stiffness ga33' in line:
            bp.ga33 = float(line.split()[-1])
        elif 'principal shear axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = lines[i+1].split()
                tmp_id = line.index('degrees')
            bp.phi_psa = float(line[tmp_id - 1])

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


    ln = keywordsIndex['mass']
    bp.mass = sui.textToMatrix(linesRead[ln + 2:ln + 8])

    if 'mass_mc' in keywordsIndex.keys():
        ln = keywordsIndex['mass_mc']
        bp.mass_cs = sui.textToMatrix(linesRead[ln + 2:ln + 8])

    #check whether the analysis is Vlasov or timoshenko
    #Read stiffness matrix and compliance matrix
    if 'vsm' in keywordsIndex.keys():
        pass
        # try:
        #     ln = keywordsIndex['vsm']
        #     sm.stiffness_refined = utl.textToMatrix(linesRead[ln + 3:ln + 8])
        #     #old dic to save valsov stiffness matrix
        #     # sm.eff_props[1]['stiffness']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 8])
        # except KeyError:
        #     if scrnout:
        #         print('No Vlasov stiffness matrix found.')
        #     else:
        #         pass
        # try:
        #     ln = keywordsIndex['vfm']
        #     sm.compliance_refined = utl.textToMatrix(linesRead[ln + 3:ln + 8])
        #     #old dic to save valsov compliance matrix
        #     # sm.eff_props[1]['compliance']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 8])            
        # except KeyError:
        #     if scrnout:
        #         print('No Vlasov flexibility matrix found.')
        #     else:
        #         pass
        #check whether trapeze effect analysis is on and read the correponding matrix
        # if 'te' in keywordsIndex.keys():
        #     try:
        #         ln = keywordsIndex['te_ag']
        #         sm.trapeze_effect['ag'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ag1--Ag1--Ag1--Ag1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_bk']
        #         sm.trapeze_effect['bk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Bk1--Bk1--Bk1--Bk1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_ck']
        #         sm.trapeze_effect['ck'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ck2--Ck2--Ck2--Ck2 matrix found.')
        #         else:
        #             pass    
        #     try:
        #         ln = keywordsIndex['te_dk']
        #         sm.trapeze_effect['dk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Dk3--Dk3--Dk3--Dk3 matrix found.')
        #         else:
        #             pass                   
    else:
        try:
            ln = keywordsIndex['csm']
            bp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 6])
            #old dic method to save classical stiffness
            # sm.eff_props[1]['stiffness']['classical'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        except KeyError:
            logger.info('No classical stiffness matrix found.')
            # if scrnout:
            # else:
            #     pass

        try:
            ln = keywordsIndex['cfm']
            bp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 6])
            #old dic method to save classical compliance
            # sm.eff_props[1]['compliance']['classical'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        except KeyError:
            logger.info('No classical compliance matrix found.')
            # if scrnout:
            # else:
            #     pass

        try:
            ln = keywordsIndex['tsm']
            bp.stff_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
            #old dic method to save refined stiffness matrix
            # sm.eff_props[1]['stiffness']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
        except KeyError:
            logger.info('No Timoshenko stiffness matrix found.')
            # if scrnout:
            # else:
            #     pass
        try:
            ln = keywordsIndex['tfm']
            bp.cmpl_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
            #old dic method to save refined compliance matrix
            # sm.eff_props[1]['compliance']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
        except KeyError:
            logger.info('No Timoshenko compliance matrix found.')
            # if scrnout:
            # else:
            #     pass

        if 'tc' in keywordsIndex.keys():
            ln = keywordsIndex['tc']
            bp.xt2, bp.xt3 = list(map(float, linesRead[ln + 2].split()))
        if 'sc' in keywordsIndex.keys():
            ln = keywordsIndex['sc']
            bp.xs2, bp.xs3 = list(map(float, linesRead[ln + 2].split()))
        if 'mc' in keywordsIndex.keys():
            ln = keywordsIndex['mc']
            bp.xm2, bp.xm3 = list(map(float, linesRead[ln + 2].split()))
        if 'gc' in keywordsIndex.keys():
            ln = keywordsIndex['gc']
            bp.xg2, bp.xg3 = list(map(float, linesRead[ln + 2].split()))

        #check whether trapeze effect analysis is on and read the correponding matrix
        # if 'te' in keywordsIndex.keys():
        #     try:
        #         ln = keywordsIndex['te_ag']
        #         sm.trapeze_effect['ag'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ag1--Ag1--Ag1--Ag1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_bk']
        #         sm.trapeze_effect['bk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Bk1--Bk1--Bk1--Bk1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_ck']
        #         sm.trapeze_effect['ck'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ck2--Ck2--Ck2--Ck2 matrix found.')
        #         else:
        #             pass    
        #     try:
        #         ln = keywordsIndex['te_dk']
        #         sm.trapeze_effect['dk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Dk3--Dk3--Dk3--Dk3 matrix found.')
        #         else:
        #             pass              

    ms.constitutive = bp

    return ms




def _readOutputFailureIndex(file):
    r"""
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


def write(
    sg:StructureGene, fn:str, file_format:str, analysis='h', sg_fmt:int=1,
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
        sg.writeInput(fn, _file_format, sfi, sff, sg_fmt, version, mesh_only)

    elif (analysis.lower().startswith('d')) or (analysis.lower().startswith('l')) or (analysis.lower().startswith('f')):
        sg.writeInputGlobal(fn+'.glb', _file_format, sfi, sff, analysis, version)

    return fn









def writeInput(sg, fn, file_format, sfi, sff, sg_fmt, version=None, mesh_only=False):
    """
    """

    logger.debug(f'writing sg input {fn}...')

    ssff = '{:' + sff + '}'
    if not version is None:
        sg.version = suv.Version(version)

    logger.debug('format version: {}'.format(sg.version))

    with open(fn, 'w') as file:
        if not mesh_only:
            sg._writeHeader(file, file_format, sfi, sff, sg_fmt, version)

        sg._writeMesh(file, file_format=file_format, sgdim=sg.sgdim, int_fmt=sfi, float_fmt=sff)

        if not mesh_only:
            sg._writeMOCombos(file, file_format, sfi, sff)

        if not mesh_only:
            sg._writeMaterials(file, file_format, sfi, sff)

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

        if m.stff:
            anisotropy = 2
        else:
            anisotropy = m.isotropy

        # print(m.stff)
        # print(anisotropy)

        if file_format.startswith('v'):
            sui.writeFormatIntegers(file, (mid, anisotropy), sfi, newline=False)
            if counter == 0:
                file.write('  # materials')
            file.write('\n')
        elif file_format.startswith('s'):
            sui.writeFormatIntegers(file, (mid, anisotropy, 1), sfi, newline=False)
            if counter == 0:
                file.write('  # materials')
            file.write('\n')
            sui.writeFormatFloats(file, (m.temperature, m.density), sff)

        # Write elastic properties
        if anisotropy == 0:
            # mpc = m.constants
            sui.writeFormatFloats(file, [m.e1, m.nu12], sff)

        elif anisotropy == 1:
            # mpc = m.constants
            sui.writeFormatFloats(file, [m.e1, m.e2, m.e3], sff)
            sui.writeFormatFloats(file, [m.g12, m.g13, m.g23], sff)
            sui.writeFormatFloats(file, [m.nu12, m.nu13, m.nu23], sff)


        elif anisotropy == 2:
            for i in range(6):
                sui.writeFormatFloats(file, m.stff[i][i:], sff)
                # for j in range(i, 6):
                #     file.write(sff.format(m.stff[i][j]))
                # file.write('\n')

        # print('sg.physics =', sg.physics)
        # print('m.cte =', m.cte)
        # print('m.specific_heat =', m.specific_heat)
        if sg.physics in [1, 4, 6]:
            sui.writeFormatFloats(file, m.cte+[m.specific_heat,], sff)

        if file_format.lower().startswith('v'):
            sui.writeFormatFloats(file, (m.density,), sff)

        file.write('\n')
        
        counter += 1

    file.write('\n')
    return









def _writeHeader(sg, file, file_format, sfi, sff, sg_fmt, version=None):
    ssfi = '{:' + sfi + '}'

    # VABS
    if file_format.startswith('v'):
        # format_flag  nlayer
        sui.writeFormatIntegers(file, [sg_fmt, len(sg.mocombos)])
        file.write('\n')

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
        sui.writeFormatIntegers(
            file, [model, sg.do_dampling, physics], sfi, newline=False)
        file.write('  # model_flag, damping_flag, thermal_flag\n\n')

        # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
        line = [0, 0, trapeze, vlasov]
        if (sg.initial_twist != 0.0) or (sg.initial_curvature[0] != 0.0) or (sg.initial_curvature[1] != 0.0):
            line[0] = 1
        if (sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0):
            line[1] = 1
        sui.writeFormatIntegers(file, line, sfi, newline=False)
        file.write('  # curve_flag, oblique_flag, trapeze_flag, vlasov_flag\n\n')

        # k1  k2  k3
        if line[0] == 1:
            sui.writeFormatFloats(
                file,
                [sg.initial_twist, sg.initial_curvature[0], sg.initial_curvature[1]],
                sff, newline=False
            )
            file.write('  # k11, k12, k13 (initial curvatures)\n\n')
        
        # oblique1  oblique2
        if line[1] == 1:
            sui.writeFormatFloats(file, sg.oblique, sff, newline=False)
            file.write('  # cos11, cos21 (obliqueness)\n\n')
        
        # nnode  nelem  nmate
        sui.writeFormatIntegers(
            file, [sg.nnodes, sg.nelems, sg.nmates], sfi, newline=False)
        file.write('  # nnode, nelem, nmate\n\n')


    # SwiftComp
    elif file_format.startswith('s'):
        # Extra inputs for dimensionally reducible structures
        if (sg.smdim == 1) or (sg.smdim == 2):
            # model (0: classical, 1: shear refined)
            file.write(ssfi.format(sg.model))
            file.write('  # structural model (0: classical, 1: shear refined)')
            file.write('\n\n')

            if sg.smdim == 1:  # beam
                # initial twist/curvatures
                # file.write((sff * 3 + '\n').format(0., 0., 0.))
                sui.writeFormatFloats(
                    file,
                    [sg.initial_twist, sg.initial_curvature[0], sg.initial_curvature[1]],
                    sff, newline=False
                )
                file.write('  # initial curvatures k11, k12, k13\n')
                file.write('\n')
                # oblique cross section
                # file.write((sff * 2 + '\n').format(1., 0.))
                sui.writeFormatFloats(file, sg.oblique, sff)

            elif sg.smdim == 2:  # shell
                # initial twist/curvatures
                # file.write((sff * 2 + '\n').format(
                #     sg.initial_curvature[0], sg.initial_curvature[1]
                # ))
                sui.writeFormatFloats(file, sg.initial_curvature, sff, newline=False)
                file.write('  # initial curvatures k12, k21\n')
                # if sg.geo_correct:
                # if sg.initial_curvature[0] != 0 or sg.initial_curvature[1] != 0:
                if version > '2.1':
                    sui.writeFormatFloats(file, sg.lame_params, sff, newline=False)
                    file.write('  # Lame parameters\n')
            file.write('\n')

        # Head
        nums = [
            sg.physics, sg.ndim_degen_elem, sg.use_elem_local_orient,
            sg.is_temp_nonuniform
        ]
        cmt = '  # analysis, elem_flag, trans_flag, temp_flag'
        if version > '2.1':
            nums += [sg.force_flag, sg.steer_flag]
            cmt = cmt + ', force_flag, steer_flag'
        sui.writeFormatIntegers(file, nums, sfi, newline=False)
        file.write(cmt)
        file.write('\n\n')
        # file.write((sfi * 6 + '\n').format(
        #     sg.sgdim,
        #     len(sg.nodes),
        #     len(sg.elements),
        #     len(sg.materials),
        #     sg.num_slavenodes,
        #     len(sg.mocombos)
        # ))
        sui.writeFormatIntegers(file, [
            sg.sgdim,
            sg.nnodes,
            sg.nelems,
            sg.nmates,
            sg.num_slavenodes,
            len(sg.mocombos)
        ], sfi, newline=False)
        file.write('  # nsg, nnode, nelem, nmate, nslave, nlayer')
        file.write('\n\n')

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

        sui.writeFormatIntegers(
            file,
            # (m.strength['criterion'], len(m.strength['constants'])),
            [m.failure_criterion, len(strength)],
            sfi
        )
        # file.write((sff+'\n').format(m.strength['chara_len']))
        sui.writeFormatFloats(file, [m.char_len,], sff)
        # sui.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
        sui.writeFormatFloats(file, strength, sff)
    return









def _writeInputDisplacements(sg, file, file_format, sff):
    sui.writeFormatFloats(file, sg.global_displacements, sff[2:-1])
    sui.writeFormatFloatsMatrix(file, sg.global_rotations, sff[2:-1])









def _writeInputLoads(sg, file, file_format, sfi, sff):
    if file_format.startswith('v'):
        if sg.model == 0:
            sui.writeFormatFloats(file, sg.global_loads)
        else:
            sui.writeFormatFloats(file, [sg.global_loads[i] for i in [0, 3, 4, 5]])
            sui.writeFormatFloats(file, [sg.global_loads[i] for i in [1, 2]])
            file.write('\n')
            sui.writeFormatFloats(file, sg.global_loads_dist[0])
            sui.writeFormatFloats(file, sg.global_loads_dist[1])
            sui.writeFormatFloats(file, sg.global_loads_dist[2])
            sui.writeFormatFloats(file, sg.global_loads_dist[3])
    elif file_format.startswith('s'):
        # file.write((sfi+'\n').format(sg.global_loads_type))
        for load_case in sg.global_loads:
            sui.writeFormatFloats(file, load_case, sff)
    file.write('\n')
    return









def writeInputGlobal(sg, fn, file_format, sfi, sff, analysis, version=None):
    with open(fn, 'w') as file:
        if analysis.startswith('d') or analysis.lower().startswith('l'):
            sg._writeInputDisplacements(file, file_format, sff)
        elif analysis.startswith('f'):
            sg._writeInputMaterialStrength(file, file_format, sfi, sff)

        if file_format.startswith('s'):
            # file.write((sfi+'\n').format(sg.global_loads_type))
            sui.writeFormatIntegers(file, [sg.global_loads_type, ], sfi)

        if analysis != 'f':
            sg._writeInputLoads(file, file_format, sfi, sff)

