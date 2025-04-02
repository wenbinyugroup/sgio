from __future__ import annotations

import sgio._global as GLOBAL
import sgio.utils as sutl
import sgio.model as smdl

import logging
logger = logging.getLogger(GLOBAL.LOGGER_NAME)




# Read homogenization output


def _readOutputH(file, model_type='BM1', **kwargs):
    """Read VABS homogenization output.
    """

    # try:
    #     model_type = kwargs['model_type'].upper()
    # except KeyError:
    #     model_type = kwargs['submodel']

    model = kwargs.get('model', None)

    if model_type.upper() == 'BM1' or model_type == 1:
        return _readEulerBernoulliBeamModel(file, model)
    elif model_type.upper() == 'BM2' or model_type == 2:
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




# Read dehomogenization output


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




def _readOutputElementStrainStressCase(file, nelem):
    """Read VABS output averaged strains and stressed on elements.

    Parameters
    ----------
    file:
        File object of the output file.
    nelem: int
        Number of elements.

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
    i = 0
    # for i, line in enumerate(file):
    while i < nelem:
        line = file.readline().strip()
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

        i += 1

    return e, s, em, sm




# Read failure analysis output


def _readOutputFailureIndexCase(file, nelem):
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

    i = 0
    # for i, line in enumerate(file):
    while i <= nelem:
        line = file.readline().strip()
        if line == '':
            continue
        # if line.startswith('Failure index'):
        #     continue

        # Read the initial failure indices and strength ratios
        if i < nelem:
            line = line.split()
            if len(line) == 3:
                # lines.append(line)
                fi[int(line[0])] = float(line[1])
                sr[int(line[0])] = float(line[2])

        # Read the last line of sectional strength ratio
        # if (line.startswith('The sectional strength ratio is')):
        elif i == nelem:
            # line = file.readline().strip()
            line = line.split()
            # _loc = line.index('existing')
            # _sr_min = float(line[tmp_id - 1])
            try:
                _eid = int(line[-1])
            except ValueError:
                line = file.readline().split()
                _eid = int(line[0])

            eids_sr_min.append(_eid)
            # lines.pop()
            # continue

        i += 1

    # result = []
    # # fis = []
    # # srs = []
    # for line in lines:
    #     # line = line.strip().split()
    #     result.append([int(line[0]), float(line[1]), float(line[2])])
    #     # fis.append(float(line[1]))
    #     # srs.append(float(line[2]))

    return fi, sr, eids_sr_min


