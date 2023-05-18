import logging

import sgio.utils.io as sui
import sgio.model as sgmodel

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

    mesh = sm.read(
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

def readOutFailureIndex(fn, solver):
    r"""
    """
    # if not logger:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sg failure indices and strengh ratios: {}...'.format(fn))

    lines = []
    load_case = 0
    sr_min = None
    with open(fn, 'r') as fobj:
        for i, line in enumerate(fobj):
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









def readOutHomo(fn, scrnout=True):
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
    bp = sgmodel.MaterialSection()

    linesRead = []
    keywordsIndex = {}


    with open(fn, 'r') as fin:
        ln = -1
        lines = fin.readlines()
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
            if scrnout:
                print('No classical stiffness matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['cfm']
            bp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 6])
            #old dic method to save classical compliance
            # sm.eff_props[1]['compliance']['classical'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        except KeyError:
            if scrnout:
                print('No classical compliance matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['tsm']
            bp.stff_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
            #old dic method to save refined stiffness matrix
            # sm.eff_props[1]['stiffness']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
        except KeyError:
            if scrnout:
                print('No Timoshenko stiffness matrix found.')
            else:
                pass
        try:
            ln = keywordsIndex['tfm']
            bp.cmpl_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
            #old dic method to save refined compliance matrix
            # sm.eff_props[1]['compliance']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
        except KeyError:
            if scrnout:
                print('No Timoshenko compliance matrix found.')
            else:
                pass

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

    return bp




def readOutStrengthRatio(fn_in):
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


