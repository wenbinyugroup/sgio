import logging

import sgio.utils.io as sui
# import sgio.utils.logger as mul
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

    if smdim == 1:
        line = sui.readNextNonEmptyLine(file)
        configs['model'] = int(line.split()[0])
        line = sui.readNextNonEmptyLine(file)
        configs['curvature'] = list(map(float, line.split()[:3]))
        line = sui.readNextNonEmptyLine(file)
        configs['oblique'] = list(map(float, line.split()[:2]))
    elif smdim == 2:
        line = sui.readNextNonEmptyLine(file)
        configs['model'] = int(line.split()[0])
        line = sui.readNextNonEmptyLine(file)
        configs['curvature'] = list(map(float, line.split()[:2]))
        if format_version >= '2.2':
            line = sui.readNextNonEmptyLine(file)
            configs['lame'] = list(map(float, line.split()[:2]))

    line = sui.readNextNonEmptyLine(file)
    line = line.split()
    configs['physics'] = int(line[0])
    configs['ndim_degen_elem'] = int(line[1])
    configs['use_elem_local_orient'] = int(line[2])
    configs['is_temp_nonuniform'] = int(line[3])
    if format_version >= '2.2':
        configs['force_flag'] = int(line[4])
        configs['steer_flag'] = int(line[5])

    line = sui.readNextNonEmptyLine(file)
    line = line.split()
    configs['sgdim'] = int(line[0])
    configs['num_nodes'] = int(line[1])
    configs['num_elements'] = int(line[2])
    configs['num_materials'] = int(line[3])
    configs['num_slavenodes'] = int(line[4])
    configs['num_mat_angle3_comb'] = int(line[5])

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
        mate_id, isotropy, ntemp = list(map(int, line))

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

        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()
        line = line.split()
        temperature, density = list(map(float, line))
        mp.temperature = temperature

        # Read conductivity properties

        # Read elastic properties
        elastic_props = _readElasticProperty(file, isotropy)
        mp.setElasticProperty(elastic_props, isotropy)

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




def readOutBeamProperty(fn, scrnout=True):
    """Read SwiftComp homogenization results

    Parameters
    ----------
    fn : str
        SwiftComp output file name (e.g. example.sg.k).
    scrnout : bool, default True
        Switch of printing cmd output.

    Returns
    -------
    msgpi.sg.BeamProperty
        Material/sectional properties.
    """
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    # sm = mms.MaterialSection(smdim = 1)
    # bp = mmbm.BeamProperty()
    bp = sgmodel.MaterialSection()

    linesRead = []
    keywordsIndex = {}


    with open(fn, 'r') as fin:
        ln = -1
        for line in fin:

            line = line.strip()

            if len(line) > 0:
                linesRead.append(line)
                ln += 1
            else:
                continue

            if '-----' in line:
                continue


            # Inertial properties
            # -------------------

            elif 'Effective Mass Matrix' in line:
                keywordsIndex['mass'] = ln
            elif 'Mass Center Location' in line:
                keywordsIndex['mc'] = ln
            elif 'Mass per unit span' in line:
                bp.mu = float(line.split()[-1])
            elif 'i11' in line:
                bp.i11 = float(line.split()[-1])
            elif 'i22' in line:
                bp.i22 = float(line.split()[-1])
            elif 'i33' in line:
                bp.i33 = float(line.split()[-1])
            elif 'principal inertial axes rotated' in line:
                line = line.split()
                tmp_id = line.index('degrees')
                bp.phi_pia = float(line[tmp_id - 1])
            elif 'Mass-Weighted Radius of Gyration' in line:
                bp.rg = float(line.split()[-1])


            # Structural properties
            # ---------------------

            elif 'Effective Stiffness Matrix' in line:
                keywordsIndex['csm'] = ln
            elif 'Effective Compliance Matrix' in line:
                keywordsIndex['cfm'] = ln

            elif 'Tension Center Location' in line:
                keywordsIndex['tc'] = ln
            elif 'extension stiffness EA' in line:
                bp.ea = float(line.split()[-1])
            elif 'torsional stiffness GJ' in line:
                bp.gj = float(line.split()[-1])
            elif 'Principal bending stiffness EI22' in line:
                bp.ei22 = float(line.split()[-1])
            elif 'Principal bending stiffness EI33' in line:
                bp.ei33 = float(line.split()[-1])
            elif 'principal bending axes rotated' in line:
                line = line.split()
                tmp_id = line.index('degrees')
                bp.phi_pba = float(line[tmp_id - 1])

            elif 'Timoshenko Stiffness Matrix' in line:
                keywordsIndex['tsm'] = ln
            elif 'Timoshenko Compliance Matrix' in line:
                keywordsIndex['tfm'] = ln

            elif 'Shear Center Location' in line:
                keywordsIndex['sc'] = ln
            elif 'Principal shear stiffness GA22' in line:
                bp.ga22 = float(line.split()[-1])
            elif 'Principal shear stiffness GA33' in line:
                bp.ga33 = float(line.split()[-1])
            elif 'principal shear axes rotated' in line:
                line = line.split()
                tmp_id = line.index('degrees')
                bp.phi_psa = float(line[tmp_id - 1])


    ln = keywordsIndex['mass']
    bp.mass = sui.textToMatrix(linesRead[ln + 2:ln + 8])

    #check whether the analysis is Vlasov or timoshenko
    #Read stiffness matrix and compliance matrix
    if 'vsm' in keywordsIndex.keys():
        pass

    else:
        try:
            ln = keywordsIndex['csm']
            bp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 6])
        except KeyError:
            if scrnout:
                print('No classical stiffness matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['cfm']
            bp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 6])
        except KeyError:
            if scrnout:
                print('No classical flexibility matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['tsm']
            bp.stff_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
        except KeyError:
            if scrnout:
                print('No Timoshenko stiffness matrix found.')
            else:
                pass
        try:
            ln = keywordsIndex['tfm']
            bp.cmpl_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
        except KeyError:
            if scrnout:
                print('No Timoshenko flexibility matrix found.')
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


    return bp




def readOutShellProperty(fn, scrnout=True):
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    # sm = mms.MaterialSection(smdim = 1)
    # sp = mmps.ShellProperty()
    sp = sgmodel.MaterialSection()

    linesRead = []
    keywordsIndex = {}

    with open(fn, 'r') as fin:
        ln = -1
        prop_plane = None
        for line in fin:

            line = line.strip()

            if len(line) > 0:
                linesRead.append(line)
                ln += 1
            else:
                continue

            if '-----' in line:
                continue

            # Inertial properties
            # -------------------

            elif 'Effective Mass Matrix' in line:
                keywordsIndex['mass'] = ln
            elif 'Mass Center Location' in line:
                sp.xm3 = float(line.split()[-1])
            elif 'i11' in line:
                sp.i11 = float(line.split()[-1])
                sp.i22 = sp.i11


            # Structural properties
            # ---------------------

            elif 'Effective Stiffness Matrix' in line:
                keywordsIndex['stff'] = ln
            elif 'Effective Compliance Matrix' in line:
                keywordsIndex['cmpl'] = ln

            elif 'Geometric Correction to the Stiffness Matrix' in line:
                keywordsIndex['geo_to_stff'] = ln
            elif 'Total Stiffness Matrix after Geometric Correction' in line:
                keywordsIndex['stff_geo'] = ln

            elif 'In-Plane' in line:
                prop_plane = 'in'
            elif 'Flexural' in line:
                prop_plane = 'out'

            elif 'E1' in line:
                if prop_plane == 'in':
                    sp.e1_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.e1_o = float(line.split('=')[-1])
            elif 'E2' in line:
                if prop_plane == 'in':
                    sp.e2_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.e2_o = float(line.split('=')[-1])
            elif 'G12' in line:
                if prop_plane == 'in':
                    sp.g12_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.g12_o = float(line.split('=')[-1])
            elif 'nu12' in line:
                if prop_plane == 'in':
                    sp.nu12_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.nu12_o = float(line.split('=')[-1])
            elif 'eta121' in line:
                if prop_plane == 'in':
                    sp.eta121_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.eta121_o = float(line.split('=')[-1])
            elif 'eta122' in line:
                if prop_plane == 'in':
                    sp.eta122_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.eta122_o = float(line.split('=')[-1])

            # Thermal properties
            # ---------------------

            elif 'N11T' in line:
                sp.n11_t = float(line.split('=')[-1])
            elif 'N22T' in line:
                sp.n22_t = float(line.split('=')[-1])
            elif 'N12T' in line:
                sp.n12_t = float(line.split('=')[-1])
            elif 'M11T' in line:
                sp.m11_t = float(line.split('=')[-1])
            elif 'M22T' in line:
                sp.m22_t = float(line.split('=')[-1])
            elif 'M12T' in line:
                sp.m12_t = float(line.split('=')[-1])

    try:
        ln = keywordsIndex['mass']
        sp.mass = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No mass matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['stff']
        sp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical stiffness matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['cmpl']
        sp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical flexibility matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['geo_to_stff']
        sp.geo_correction_stff = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No geometric correction matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['stff_geo']
        sp.stff_geo = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No geometric corrected stiffness matrix found.')
        else:
            pass


    return sp









def readOutMaterialProperty(fn, scrnout=True):
    r"""
    """
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    # mp = mmsd.MaterialProperty()
    mp = sgmodel.MaterialSection()

    linesRead = []
    keywordsIndex = {}

    with open(fn, 'r') as fin:
        ln = -1

        for line in fin:

            line = line.strip()

            if len(line) > 0:
                linesRead.append(line)
                ln += 1
            else:
                continue

            if '-----' in line:
                continue

            if 'The Effective Stiffness Matrix' in line:
                keywordsIndex['stff'] = ln
            if 'The Effective Compliance Matrix' in line:
                keywordsIndex['cmpl'] = ln
            if 'The Engineering Constants' in line:
                keywordsIndex['const'] = ln
            if 'Effective Density' in line:
                keywordsIndex['density'] = ln

            # Thermal properties
            # ---------------------

            elif 'alpha11' in line:
                _a11 = float(line.split('=')[-1])
            elif 'alpha22' in line:
                _a22 = float(line.split('=')[-1])
            elif 'alpha33' in line:
                _a33 = float(line.split('=')[-1])
            elif '2alpha23' in line:
                _2a23 = float(line.split('=')[-1])
            elif '2alpha13' in line:
                _2a13 = float(line.split('=')[-1])
            elif '2alpha12' in line:
                _2a12 = float(line.split('=')[-1])
                mp.cte = [_a11, _a22, _a33, _2a23, _2a13, _2a12]

            elif 'Dthetatheta' in line:
                mp.d_thetatheta = float(line.split('=')[-1])
            elif 'Feff' in line:
                mp.f_eff = float(line.split('=')[-1])
                _t1 = 0
                _tm = 1
                _t = _t1 + _tm
                mp.specific_heat = mp.d_thetatheta - _t * mp.f_eff

    try:
        ln = keywordsIndex['stff']
        mp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical stiffness matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['cmpl']
        mp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical flexibility matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['const']
        for line in linesRead[ln + 2:ln + 11]:
            line = line.strip()
            line = line.split('=')
            label = line[0].strip().lower()
            value = float(line[-1].strip())
            mp.constants[label] = value
    except KeyError:
        print('No engineering constants found.')

    line = linesRead[keywordsIndex['density']]
    line = line.strip().split('=')
    mp.density = float(line[-1].strip())


    return mp









def readOutHomo(fn, smdim, scrnout=True):
    """Read SwiftComp homogenization results.

    :param fn: SwiftComp output file (e.g. example.sg.k)
    :type fn: string

    :param smdim: Dimension of the structural model
    :type smdim: int
    """
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    if smdim == 1:
        out = readOutBeamProperty(fn, scrnout)
    elif smdim == 2:
        out = readOutShellProperty(fn, scrnout)
    elif smdim == 3:
        out = readOutMaterialProperty(fn, scrnout)


    return out









def readOutFailure(fn_sc_out_fi, failure_analysis):
    r"""
    """
    # if not logger:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sc failure analysis ({}) output file: {}...'.format(failure_analysis, fn_sc_out_fi))

    lines = []
    kw_index = {}
    results = []
    with open(fn_sc_out_fi, 'r') as fin:
        for i, line in enumerate(fin):
            lines.append(line)
            if failure_analysis == 'f':
                # initial failue strength
                if 'Initial Failure Strengths' in line:
                    kw_index['Initial Failure Strengths'] = i
            elif failure_analysis == 'fe':
                # initial failure envelope
                pass
            elif failure_analysis == 'fi':
                # initial failure indices and strength ratios
                pass

    if failure_analysis == 'f':
        # initial failure strength
        try:
            index = kw_index['Initial Failure Strengths']
            for line in lines[index + 2:index + 8]:
                line = line.strip().split()
                results.append(list(map(float, line[:2])))
        except KeyError:
            print('No initial failure strength found.')

    elif failure_analysis == 'fe':
        # initial failure envelope
        for line in lines:
            line = line.strip().split()
            results.append([int(line[0]), float(line[1]), float(line[2])])

    elif failure_analysis == 'fi':
        # initial failure indices and strength ratios
        eids = []
        fis = []
        srs = []
        for line in lines:
            line = line.strip().split()
            # results.append([int(line[0]), float(line[1]), float(line[2])])
            eids.append(float(line[0]))
            fis.append(float(line[1]))
            srs.append(float(line[2]))
        return eids, fis, srs

    return results


