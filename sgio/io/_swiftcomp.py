import logging

from sgio.core.sg import StructureGene
# from sgio.model import Model
import sgio.utils as sutl
import sgio.model as smdl
import sgio.meshio as smsh


logger = logging.getLogger(__name__)


# ====================================================================
# Readers
# ====================================================================


# Read input
# ----------

def readInputBuffer(file, format_version:str, smdim:int):
    """
    """
    logger.debug(f'local variables:\n{sutl.convertToPrettyString(locals())}')
    sg = StructureGene()
    sg.version = format_version
    sg.smdim = smdim

    # Read head
    configs = _readHeader(file, format_version, smdim)
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
    sg.mesh = _readMesh(file, sg.sgdim, nnode, nelem, _use_elem_local_orient)

    # Read material in-plane angle combinations
    nma_comb = configs['num_mat_angle3_comb']
    sg.mocombos = _readMaterialRotationCombinations(file, nma_comb)

    # Read materials
    nmate = configs['num_materials']
    sg.materials = _readMaterials(file, nmate)

    return sg





def _readHeader(file, format_version:str, smdim:int):
    """
    """

    logger.debug('reading header...')

    configs = {}

    if smdim == 1:
        line = sutl.readNextNonEmptyLine(file)
        configs['model'] = int(line.split()[0])
        line = sutl.readNextNonEmptyLine(file)
        configs['curvature'] = list(map(float, line.split()[:3]))
        line = sutl.readNextNonEmptyLine(file)
        configs['oblique'] = list(map(float, line.split()[:2]))
    elif smdim == 2:
        line = sutl.readNextNonEmptyLine(file)
        configs['model'] = int(line.split()[0])
        line = sutl.readNextNonEmptyLine(file)
        configs['curvature'] = list(map(float, line.split()[:2]))
        if format_version >= '2.2':
            line = sutl.readNextNonEmptyLine(file)
            configs['lame'] = list(map(float, line.split()[:2]))

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['physics'] = int(line[0])
    configs['ndim_degen_elem'] = int(line[1])
    configs['use_elem_local_orient'] = int(line[2])
    configs['is_temp_nonuniform'] = int(line[3])
    if format_version >= '2.2':
        configs['force_flag'] = int(line[4])
        configs['steer_flag'] = int(line[5])

    line = sutl.readNextNonEmptyLine(file)
    line = line.split()
    configs['sgdim'] = int(line[0])
    configs['num_nodes'] = int(line[1])
    configs['num_elements'] = int(line[2])
    configs['num_materials'] = int(line[3])
    configs['num_slavenodes'] = int(line[4])
    configs['num_mat_angle3_comb'] = int(line[5])

    return configs




def _readMesh(file, sgdim:int, nnode:int, nelem:int, read_local_frame):
    """
    """

    logger.debug('reading mesh...')

    mesh = smsh.read(
        file, 'sc',
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




def _readMaterials(file, nmate:int):
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

        material = _readMaterial(file, isotropy, ntemp)

        materials[mate_id] = material

        counter += 1

    return materials




def _readMaterial(file, isotropy:int, ntemp:int=1):
    """
    """

    # mp = smdl.MaterialProperty()
    # mp = smdl.MaterialSection()
    mp = smdl.CauchyContinuumModel()
    # mp.isotropy = isotropy
    mp.set('isotropy', isotropy)

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
        mp.setElastic(elastic_props, isotropy)

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









# Read output
# -----------
def readOutputBuffer(
    file, analysis=0, smdim:int=0,
    sg:StructureGene=None, **kwargs
    ):

    if analysis == 0 or analysis == 'h' or analysis == '':
        return _readOutputH(file, smdim, **kwargs)

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




def _readOutputH(file, smdim, **kwargs):
    """Read SwiftComp homogenization results.

    :param fn: SwiftComp output file (e.g. example.sg.k)
    :type fn: string

    :param smdim: Dimension of the structural model
    :type smdim: int
    """

    try:
        model = kwargs['model']
    except KeyError:
        model = kwargs['submodel']

    if smdim == 1:
        out = _readOutputBeamModel(file, model=model)
    elif smdim == 2:
        out = _readOutputShellModel(file, model=model)
    elif smdim == 3:
        out = _readOutputCauchyContinuumModel(file)


    return out





def _readOutputBeamModel(file, model):
    """
    """

    if model == 'BM1' or model == 1:
        return _readEulerBernoulliBeamModel(file)
    elif model == 'BM2' or model == 2:
        return _readTimoshenkoBeamModel(file)



def _readEulerBernoulliBeamModel(file):
    """Read homogenization output for Euler-Bernoulli beam model.
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


        # Inertial properties
        # -------------------

        elif 'Effective Mass Matrix' in line:
            line = file.readline()
            _mass, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.mass = _mass

        elif 'Mass Center Location' in line:
            for _ in range(2): line = file.readline()
            model.xm2, model.xm3 = list(map(float, line.split()))
        elif 'Mass per unit span' in line:
            model.mu = float(line.split()[-1])
        elif 'i11' in line:
            model.i11 = float(line.split()[-1])
        elif 'i22' in line:
            model.i22 = float(line.split()[-1])
        elif 'i33' in line:
            model.i33 = float(line.split()[-1])
        elif 'principal inertial axes' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
                model.phi_pia = float(line[tmp_id - 1])
            except ValueError:
                model.phi_pia = 0
        elif 'Mass-Weighted Radius of Gyration' in line:
            model.rg = float(line.split()[-1])


        # Structural properties
        # ---------------------

        elif 'Effective Stiffness Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4,
                number_type=float, comments=['----',]
                )
            model.stff = _matrix
        elif 'Effective Compliance Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4,
                number_type=float, comments=['----',]
                )
            model.cmpl = _matrix

        elif 'Tension Center Location' in line:
            for _ in range(2): line = file.readline()
            model.xt2, model.xt3 = list(map(float, line.split()))

        elif 'extension stiffness EA' in line:
            model.ea = float(line.split()[-1])
        elif 'torsional stiffness GJ' in line:
            model.gj = float(line.split()[-1])
        elif 'Principal bending stiffness EI22' in line:
            model.ei22 = float(line.split()[-1])
        elif 'Principal bending stiffness EI33' in line:
            model.ei33 = float(line.split()[-1])
        elif 'principal bending axes' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
                model.phi_pba = float(line[tmp_id - 1])
            except ValueError:
                model.phi_pba = 0

        line = file.readline()

    return model




def _readTimoshenkoBeamModel(file):
    """Read homogenization output for Timoshenko beam model.
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


        # Inertial properties
        # -------------------

        elif 'Effective Mass Matrix' in line:
            line = file.readline()
            _mass, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.mass = _mass

        elif 'Mass Center Location' in line:
            for _ in range(2): line = file.readline()
            model.xm2, model.xm3 = list(map(float, line.split()))
        elif 'Mass per unit span' in line:
            model.mu = float(line.split()[-1])
        elif 'i11' in line:
            model.i11 = float(line.split()[-1])
        elif 'i22' in line:
            model.i22 = float(line.split()[-1])
        elif 'i33' in line:
            model.i33 = float(line.split()[-1])
        elif 'principal inertial axes' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
                model.phi_pia = float(line[tmp_id - 1])
            except ValueError:
                model.phi_pia = 0
        elif 'Mass-Weighted Radius of Gyration' in line:
            model.rg = float(line.split()[-1])


        # Structural properties
        # ---------------------

        elif 'Effective Stiffness Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4,
                number_type=float, comments=['----',]
                )
            model.stff_c = _matrix
        elif 'Effective Compliance Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4,
                number_type=float, comments=['----',]
                )
            model.cmpl_c = _matrix

        elif 'Effective Timoshenko Stiffness Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.stff = _matrix
        elif 'Effective Timoshenko Compliance Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.cmpl = _matrix

        elif 'Tension Center Location' in line:
            for _ in range(2): line = file.readline()
            model.xt2, model.xt3 = list(map(float, line.split()))

        elif 'Shear Center Location' in line:
            for _ in range(2): line = file.readline()
            model.xs2, model.xs3 = list(map(float, line.split()))

        elif 'extension stiffness EA' in line:
            model.ea = float(line.split()[-1])
        elif 'torsional stiffness GJ' in line:
            model.gj = float(line.split()[-1])
        elif 'Principal bending stiffness EI22' in line:
            model.ei22 = float(line.split()[-1])
        elif 'Principal bending stiffness EI33' in line:
            model.ei33 = float(line.split()[-1])
        elif 'principal bending axes' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
                model.phi_pba = float(line[tmp_id - 1])
            except ValueError:
                model.phi_pba = 0
        elif 'Principal shear stiffness GA22' in line:
            model.ga22 = float(line.split()[-1])
        elif 'Principal shear stiffness GA33' in line:
            model.ga33 = float(line.split()[-1])
        elif 'principal shear axes' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
                model.phi_psa = float(line[tmp_id - 1])
            except ValueError:
                model.phi_psa = 0

        line = file.readline()

    return model




# def _readOutputBeamModel(file):
#     """Read homogenization output for Euler-Bernoulli beam model.
#     """
#     # if logger is None:
#     #     logger = mul.initLogger(__name__)

#     # sm = mms.MaterialSection(smdim = 1)
#     # bp = mmbm.BeamProperty()
#     bp = smdl.MaterialSection()

#     linesRead = []
#     keywordsIndex = {}


#     # with open(fn, 'r') as fin:
#     ln = -1
#     for line in file:

#         line = line.strip()

#         if len(line) > 0:
#             linesRead.append(line)
#             ln += 1
#         else:
#             continue

#         if '-----' in line:
#             continue


#         # Inertial properties
#         # -------------------

#         elif 'Effective Mass Matrix' in line:
#             keywordsIndex['mass'] = ln
#         elif 'Mass Center Location' in line:
#             keywordsIndex['mc'] = ln
#         elif 'Mass per unit span' in line:
#             bp.mu = float(line.split()[-1])
#         elif 'i11' in line:
#             bp.i11 = float(line.split()[-1])
#         elif 'i22' in line:
#             bp.i22 = float(line.split()[-1])
#         elif 'i33' in line:
#             bp.i33 = float(line.split()[-1])
#         elif 'principal inertial axes rotated' in line:
#             line = line.split()
#             tmp_id = line.index('degrees')
#             bp.phi_pia = float(line[tmp_id - 1])
#         elif 'Mass-Weighted Radius of Gyration' in line:
#             bp.rg = float(line.split()[-1])


#         # Structural properties
#         # ---------------------

#         elif 'Effective Stiffness Matrix' in line:
#             keywordsIndex['csm'] = ln
#         elif 'Effective Compliance Matrix' in line:
#             keywordsIndex['cfm'] = ln

#         elif 'Tension Center Location' in line:
#             keywordsIndex['tc'] = ln
#         elif 'extension stiffness EA' in line:
#             bp.ea = float(line.split()[-1])
#         elif 'torsional stiffness GJ' in line:
#             bp.gj = float(line.split()[-1])
#         elif 'Principal bending stiffness EI22' in line:
#             bp.ei22 = float(line.split()[-1])
#         elif 'Principal bending stiffness EI33' in line:
#             bp.ei33 = float(line.split()[-1])
#         elif 'principal bending axes rotated' in line:
#             line = line.split()
#             tmp_id = line.index('degrees')
#             bp.phi_pba = float(line[tmp_id - 1])

#         elif 'Timoshenko Stiffness Matrix' in line:
#             keywordsIndex['tsm'] = ln
#         elif 'Timoshenko Compliance Matrix' in line:
#             keywordsIndex['tfm'] = ln

#         elif 'Shear Center Location' in line:
#             keywordsIndex['sc'] = ln
#         elif 'Principal shear stiffness GA22' in line:
#             bp.ga22 = float(line.split()[-1])
#         elif 'Principal shear stiffness GA33' in line:
#             bp.ga33 = float(line.split()[-1])
#         elif 'principal shear axes rotated' in line:
#             line = line.split()
#             tmp_id = line.index('degrees')
#             bp.phi_psa = float(line[tmp_id - 1])


#     ln = keywordsIndex['mass']
#     bp.mass = sutl.textToMatrix(linesRead[ln + 2:ln + 8])

#     #check whether the analysis is Vlasov or timoshenko
#     #Read stiffness matrix and compliance matrix
#     if 'vsm' in keywordsIndex.keys():
#         pass

#     else:
#         try:
#             ln = keywordsIndex['csm']
#             bp.stff = sutl.textToMatrix(linesRead[ln + 2:ln + 6])
#         except KeyError:
#             logger.debug('No classical stiffness matrix found.')

#         try:
#             ln = keywordsIndex['cfm']
#             bp.cmpl = sutl.textToMatrix(linesRead[ln + 2:ln + 6])
#         except KeyError:
#             logger.debug('No classical flexibility matrix found.')

#         try:
#             ln = keywordsIndex['tsm']
#             bp.stff_t = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
#         except KeyError:
#             logger.debug('No Timoshenko stiffness matrix found.')

#         try:
#             ln = keywordsIndex['tfm']
#             bp.cmpl_t = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
#         except KeyError:
#                 logger.debug('No Timoshenko flexibility matrix found.')
       

#         if 'tc' in keywordsIndex.keys():
#             ln = keywordsIndex['tc']
#             bp.xt2, bp.xt3 = list(map(float, linesRead[ln + 2].split()))
#         if 'sc' in keywordsIndex.keys():
#             ln = keywordsIndex['sc']
#             bp.xs2, bp.xs3 = list(map(float, linesRead[ln + 2].split()))
#         if 'mc' in keywordsIndex.keys():
#             ln = keywordsIndex['mc']
#             bp.xm2, bp.xm3 = list(map(float, linesRead[ln + 2].split()))


#     return bp




def _readOutputShellModel(file, model):
    """
    """

    if model == 'PL1' or model == 1:
        return _readKirchhoffLovePlateShellModel(file)



def _readKirchhoffLovePlateShellModel(file):
    """
    """

    model = smdl.KirchhoffLovePlateShellModel()

    block = ''
    line = file.readline()

    while True:
        if not line:  # EOF
            break

        line = line.strip()

        if '-----' in line or len(line) == 0:
            line = file.readline()
            continue


        # Inertial properties
        # -------------------

        elif 'Effective Mass Matrix' in line:
            line = file.readline()
            _mass, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.mass = _mass

        elif 'Mass Center Location' in line:
            model.xm3 = float(line.split()[-1])

        elif 'i11' in line:
            model.i11 = float(line.split()[-1])
            model.i22 = model.i11


        # Structural properties
        # ---------------------

        elif 'Effective Stiffness Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.stff = _matrix
        elif 'Effective Compliance Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.cmpl = _matrix

        elif 'Geometric Correction to the Stiffness Matrix' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.geo_correction_stff = _matrix
        elif 'Total Stiffness Matrix after Geometric Correction' in line:
            line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float, comments=['----',]
                )
            model.stff_geo = _matrix

        elif 'In-Plane' in line:
            block = 'in_plane_prop'
        elif 'Flexural' in line:
            block = 'flexural_prop'

        elif line.startswith('E1'):
            if block == 'in_plane_prop':
                model.e1_i = float(line.split('=')[-1])
            elif block == 'flexural_prop':
                model.e1_o = float(line.split('=')[-1])
        elif line.startswith('E2'):
            if block == 'in_plane_prop':
                model.e2_i = float(line.split('=')[-1])
            elif block == 'flexural_prop':
                model.e2_o = float(line.split('=')[-1])
        elif line.startswith('G12'):
            if block == 'in_plane_prop':
                model.g12_i = float(line.split('=')[-1])
            elif block == 'flexural_prop':
                model.g12_o = float(line.split('=')[-1])
        elif line.startswith('nu12'):
            if block == 'in_plane_prop':
                model.nu12_i = float(line.split('=')[-1])
            elif block == 'flexural_prop':
                model.nu12_o = float(line.split('=')[-1])
        elif line.startswith('eta121'):
            if block == 'in_plane_prop':
                model.eta121_i = float(line.split('=')[-1])
            elif block == 'flexural_prop':
                model.eta121_o = float(line.split('=')[-1])
        elif line.startswith('eta122'):
            if block == 'in_plane_prop':
                model.eta122_i = float(line.split('=')[-1])
            elif block == 'flexural_prop':
                model.eta122_o = float(line.split('=')[-1])


        # Thermal properties
        # ---------------------

        elif 'N11T' in line:
            model.n11_t = float(line.split('=')[-1])
        elif 'N22T' in line:
            model.n22_t = float(line.split('=')[-1])
        elif 'N12T' in line:
            model.n12_t = float(line.split('=')[-1])
        elif 'M11T' in line:
            model.m11_t = float(line.split('=')[-1])
        elif 'M22T' in line:
            model.m22_t = float(line.split('=')[-1])
        elif 'M12T' in line:
            model.m12_t = float(line.split('=')[-1])

        line = file.readline()

    return model



# def _readOutputShellModel(file):

#     sp = smdl.ShellProperty()
#     # sp = smdl.MaterialSection()

#     linesRead = []
#     keywordsIndex = {}

#     # with open(fn, 'r') as fin:
#     ln = -1
#     prop_plane = None
#     for line in file:

#         line = line.strip()

#         if len(line) > 0:
#             linesRead.append(line)
#             ln += 1
#         else:
#             continue

#         if '-----' in line:
#             continue

#         # Inertial properties
#         # -------------------

#         elif 'Effective Mass Matrix' in line:
#             keywordsIndex['mass'] = ln
#         elif 'Mass Center Location' in line:
#             sp.xm3 = float(line.split()[-1])
#         elif 'i11' in line:
#             sp.i11 = float(line.split()[-1])
#             sp.i22 = sp.i11


#         # Structural properties
#         # ---------------------

#         elif 'Effective Stiffness Matrix' in line:
#             keywordsIndex['stff'] = ln
#         elif 'Effective Compliance Matrix' in line:
#             keywordsIndex['cmpl'] = ln

#         elif 'Geometric Correction to the Stiffness Matrix' in line:
#             keywordsIndex['geo_to_stff'] = ln
#         elif 'Total Stiffness Matrix after Geometric Correction' in line:
#             keywordsIndex['stff_geo'] = ln

#         elif 'In-Plane' in line:
#             prop_plane = 'in'
#         elif 'Flexural' in line:
#             prop_plane = 'out'

#         elif 'E1' in line:
#             if prop_plane == 'in':
#                 sp.e1_i = float(line.split('=')[-1])
#             elif prop_plane == 'out':
#                 sp.e1_o = float(line.split('=')[-1])
#         elif 'E2' in line:
#             if prop_plane == 'in':
#                 sp.e2_i = float(line.split('=')[-1])
#             elif prop_plane == 'out':
#                 sp.e2_o = float(line.split('=')[-1])
#         elif 'G12' in line:
#             if prop_plane == 'in':
#                 sp.g12_i = float(line.split('=')[-1])
#             elif prop_plane == 'out':
#                 sp.g12_o = float(line.split('=')[-1])
#         elif 'nu12' in line:
#             if prop_plane == 'in':
#                 sp.nu12_i = float(line.split('=')[-1])
#             elif prop_plane == 'out':
#                 sp.nu12_o = float(line.split('=')[-1])
#         elif 'eta121' in line:
#             if prop_plane == 'in':
#                 sp.eta121_i = float(line.split('=')[-1])
#             elif prop_plane == 'out':
#                 sp.eta121_o = float(line.split('=')[-1])
#         elif 'eta122' in line:
#             if prop_plane == 'in':
#                 sp.eta122_i = float(line.split('=')[-1])
#             elif prop_plane == 'out':
#                 sp.eta122_o = float(line.split('=')[-1])

#         # Thermal properties
#         # ---------------------

#         elif 'N11T' in line:
#             sp.n11_t = float(line.split('=')[-1])
#         elif 'N22T' in line:
#             sp.n22_t = float(line.split('=')[-1])
#         elif 'N12T' in line:
#             sp.n12_t = float(line.split('=')[-1])
#         elif 'M11T' in line:
#             sp.m11_t = float(line.split('=')[-1])
#         elif 'M22T' in line:
#             sp.m22_t = float(line.split('=')[-1])
#         elif 'M12T' in line:
#             sp.m12_t = float(line.split('=')[-1])

#     try:
#         ln = keywordsIndex['mass']
#         sp.mass = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
#     except KeyError:
#         logger.debug('No mass matrix found.')

#     try:
#         ln = keywordsIndex['stff']
#         sp.stff = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
#     except KeyError:
#         logger.debug('No classical stiffness matrix found.')

#     try:
#         ln = keywordsIndex['cmpl']
#         sp.cmpl = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
#     except KeyError:
#         logger.debug('No classical flexibility matrix found.')

#     try:
#         ln = keywordsIndex['geo_to_stff']
#         sp.geo_correction_stff = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
#     except KeyError:
#         logger.debug('No geometric correction matrix found.')

#     try:
#         ln = keywordsIndex['stff_geo']
#         sp.stff_geo = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
#     except KeyError:
#         logger.debug('No geometric corrected stiffness matrix found.')


#     return sp




def _readOutputCauchyContinuumModel(file):
    r"""
    """

    # mp = mmsd.MaterialProperty()
    # mp = smdl.MaterialSection()
    mp = smdl.CauchyContinuumModel()

    # Always set the homogenizated material as general anisotropic
    mp.isotropy = 2

    linesRead = []
    keywordsIndex = {}

    # with open(fn, 'r') as fin:
    ln = -1

    for line in file:

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
        mp.stff = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        logger.debug('No classical stiffness matrix found.')

    try:
        ln = keywordsIndex['cmpl']
        mp.cmpl = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        logger.debug('No classical flexibility matrix found.')

    try:
        ln = keywordsIndex['const']
        for line in linesRead[ln + 2:ln + 11]:
            line = line.strip()
            line = line.split('=')
            label = line[0].strip().lower()
            value = float(line[-1].strip())
            # mp.constants[label] = value
            mp.set(label, value)
    except KeyError:
        logger.debug('No engineering constants found.')

    line = linesRead[keywordsIndex['density']]
    line = line.strip().split('=')
    mp.set('density', float(line[-1].strip()))
    # mp.density = float(line[-1].strip())


    return mp





def _readOutputFailureIndex(file):
    r"""
    """
    # if not logger:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sg failure indices and strengh ratios...')

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




# def _readOutputFailure(fn_sc_out_fi, failure_analysis):
#     r"""
#     """
#     # if not logger:
#     #     logger = mul.initLogger(__name__)

#     logger.info('reading sc failure analysis ({}) output file: {}...'.format(failure_analysis, fn_sc_out_fi))

#     lines = []
#     kw_index = {}
#     results = []
#     with open(fn_sc_out_fi, 'r') as fin:
#         for i, line in enumerate(fin):
#             lines.append(line)
#             if failure_analysis == 'f':
#                 # initial failue strength
#                 if 'Initial Failure Strengths' in line:
#                     kw_index['Initial Failure Strengths'] = i
#             elif failure_analysis == 'fe':
#                 # initial failure envelope
#                 pass
#             elif failure_analysis == 'fi':
#                 # initial failure indices and strength ratios
#                 pass

#     if failure_analysis == 'f':
#         # initial failure strength
#         try:
#             index = kw_index['Initial Failure Strengths']
#             for line in lines[index + 2:index + 8]:
#                 line = line.strip().split()
#                 results.append(list(map(float, line[:2])))
#         except KeyError:
#             print('No initial failure strength found.')

#     elif failure_analysis == 'fe':
#         # initial failure envelope
#         for line in lines:
#             line = line.strip().split()
#             results.append([int(line[0]), float(line[1]), float(line[2])])

#     elif failure_analysis == 'fi':
#         # initial failure indices and strength ratios
#         eids = []
#         fis = []
#         srs = []
#         for line in lines:
#             line = line.strip().split()
#             # results.append([int(line[0]), float(line[1]), float(line[2])])
#             eids.append(float(line[0]))
#             fis.append(float(line[1]))
#             srs.append(float(line[2]))
#         return eids, fis, srs

#     return results









# ====================================================================
# Writers
# ====================================================================


def writeBuffer(
    sg:StructureGene, file, analysis='h',
    sfi:str='8d', sff:str='20.12e', version=None
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

    if analysis.startswith('h'):
        writeInputBuffer(sg, file, sfi, sff, version)

    elif (analysis.startswith('d')) or (analysis.startswith('l')) or (analysis.startswith('f')):
        writeInputBufferGlobal(sg, file, sfi, sff, analysis, version)

    return









def writeInputBuffer(sg, file, sfi, sff, version=None):
    """
    """

    logger.debug(f'writing sg input...')

    # print(sg)

    ssff = '{:' + sff + '}'
    # if not version is None:
    #     sg.version = sutl.Version(version)
    sg.version = version

    logger.debug('format version: {}'.format(sg.version))

    _writeHeader(sg, file, sfi, sff, version)

    _writeMesh(sg, file, sgdim=sg.sgdim, int_fmt=sfi, float_fmt=sff)

    _writeMOCombos(sg, file, sfi, sff)

    _writeMaterials(sg, file, sfi, sff)

    file.write((ssff + '\n').format(sg.omega))

    return




def writeInputBufferGlobal(sg, file, sfi, sff, analysis, version=None):
    # with open(fn, 'w') as file:
    if analysis.startswith('d') or analysis.lower().startswith('l'):
        _writeInputDisplacements(sg, file, sff)
    elif analysis.startswith('f'):
        _writeInputMaterialStrength(sg, file, sfi, sff)

    sutl.writeFormatIntegers(file, [sg.global_loads_type, ], sfi)

    if analysis != 'f':
        _writeInputLoads(sg, file, sfi, sff)









def _writeMesh(sg, file, sgdim, int_fmt, float_fmt):
    """
    """
    logger.debug('writing mesh...')

    sg.mesh.write(
        file, 'sc', sgdim=sgdim,
        int_fmt=int_fmt, float_fmt=float_fmt)

    return









def _writeMOCombos(sg, file, sfi, sff):
    ssfi = '{:' + sfi + '}'
    ssff = '{:' + sff + '}'
    count = 0
    for cid, combo in sg.mocombos.items():
        print(f'cid: {cid}, combo: {combo}')
        count += 1
        file.write((ssfi + ssfi + ssff).format(cid, combo[0], combo[1]))
        if count == 1:
            file.write('  # combination id, material id, in-plane rotation angle')
        file.write('\n')
    file.write('\n')
    return









def _writeMaterials(sg:StructureGene, file, sfi, sff):
    """
    """

    logger.debug('writing materials...')

    counter = 0
    for mid, m in sg.materials.items():

        # print('writing material {}'.format(mid))

        # print(m)

        # cm = m.constitutive

        # if m.stff:
        #     anisotropy = 2
        # else:
        anisotropy = m.get('isotropy')

        sutl.writeFormatIntegers(file, (mid, anisotropy, 1), sfi, newline=False)
        if counter == 0:  file.write('  # materials')
        file.write('\n')
        sutl.writeFormatFloats(file, (m.get('temperature'), m.get('density')), sff)

        # Write elastic properties
        if anisotropy == 0:
            sutl.writeFormatFloats(file, [m.get('e1'), m.get('nu12')], sff)

        elif anisotropy == 1:
            sutl.writeFormatFloats(file, [m.get('e1'), m.get('e2'), m.get('e3')], sff)
            sutl.writeFormatFloats(file, [m.get('g12'), m.get('g13'), m.get('g23')], sff)
            sutl.writeFormatFloats(file, [m.get('nu12'), m.get('nu13'), m.get('nu23')], sff)

        elif anisotropy == 2:
            for i in range(6):
                for j in range(i, 6):
                    sutl.writeFormatFloats(file, m.get(f'c{i+1}{j+1}'), sff, newline=False)
                file.write('\n')

        if sg.physics in [1, 4, 6]:
            sutl.writeFormatFloats(file, m.get('cte')+[m.get('specific_heat'),], sff)

        file.write('\n')
        
        counter += 1

    file.write('\n')
    return









def _writeHeader(sg:StructureGene, file, sfi, sff, version=None):
    ssfi = '{:' + sfi + '}'

    # Extra inputs for dimensionally reducible structures
    if (sg.smdim == 1) or (sg.smdim == 2):
        # model (0: classical, 1: shear refined)
        file.write(ssfi.format(sg.model))
        file.write('  # structural model (0: classical, 1: shear refined)')
        file.write('\n\n')

        if sg.smdim == 1:  # beam
            # initial twist/curvatures
            sutl.writeFormatFloats(
                file,
                [sg.initial_twist, sg.initial_curvature[0], sg.initial_curvature[1]],
                sff, newline=False
            )
            file.write('  # initial curvatures k11, k12, k13\n')
            file.write('\n')
            # oblique cross section
            sutl.writeFormatFloats(file, sg.oblique, sff)

        elif sg.smdim == 2:  # shell
            # initial twist/curvatures
            sutl.writeFormatFloats(file, sg.initial_curvature, sff, newline=False)
            file.write('  # initial curvatures k12, k21\n')
            if version > '2.1':
                sutl.writeFormatFloats(file, sg.lame_params, sff, newline=False)
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
    sutl.writeFormatIntegers(file, nums, sfi, newline=False)
    file.write(cmt)
    file.write('\n\n')

    nums = [
        sg.sgdim, sg.nnodes, sg.nelems, sg.nmates,
        sg.num_slavenodes, sg.nma_combs
    ]
    sutl.writeFormatIntegers(file, nums, sfi, newline=False)
    file.write('  # nsg, nnode, nelem, nmate, nslave, nlayer')
    file.write('\n\n')

    return









def _writeInputMaterialStrength(sg, file, sfi, sff):
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









def _writeInputDisplacements(sg, file, sff):
    sutl.writeFormatFloats(file, sg.global_displacements, sff[2:-1])
    sutl.writeFormatFloatsMatrix(file, sg.global_rotations, sff[2:-1])









def _writeInputLoads(sg, file, sfi, sff):
    for load_case in sg.global_loads:
        sutl.writeFormatFloats(file, load_case, sff)
    file.write('\n')
    return

