from __future__ import annotations

import logging

# import sgio._global as GLOBAL
import sgio.utils as sutl
import sgio.model as smdl
from sgio._exceptions import OutputFileError

logger = logging.getLogger(__name__)

def _readOutputH(file, model_type, **kwargs):
    """Read SwiftComp homogenization results.

    :param fn: SwiftComp output file (e.g. example.sg.k)
    :type fn: string

    :param smdim: Dimension of the structural model
    :type smdim: int
    """
    # print('reading homogenization output...')

    # try:
    #     model_type = kwargs['model_type']
    # except KeyError:
    #     model_type = kwargs['submodel']

    if model_type.upper().startswith('BM'):
        out = _readOutputBeamModel(file, model=model_type)

    elif model_type.upper().startswith('PL'):
        out = _readOutputShellModel(file, model=model_type)

    elif  model_type.upper().startswith('SD'):
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
    # print('reading shell model...')

    if model.upper() == 'PL1':
        return _readKirchhoffLovePlateShellModel(file)



def _readKirchhoffLovePlateShellModel(file):
    """
    """
    # print('reading Kirchhoff-Love plate shell model...')

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


    if model.mass is None:
        raise OutputFileError('No mass matrix found.')

    if model.stff is None:
        raise OutputFileError('No stiffness matrix found.')
    if model.cmpl is None:
        raise OutputFileError('No compliance matrix found.')

    if model.e1_i is None:
        raise OutputFileError('No in-plane E1 found.')
    if model.e2_i is None:
        raise OutputFileError('No in-plane E2 found.')
    if model.g12_i is None:
        raise OutputFileError('No in-plane G12 found.')
    if model.nu12_i is None:
        raise OutputFileError('No in-plane nu12 found.')
    if model.eta121_i is None:
        raise OutputFileError('No in-plane eta121 found.')
    if model.eta122_i is None:
        raise OutputFileError('No in-plane eta122 found.')

    if model.e1_o is None:
        raise OutputFileError('No flexural E1 found.')
    if model.e2_o is None:
        raise OutputFileError('No flexural E2 found.')
    if model.g12_o is None:
        raise OutputFileError('No flexural G12 found.')
    if model.nu12_o is None:
        raise OutputFileError('No flexural nu12 found.')
    if model.eta121_o is None:
        raise OutputFileError('No flexural eta121 found.')
    if model.eta122_o is None:
        raise OutputFileError('No flexural eta122 found.')


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
    # mp.isotropy = 2
    mp.set('isotropy', 2)

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
            _cte = [_a11, _a22, _a33, _2a23, _2a13, _2a12]
            mp.set('cte', _cte)

        elif 'Dthetatheta' in line:
            mp.d_thetatheta = float(line.split('=')[-1])
        elif 'Feff' in line:
            mp.f_eff = float(line.split('=')[-1])
            _t1 = 0
            _tm = 1
            _t = _t1 + _tm
            _specific_heat = mp.d_thetatheta - _t * mp.f_eff
            mp.set('specific_heat', _specific_heat)

    try:
        ln = keywordsIndex['stff']
        _stff = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
        mp.set('elastic', _stff, input_type='stiffness')
    except KeyError:
        logger.debug('No classical stiffness matrix found.')

    try:
        ln = keywordsIndex['cmpl']
        _cmpl = sutl.textToMatrix(linesRead[ln + 2:ln + 8])
        mp.set('elastic', _cmpl, input_type='compliance')
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
    """
    """

    logger.debug('reading sg failure indices and strengh ratios...')

    fi = {}
    sr = {}
    eids_sr_min = []

    _sr_min = -1
    _eid_sr_min = 0

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
            _eid = int(line[0])
            _fi = float(line[1])
            _sr = float(line[2])

            fi[_eid] = _fi
            sr[_eid] = _sr

            if _sr_min == -1 or _sr < _sr_min:
                _sr_min = _sr
                _eid_sr_min = _eid

    if len(sr) == 1 and len(eids_sr_min) == 0:
        eids_sr_min.append(1)

    if len(eids_sr_min) == 0:
        eids_sr_min.append(_eid_sr_min)

    return fi, sr, eids_sr_min




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

