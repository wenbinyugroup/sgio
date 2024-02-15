import logging

from sgio.core.sg import StructureGene
import sgio.utils as sutl
import sgio.model as smdl
import sgio.meshio as smsh

logger = logging.getLogger(__name__)


def readBuffer(f, file_format:str, format_version:str, model:int|str):
    """
    """
    sg = StructureGene()
    sg.version = format_version

    if isinstance(model, int):
        smdim = model
    elif isinstance(model, str):
        if model.upper()[:2] == 'SD':
            smdim = 3
        elif model.upper()[:2] == 'PL':
            smdim = 2
        elif model.upper()[:2] == 'BM':
            smdim = 1

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
def readOutputBuffer(
    file, analysis='h', sg:StructureGene=None, ext:str='', **kwargs):
    """
    """

    if analysis == 0 or analysis == 'h' or analysis == '':
        return _readOutputH(file, **kwargs)

    elif analysis == 1 or analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
        if ext == 'u':
            return _readOutputNodeDisplacement(file)
        elif ext == 'ele':
            return _readOutputElementStrainStress(file)

    elif analysis == 'f' or analysis == 3:
        # return readSCOutFailure(file, analysis)
        pass

    elif analysis == 'fe' or analysis == 4:
        # return readSCOutFailure(file, analysis)
        pass

    elif analysis == 'fi' or analysis == 5:
        output = {}
        _fi, _sr, _eids_sr_min = _readOutputFailureIndex(file)
        output['failure_index'] = _fi
        output['strength_ratio'] = _sr
        output['elems_sr_min'] = _eids_sr_min

        return output

    return




def _readOutputH(file, **kwargs):
    """Read VABS homogenization output.
    """

    try:
        model_type = kwargs['model_type'].upper()
    except KeyError:
        model_type = kwargs['submodel']

    model = kwargs.get('model', None)

    if model_type == 'BM1' or model_type == 1:
        return _readEulerBernoulliBeamModel(file, model)
    elif model_type == 'BM2' or model_type == 2:
        return _readTimoshenkoBeamModel(file, model)




def _readEulerBernoulliBeamModel(file, model=None):
    """
    """
    if model is None:
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




def _readTimoshenkoBeamModel(file, model=None):
    """
    """

    if model is None:
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




def _readOutputNodeDisplacement(file):
    """Read VABS output displacement on nodes.

    Parameters
    ----------
    file:
        File object of the output file.

    Returns
    -------
    dict[int, list[float]]:
        Averaged 3D strains in the beam coordinate system.
    """

    u = {}
    for i, line in enumerate(file):
        line = line.strip()
        if line == '':
            continue

        line = line.split()
        _nid = int(line[0])
        _ui = list(map(float, line[3:6]))

        u[_nid] = _ui

    return u




def _readOutputElementStrainStress(file):
    """Read VABS output averaged strains and stressed on elements.

    Parameters
    ----------
    file:
        File object of the output file.

    Returns
    -------
    dict[int, list[float]]:
        Averaged 3D strains in the beam coordinate system.
    dict[int, list[float]]:
        Averaged 3D stressess in the beam coordinate system.
    dict[int, list[float]]:
        Averaged 3D strains in the material coordinate system.
    dict[int, list[float]]:
        Averaged 3D stressess in the material coordinate system.
    """

    e, s, em, sm = {}, {}, {}, {}
    for i, line in enumerate(file):
        line = line.strip()
        if line == '':
            continue

        line = line.split()
        _eid = int(line[0])
        _ei = list(map(float, line[1:7]))
        _si = list(map(float, line[7:13]))
        _emi = list(map(float, line[13:19]))
        _smi = list(map(float, line[19:]))

        e[_eid] = _ei
        s[_eid] = _si
        em[_eid] = _emi
        sm[_eid] = _smi

    return e, s, em, sm




def _readOutputFailureIndex(file):
    """Read VABS output initial failure indices and strength ratios for elements.

    Parameters
    ----------
    file:
        File object of the output file.

    Returns
    -------
    dict[int, list[float]]:
        Initial failure index and strength ratio for each element.
    list[int]:
        ID of elemnets having the lowest strength ratio.
    """

    fi = {}
    sr = {}
    eids_sr_min = []

    for i, line in enumerate(file):
        line = line.strip()
        if (line == ''):
            continue
        if line.startswith('Failure index'):
            continue

        if (line.startswith('The sectional strength ratio is')):
            line = line.split()
            # _loc = line.index('existing')
            # _sr_min = float(line[tmp_id - 1])
            _eid = int(line[-1])
            eids_sr_min.append(_eid)
            # lines.pop()
            continue

        line = line.split()
        if len(line) == 3:
            # lines.append(line)
            fi[int(line[0])] = float(line[1])
            sr[int(line[0])] = float(line[2])

    # result = []
    # # fis = []
    # # srs = []
    # for line in lines:
    #     # line = line.strip().split()
    #     result.append([int(line[0]), float(line[1]), float(line[2])])
    #     # fis.append(float(line[1]))
    #     # srs.append(float(line[2]))

    return fi, sr, eids_sr_min
    # return result, sr_min, eid_sr_min




# def _readOutputStrengthRatio(fn_in):
#     lines = []
#     sr_min = None
#     with open(fn_in, 'r') as fin:
#         for i, line in enumerate(fin.readlines()):
#             line = line.strip()
#             if (line == ''):
#                 continue
#             if line.startswith('Failure index'):
#                 continue
#             # lines.append(line)
#             # initial failure indices and strength ratios
#             if (line.startswith('The sectional strength ratio is')):
#                 line = line.split()
#                 tmp_id = line.index('existing')
#                 sr_min = float(line[tmp_id - 1])
#                 # lines.pop()
#                 continue
#             line = line.split()
#             if len(line) == 3:
#                 lines.append(line)

#     # print(lines)
#     # initial failure indices and strength ratios
#     fis = []
#     srs = []
#     for line in lines:
#         # line = line.strip().split()
#         # results.append([int(line[0]), float(line[1]), float(line[2])])
#         fis.append(float(line[1]))
#         srs.append(float(line[2]))
#     return fis, srs, sr_min









# Writers


def writeBuffer(
    sg:StructureGene, file, analysis='h', sg_fmt:int=1, model=0,
    macro_responses:list[smdl.StateCase]=[],
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

    if sg is None:
        timoshenko_flag = model
    else:
        timoshenko_flag = 0
        trapeze_flag = 0
        vlasov_flag = 0
        if sg.model == 1:
            timoshenko_flag = 1
        elif sg.model == 2:
            timoshenko_flag = 1
            vlasov_flag = 1
        elif sg.model == 3:
            trapeze_flag = 1
        thermal_flag = 0
        if sg.physics == 1:
            thermal_flag = 3

    if analysis == 'h':
        writeInputBuffer(
            sg, file, sg_fmt,
            timoshenko_flag, vlasov_flag, trapeze_flag, thermal_flag,
            sfi, sff, version)

    elif (analysis == 'd') or (analysis == 'l') or (analysis.startswith('f')):
        if sg is None:
            materials = {}
        else:
            materials = sg.materials

        writeInputBufferGlobal(
            file, timoshenko_flag, analysis,
            macro_responses, materials,
            sfi=sfi, sff=sff)

    return









def writeInputBuffer(
    sg, file, sg_fmt,
    timoshenko_flag, vlasov_flag, trapeze_flag, thermal_flag,
    sfi:str='8d', sff:str='20.12e', version=None):
    """
    """

    logger.debug(f'writing sg input...')

    # ssff = '{:' + sff + '}'
    # if not version is None:
    #     sg.version = sutl.Version(version)
    sg.version = version

    logger.debug('format version: {}'.format(sg.version))

    nlayer = len(sg.mocombos)

    # timoshenko_flag = model
    # trapeze_flag = 0
    # vlasov_flag = 0
    # if sg.model == 1:
    #     timoshenko_flag = 1
    # elif sg.model == 2:
    #     timoshenko_flag = 1
    #     vlasov_flag = 1
    # elif sg.model == 3:
    #     trapeze_flag = 1
    # thermal_flag = 0
    # if sg.physics == 1:
    #     thermal_flag = 3

    curve_flag = 0
    if (sg.initial_twist != 0.0) or (sg.initial_curvature[0] != 0.0) or (sg.initial_curvature[1] != 0.0):
        curve_flag = 1
    initial_curvatures = [sg.initial_twist,]+sg.initial_curvature

    oblique_flag = 0
    if (sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0):
        oblique_flag = 1

    _writeHeader(
        sg_fmt, nlayer,
        timoshenko_flag, sg.do_damping, thermal_flag,
        curve_flag, oblique_flag, trapeze_flag, vlasov_flag,
        initial_curvatures, sg.oblique,
        sg.nnodes, sg.nelems, sg.nmates,
        file, sfi, sff)

    _writeMesh(sg, file, int_fmt=sfi, float_fmt=sff)

    # if not mesh_only:
    _writeMOCombos(sg, file, sfi, sff)

    # if not mesh_only:
    _writeMaterials(sg.materials, file, thermal_flag, sfi, sff)

    return









def _writeMesh(sg, file, int_fmt, float_fmt):
    """
    """
    logger.debug('writing mesh...')

    sg.mesh.write(file, 'vabs', sgdim=2, int_fmt=int_fmt, float_fmt=float_fmt)

    return









def _writeMOCombos(sg, file, sfi:str='8d', sff:str='20.12e'):
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




def _writeMaterial(
    mid:int, material:smdl.CauchyContinuumModel, file,
    thermal_flag, analysis, failure_criterion,
    sfi:str='8d', sff:str='20.12e'):
    """
    """

    anisotropy = material.get('isotropy')

    if analysis == 'h':
        # Write material properties for homogenization

        sutl.writeFormatIntegers(file, (mid, anisotropy), sfi, newline=False)
        file.write('  # material id, anisotropy\n')

        # Write elastic properties
        if anisotropy == 0:
            sutl.writeFormatFloats(file, [material.get('e'), material.get('nu')], sff)
            if thermal_flag == 3:
                sutl.writeFormatFloats(file, [material.get('alpha'),], sff)

        elif anisotropy == 1:
            sutl.writeFormatFloats(file, [material.get('e1'), material.get('e2'), material.get('e3')], sff)
            sutl.writeFormatFloats(file, [material.get('g12'), material.get('g13'), material.get('g23')], sff)
            sutl.writeFormatFloats(file, [material.get('nu12'), material.get('nu13'), material.get('nu23')], sff)
            if thermal_flag == 3:
                sutl.writeFormatFloats(
                    file, [material.get('alpha11'), material.get('alpha22'), material.get('alpha33')], sff)

        elif anisotropy == 2:
            for _i in range(6):
                for _j in range(_i, 6):
                    sutl.writeFormatFloats(
                        file, material.get(f'c{_i+1}{_j+1}'), sff)
            if thermal_flag == 3:
                sutl.writeFormatFloats(
                    file, [
                        material.get('alpha11'),
                        material.get('alpha12')*2,
                        material.get('alpha13')*2,
                        material.get('alpha22'),
                        material.get('alpha23')*2,
                        material.get('alpha33')
                    ],sff)

        sutl.writeFormatFloats(file, [material.get('density'),], sff)

    elif analysis == 'f':
        # Write material properties for failure analysis

        strength = []
        if anisotropy == 0:
            if failure_criterion == 1:
                pass
            elif failure_criterion == 2:
                pass
            elif failure_criterion == 3:
                pass
            elif failure_criterion == 4:
                pass
            elif failure_criterion == 5:
                pass
        else:
            if failure_criterion == 1:
                pass
            elif failure_criterion == 2:
                pass
            elif failure_criterion == 3:
                pass
            elif failure_criterion == 4:
                # Tsai-Wu
                strength = [
                    material.get('x1t'), material.get('x2t'), material.get('x3t'),
                    material.get('x1c'), material.get('x2c'), material.get('x3c'),
                    material.get('x23'), material.get('x13'), material.get('x12'),
                    # strength_constants['r'], m.strength_constants['t'], m.strength_constants['s'],
                ]
            elif failure_criterion == 5:
                pass

        sutl.writeFormatIntegers(
            file,
            # (m.strength['criterion'], len(m.strength['constants'])),
            [failure_criterion, len(strength)],
            sfi
        )
        # file.write((sff+'\n').format(m.strength['chara_len']))
        # sutl.writeFormatFloats(file, [m.char_len,], sff)
        # sutl.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
        sutl.writeFormatFloats(file, strength, sff)


    file.write('\n')

    return




def _writeMaterials(
    dict_materials, file, thermal_flag=0, sfi:str='8d', sff:str='20.12e'):
    """
    """

    logger.debug('writing materials...')

    # counter = 0
    for mid, m in dict_materials.items():
        _writeMaterial(mid, m, file, thermal_flag, sfi, sff)

    file.write('\n')
    return









def _writeHeader(
    format_flag, nlayer,
    timoshenko_flag, damping_flag, thermal_flag,
    curve_flag, oblique_flag, trapeze_flag, vlasov_flag,
    initial_curvatures, obliqueness,
    nnode, nelem, nmate,
    file, sfi:str='8d', sff:str='20.12e'):
    # ssfi = '{:' + sfi + '}'

    # format_flag  nlayer
    sutl.writeFormatIntegers(file, [format_flag, nlayer], newline=False)
    file.write('  # format_flag, nlayer\n\n')

    # timoshenko_flag  damping_flag  thermal_flag
    sutl.writeFormatIntegers(
        file, [timoshenko_flag, damping_flag, thermal_flag], sfi, newline=False)
    file.write('  # model_flag, damping_flag, thermal_flag\n\n')

    # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
    line = [curve_flag, oblique_flag, trapeze_flag, vlasov_flag]
    # if (sg.initial_twist != 0.0) or (sg.initial_curvature[0] != 0.0) or (sg.initial_curvature[1] != 0.0):
    #     line[0] = 1
    # if (sg.oblique[0] != 1.0) or (sg.oblique[1] != 0.0):
    #     line[1] = 1
    sutl.writeFormatIntegers(file, line, sfi, newline=False)
    file.write('  # curve_flag, oblique_flag, trapeze_flag, vlasov_flag\n\n')

    # k1  k2  k3
    if line[0] == 1:
        sutl.writeFormatFloats(
            file, initial_curvatures, sff, newline=False
        )
        file.write('  # k11, k12, k13 (initial curvatures)\n\n')
    
    # oblique1  oblique2
    if line[1] == 1:
        sutl.writeFormatFloats(file, obliqueness, sff, newline=False)
        file.write('  # cos11, cos21 (obliqueness)\n\n')
    
    # nnode  nelem  nmate
    sutl.writeFormatIntegers(
        file, [nnode, nelem, nmate], sfi, newline=False)
    file.write('  # nnode, nelem, nmate\n\n')

    return









# def _writeInputMaterialStrength(sg, file, sfi, sff):
#     for i, m in sg.materials.items():
#         # print(m.strength)
#         # print(m.failure_criterion)
#         # print(m.char_len)

#         # file.write('{} {}'.format(m.failure_criterion, len(m.strength)))

#         strength = []
#         if m.type == 0:
#             pass
#         else:
#             if m.failure_criterion == 1:
#                 pass
#             elif m.failure_criterion == 2:
#                 pass
#             elif m.failure_criterion == 3:
#                 pass
#             elif m.failure_criterion == 4:
#                 # Tsai-Wu
#                 strength = [
#                     m.strength_constants['xt'], m.strength_constants['yt'], m.strength_constants['zt'],
#                     m.strength_constants['xc'], m.strength_constants['yc'], m.strength_constants['zc'],
#                     m.strength_constants['r'], m.strength_constants['t'], m.strength_constants['s'],
#                 ]
#             elif m.failure_criterion == 5:
#                 pass

#         sutl.writeFormatIntegers(
#             file,
#             # (m.strength['criterion'], len(m.strength['constants'])),
#             [m.failure_criterion, len(strength)],
#             sfi
#         )
#         # file.write((sff+'\n').format(m.strength['chara_len']))
#         sutl.writeFormatFloats(file, [m.char_len,], sff)
#         # sutl.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
#         sutl.writeFormatFloats(file, strength, sff)
#     return









def _writeDisplacementRotation(
    # macro_response:smdl.SectionResponse,
    file,
    displacement:list[float]=[0, 0, 0],
    rotation:list[list[float]]=[[1,0,0],[0,1,0],[0,0,1]],
    sff:str='20.12e'):

    # sutl.writeFormatFloats(file, macro_response.getDisplacement(), sff)
    # sutl.writeFormatFloatsMatrix(file, macro_response.getDirectionCosine(), sff)
    sutl.writeFormatFloats(file, displacement, sff)
    file.write('\n')
    sutl.writeFormatFloatsMatrix(file, rotation, sff)









def _writeLoad(
    file, macro_response:smdl.StateCase, model, sff:str='20.12e'):

    # _load = macro_response.getLoad()
    _load = macro_response.load.data

    if model == 0 or model == 'BM1':
        # sutl.writeFormatFloats(file, macro_response.getLoad())
        sutl.writeFormatFloats(file, _load, fmt=sff)

    elif model == 1 or model == 'BM2':
        sutl.writeFormatFloats(file, [_load[i] for i in [0, 3, 4, 5]], fmt=sff)
        sutl.writeFormatFloats(file, [_load[i] for i in [1, 2]], fmt=sff)
        file.write('\n')

        # _distr_load = macro_response.getDistributedLoad()
        _distr_load = macro_response.distributed_load
        if _distr_load is None:
            _distr_load = [[0,]*6]*4
        else:
            _distr_load = _distr_load.data
        sutl.writeFormatFloats(file, _distr_load[0], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[1], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[2], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[3], fmt=sff)

    file.write('\n')

    return




def _writeGlobalResponses(
    file, macro_responses:list[smdl.StateCase], model, sff:str='20.12e'):

    for _i, _response in enumerate(macro_responses):
        if _i == 0:
            # _writeDisplacementRotation(_response, file, sff)
            _disp = _response.displacement
            if _disp is None:
                _disp = [0, 0, 0]
            else:
                _disp = _disp.data

            _rot = _response.rotation
            if _rot is None:
                _rot = [[1,0,0],[0,1,0],[0,0,1]]
            else:
                _rot = _rot.data

            _writeDisplacementRotation(
                file=file,
                displacement=_disp,
                rotation=_rot,
                sff=sff
            )

            file.write('\n')

        _writeLoad(file, _response, model, sff)

    return









def writeInputBufferGlobal(
    file, model, analysis,
    macro_responses:list[smdl.StateCase]=[],
    dict_materials={},
    sfi:str='8d', sff:str='20.12e'):
    """Write material strength and global/macro responses to a file.

    Parameters
    ----------
    file:
        File object to which data will be written.
    model:
        Model of the global/macro structure.
    analysis:
        Identifier for the analysis. If 'f' (failure analysis), then material strengh will be written.
    """

    if analysis.startswith('f'):
        _writeMaterials(dict_materials, file, sfi=sfi, sff=sff)

    _writeGlobalResponses(file, macro_responses, model, sff)

